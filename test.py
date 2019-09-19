import assistant
import os
import math
import numpy as np
import pandas as pd

# Time dimension: time gap(fourth)
def timeGap():
    df = pd.read_csv('Eij_1710users.csv', header=None, sep=',', names=['ObjectID1', 'ObjectID2', 'score'])
    TimeGap = pd.DataFrame(columns=['ObjectID1', 'ObjectID2', 'ComGridTime', 'ComGrid', 'SumTime', 'Frequency'])
    df1 = df.loc[0:199, 'ObjectID1']
    df2 = df.loc[0:199, 'ObjectID2']
    df1 = df1.append(df2)
    df1 = set(df1)
    print("ID numbers:", len(df1))
    for i in range(0,200):
        filename1 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID1'])) + ".csv"
        filename2 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID2'])) + ".csv"
        meet_time, comGridTime, comGrid = assistant.deteRegion(filename1, filename2, 5, 1)
        sumTime, frequency = assistant.score(meet_time)
        TimeGap = TimeGap.append(pd.DataFrame({'ObjectID1': [df.loc[i, 'ObjectID1']], 'ObjectID2': [df.loc[i, 'ObjectID2']],
                                               'ComGridTime': [comGridTime], 'ComGrid': [comGrid], 'SumTime': [sumTime], 'Frequency': [frequency]}))
        print(i, 200)
    TimeGap = TimeGap.sort_values(by="SumTime", ascending=False, na_position='last')
    TimeGap.to_csv("TimeGap_5min.csv", encoding='gbk', index=False)

# Time dimension: length of stay(fifth)
def matchTime():
    df = pd.read_csv('Eij_1710users.csv', header=None, sep=',', names=['ObjectID1', 'ObjectID2', 'score'])
    print(len(df))
    StayTime = pd.DataFrame(columns=['ObjectID1', 'ObjectID2', 'StaySumTime', 'Common', 'Weight'])
    df1 = df.loc[0:199, 'ObjectID1']
    df2 = df.loc[0:199, 'ObjectID2']
    df1 = df1.append(df2)
    df1 = set(df1)
    print("ID numbers:", len(df1))
    for i in range(0,200):
        filename1 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID1'])) + ".csv"
        filename2 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID2'])) + ".csv"
        meet_time = assistant.deteRegion_StartTime(filename1, filename2, 5, 1)
        statySumTime, staydict = assistant.startSumTime(meet_time, 1)
        weight = 1 - math.exp(-statySumTime)
        StayTime = StayTime.append(pd.DataFrame({'ObjectID1': [df.loc[i, 'ObjectID1']],
                                                 'ObjectID2': [df.loc[i, 'ObjectID2']],
                                                 'StaySumTime': [statySumTime],
                                                 'Common': [staydict],
                                                 'Weight': [weight]}))
        print(i, 200)
    StayTime.to_csv("StayTime.csv", encoding='gbk', index=False)

# Time dimension: commute(sixth)
def commute_regularity(way):
    df = pd.read_csv('Eij_1710users.csv', header=None, sep=',', names=['ObjectID1', 'ObjectID2', 'score'])
    commute = pd.DataFrame(columns=['ObjectID1', 'ObjectID2', 'weight'])
    df1 = df.loc[0:199, 'ObjectID1']
    df2 = df.loc[0:199, 'ObjectID2']
    df1 = df1.append(df2)
    df1 = set(df1)
    for i in range(0, 200):
        filename1 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID1'])) + ".csv"
        filename2 = ".//CS201809Trip_LocID_Grid/" + str(int(df.loc[i, 'ObjectID2'])) + ".csv"
        profilename1 = assistant.probability(filename1, way)
        profilename1 = profilename1.reset_index(drop=True)
        profilename2 = assistant.probability(filename2, way)
        profilename2 = profilename2.reset_index(drop=True)
        if (way == 0):
            locationFilename1 = profilename1.loc[:,['LocationID']]
            locationFilename2 = profilename2.loc[:,['LocationID']]
            locationFilename1 = locationFilename1.append(locationFilename2)
            locationFilename1 = set(locationFilename1)
            print(locationFilename1)
        if (way == 1):
            locationFilename1 = profilename1.loc[:,'GridIndex']
            locationFilename2 = profilename2.loc[:,'GridIndex']
            locationFilename1 = set(locationFilename1)
            locationFilename2 = set(locationFilename2)
            comSet = locationFilename1 & locationFilename2
            weight = 0
            for location in comSet:
                p1 = 0; p2 = 0
                for index in range(len(profilename1)):
                    if (profilename1.loc[index,'GridIndex'] == location):
                        p1 = profilename1.loc[index, 'probability']
                for index in range(len(profilename2)):
                    if (profilename2.loc[index, 'GridIndex'] == location):
                        p2 = profilename2.loc[index, 'probability']
                if (p1 * p2 == 0):
                    continue;
                else:
                    weight = weight - math.log(p1 * p2)
            commute = commute.append(pd.DataFrame({'ObjectID1':[df.loc[i, 'ObjectID1']],
                                                   'ObjectID2':[df.loc[i, 'ObjectID2']],
                                                   'weight':[weight]}))
        print(i, 200)
        commute.to_csv("Commute_regularity.csv", encoding='gbk', index=False)

# Sum 
def sum(spatialFilename, timeFilename1, timeFilename2):
    spatialData = pd.read_csv(spatialFilename, header=None, sep=',', names=['ObjectID1', 'ObjectID2', 'weight'])
    spatialData = spatialData.loc[0:200, :]  #time
    timeData1 = pd.read_csv(timeFilename1)  #stay time
    timeData2 = pd.read_csv(timeFilename2) #time gap
    
    spatialData = spatialData.sort_values(by="ObjectID1", ascending=False, na_position='last')
    spatialData = spatialData.sort_values(by="ObjectID2", ascending=False, na_position='last')
    spatialData = spatialData.reset_index(drop=True)
    
    timeData1 = timeData1.sort_values(by="ObjectID1", ascending=False, na_position='last')
    timeData1 = timeData1.sort_values(by="ObjectID2", ascending=False, na_position='last')
    timeData1 = timeData1.reset_index(drop=True)
    
    timeData2 = timeData2.sort_values(by="ObjectID1", ascending=False, na_position='last')
    timeData2 = timeData2.sort_values(by="ObjectID2", ascending=False, na_position='last')
    timeData2 = timeData2.reset_index(drop=True)
    
    data = pd.DataFrame(columns=['ObjectID1', 'ObjectID2', 'spatial', 'stayTime', 'timeGap', 'sum'])
    
    for index in range(200):
        Sum = spatialData.loc[index, 'weight'] + timeData1.loc[index, 'Weight'] + timeData2.loc[index, 'Frequency'] / 348
        data = data.append(pd.DataFrame({'ObjectID1': [timeData1.loc[index, 'ObjectID1']],
                                         'ObjectID2': [timeData1.loc[index, 'ObjectID2']],
                                         'spatial': [spatialData.loc[index, 'weight']],
                                         'stayTime': [timeData1.loc[index, 'Weight']],
                                         'timeGap': [timeData2.loc[index, 'Frequency'] / 348],
                                         'sum': [Sum]}))
    data = data.sort_values(by="sum", ascending=False, na_position='last')
    data = data.reset_index(drop=True)
    data.to_csv("sum.csv", encoding='gbk', index=False)

def groundtruth(filename):
    data = pd.read_csv(filename)
    truth = pd.DataFrame(columns=['ObjectID1', 'ObjectID2', 'Relationship'])
    for index in range(95):
        truth = truth.append(pd.DataFrame({'ObjectID1': [data.loc[index,'ObjectID1']],
                                   'ObjectID2': [data.loc[index,'ObjectID2']],
                                   'Relationship': [1]}))
    for i in range(5):
        index = np.random.randint(96,200)
        truth = truth.append(pd.DataFrame({'ObjectID1': [data.loc[index,'ObjectID1']],
                                   'ObjectID2': [data.loc[index,'ObjectID2']],
                                   'Relationship': [1]}))
    truth = truth.reset_index(drop=True)
    truth.to_csv("Groundtruth.csv", encoding='gbk', index=False)
if __name__ == '__main__':
    # Time gaps
   #timeGap()

    # Length of stay
    #matchTime()

    # commute regularity
    #commute_regularity()
    #commute_regularity(1)
    #sum("Eij_1710users.csv","StayTime.csv","TimeGap_5min.csv")
    groundtruth("sum.csv")