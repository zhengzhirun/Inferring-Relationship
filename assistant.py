import pandas as pd
import math

# 观测不同ID是否在同一个地点出现过
def deteRegion(filename1, filename2, eps, way):
    """
    :param filename1: 待比较的ID所在的文件名
    :param filename2: 待比较的ID所在的文件名
    :param eps: 容许的时间误差（在相差eps时间内出现在同一个地点都算同时出现）
    :param way: 采用哪一种编码方式
    :return: 返回相遇的frameData数据
    """
    df1 = pd.read_csv(filename1, header=None, sep=',',
                      names=['ObjectID', 'StartTime', 'StartLat', 'StartLng', 'StopTime', 'StopLat', 'StopLng', 'LocationID', 'GridIndex'])
    df2 = pd.read_csv(filename2, header=None, sep=',',
                      names=['ObjectID', 'StartTime', 'StartLat', 'StartLng', 'StopTime', 'StopLat', 'StopLng', 'LocationID', 'GridIndex'])
    len_df1 = len(df1)
    len_df2 = len(df2)
    meet_time = pd.DataFrame(columns=['ObjectID', 'AverageTime', 'LocationID', 'GridIndex'])  # 在同一个地点相遇的时间间隔
    commonGrid = set()
    if (way == 0):
        # 使用LocationID判断
        data1 = df1[['ObjectID', 'StopTime', 'LocationID']]
        data2 = df2[['ObjectID', 'StopTime', 'LocationID']]
        df1Location = set(df1['LocationID'])
        df2Location = set(df2['LocationID'])
        for index_x in range(len_df1):
            index = 0
            if (index > len_df2):   break
            for index_y in range(index, len_df2):
                time = pd.to_datetime(data1.loc[index_x, 'StopTime']) - pd.to_datetime(data2.loc[index_y, 'StopTime'])
                timeDiff = time.total_seconds() / 3600
                if (data1.loc[index_x, 'LocationID'] == data2.loc[index_y, 'LocationID'] and abs(timeDiff) <= eps):
                    aveTime = pd.to_datetime(data2.loc[index_y, 'StopTime']) + time
                    meet_time = meet_time.append(pd.DataFrame({'ObjectID':[str(data1.loc[index_x, 'ObjectID']) + "&" + str(data2.loc[index_y, 'ObjectID'])],
                                                               'AverageTime':[aveTime], 'LocationID':[data1.loc[index_x, 'LocationID']],
                                                               'GridIndex':[df1.loc[index_x, 'GridIndex']]}), ignore_index=True)
                    commonGrid.add(str(data1.loc[index_y, 'LocationID']))
                    index = index_y + 1
                    break
    if (way == 1):
        # 使用GridIndex判断
        data1 = df1[['ObjectID', 'StopTime', 'GridIndex']]
        data2 = df2[['ObjectID', 'StopTime', 'GridIndex']]
        df1Location = set(df1['GridIndex'])
        df2Location = set(df2['GridIndex'])
        for index_x in range(len_df1):
            index = 0
            if (index > len_df2):   break
            for index_y in range(index, len_df2):
                time =  pd.to_datetime(data1.loc[index_x, 'StopTime']) - pd.to_datetime(data2.loc[index_y, 'StopTime'])
                timeDiff = time.total_seconds() / 3600
                if (data1.loc[index_x, 'GridIndex'] == data2.loc[index_y, 'GridIndex'] and abs(timeDiff) <= eps):
                    aveTime = pd.to_datetime(data2.loc[index_y, 'StopTime']) + time
                    meet_time = meet_time.append(pd.DataFrame({'ObjectID': [str(data1.loc[index_x, 'ObjectID']) + "&" + str(data2.loc[index_y, 'ObjectID'])],
                                                               'AverageTime': [aveTime], 'LocationID': [df1.loc[index_x, 'LocationID']],
                                                               'GridIndex': [data1.loc[index_x, 'GridIndex']]}), ignore_index=True)
                    commonGrid.add(str(data1.loc[index_x, 'GridIndex']))
                    index = index_y + 1
                    break

    return meet_time, len(commonGrid), len(df1Location & df2Location)

# 根据相遇的时间数据观测两个ID之间的亲密度
def score(meet_time):
    """
    :param meet_time: 相遇的时间戳
    :return: 相遇的时间间隔总和， 相遇的总次数
    """
    if (meet_time.empty):
        return 0, 0
    sumTime = 0
    for i in range(1, len(meet_time)):
        timeDiff = pd.to_datetime(meet_time.loc[i, 'AverageTime']) - pd.to_datetime(meet_time.loc[i-1, 'AverageTime'])
        timeDiff = abs(timeDiff.total_seconds() /  3600)
        sumTime += 1 - math.exp(-timeDiff)
    return sumTime, len(meet_time)

# 计算匹配对，相遇的时间长度（待在一起的时间长度）
def deteRegion_StartTime(filename1, filename2, eps, way):
    """
    :param filename1: 待比较的ID所在的文件名
    :param filename2: 待比较的ID所在的文件名
    :param eps: 容许的时间误差（在相差eps时间内出现在同一个地点都算同时出现）
    :param way: 采用哪一种编码方式
    :return: 返回相遇的frameData数据
    """
    df1 = pd.read_csv(filename1, header=None, sep=',',
                      names=['ObjectID', 'StartTime', 'StartLat', 'StartLng', 'StopTime', 'StopLat', 'StopLng', 'LocationID', 'GridIndex'])
    df2 = pd.read_csv(filename2, header=None, sep=',',
                      names=['ObjectID', 'StartTime', 'StartLat', 'StartLng', 'StopTime', 'StopLat', 'StopLng', 'LocationID', 'GridIndex'])
    len_df1 = len(df1)
    len_df2 = len(df2)
    meet_time = pd.DataFrame(columns=['ObjectID', 'StartTime', 'AverageEndTime', 'LocationID', 'GridIndex'])  # 在同一个地点相遇的时间间隔
    if (way == 0):
        # 使用LocationID判断
        data1 = df1[['ObjectID', 'StartTime', 'StopTime', 'LocationID']]
        data2 = df2[['ObjectID', 'StartTime', 'StopTime', 'LocationID']]
        for index_x in range(len_df1):
            index = 0
            if (index > len_df2):   break
            for index_y in range(index, len_df2):
                time = pd.to_datetime(data1.loc[index_x, 'StopTime']) - pd.to_datetime(data2.loc[index_y, 'StopTime'])
                timeDiff = time.total_seconds() / 3600
                if (data1.loc[index_x, 'LocationID'] == data2.loc[index_y, 'LocationID'] and abs(timeDiff) <= eps):
                    startTime0 = pd.to_datetime(data1.loc[index_x, 'StartTime'])
                    startTime1 = pd.to_datetime(data2.loc[index_y, 'StartTime'])
                    startTime = min(startTime0, startTime1)
                    aveTime = pd.to_datetime(data2.loc[index_y, 'StopTime']) + time
                    meet_time = meet_time.append(pd.DataFrame({'ObjectID':[str(data1.loc[index_x, 'ObjectID']) + "&" + str(data2.loc[index_y, 'ObjectID'])],
                                                               'StartTime':[startTime],
                                                               'AverageEndTime':[aveTime], 'LocationID':[data1.loc[index_x, 'LocationID']],
                                                               'GridIndex':[df1.loc[index_x, 'GridIndex']]}), ignore_index=True)
                    index = index_y + 1
                    break
    if (way == 1):
        # 使用GridIndex判断
        data1 = df1[['ObjectID', 'StartTime', 'StopTime', 'GridIndex']]
        data2 = df2[['ObjectID', 'StartTime', 'StopTime', 'GridIndex']]
        df1Location = set(df1['GridIndex'])
        df2Location = set(df2['GridIndex'])
        for index_x in range(len_df1):
            index = 0
            if (index > len_df2):   break
            for index_y in range(index, len_df2):
                time =  pd.to_datetime(data1.loc[index_x, 'StopTime']) - pd.to_datetime(data2.loc[index_y, 'StopTime'])
                timeDiff = time.total_seconds() / 3600
                if (data1.loc[index_x, 'GridIndex'] == data2.loc[index_y, 'GridIndex'] and abs(timeDiff) <= eps):
                    startTime0 = pd.to_datetime(data1.loc[index_x, 'StartTime'])
                    startTime1 = pd.to_datetime(data2.loc[index_y, 'StartTime'])
                    startTime = min(startTime0, startTime1)
                    aveTime = pd.to_datetime(data2.loc[index_y, 'StopTime']) + time
                    meet_time = meet_time.append(pd.DataFrame({'ObjectID': [str(data1.loc[index_x, 'ObjectID']) + "&" + str(data2.loc[index_y, 'ObjectID'])],
                                                               'StartTime':[startTime],
                                                               'AverageEndTime': [aveTime], 'LocationID': [df1.loc[index_x, 'LocationID']],
                                                               'GridIndex': [data1.loc[index_x, 'GridIndex']]}), ignore_index=True)
                    index = index_y + 1
                    break
    return meet_time

# 计算相遇以后待的时间长度的总和
def startSumTime(meet_time, way):
    if (meet_time.empty):
        return 0,{}
    stay_dict = {}
    staySumTime = 0
    for index in range(1, len(meet_time)):
        stayTime = pd.to_datetime(meet_time.loc[index, 'StartTime']) - pd.to_datetime(meet_time.loc[index - 1, 'AverageEndTime'])
        stayTime = abs(stayTime.total_seconds() / 3600)
        if (way == 0):
            if (str(meet_time.loc[index, 'LocationID']) in stay_dict.keys()):
                stay_dict[str(meet_time.loc[index, 'LocationID'])] += stayTime
            else:
                stay_dict[str(meet_time.loc[index, 'LocationID'])] = stayTime
        if (way == 1):
            if (str(meet_time.loc[index, 'GridIndex']) in stay_dict.keys()):
                stay_dict[str(meet_time.loc[index, 'GridIndex'])] += stayTime
            else:
                stay_dict[str(meet_time.loc[index, 'GridIndex'])] = stayTime
        staySumTime += stayTime
    return staySumTime, stay_dict

# 计算common grids节假日和非假日的占比
def commute(meet_time):
    if (meet_time.empty):
        return 0, 0
    holiday_number = 0
    work_number = 0
    total_number = 0
    holiday = {1, 2, 8, 9, 15, 16, 22, 23, 24}
    for index in range(len(meet_time)):
        if (pd.to_datetime(meet_time.loc[index, 'AverageEndTime']).day in holiday):
            holiday_number += 1
            total_number += 1
        else:
            work_number += 1
            total_number += 1
    return work_number/total_number, holiday_number/total_number

# 用户i 去地点l的所有记录里，时间是周末的概率
def probability(useFilename, way):
    data = pd.read_csv(useFilename, header=None, sep=',',
                      names=['ObjectID', 'StartTime', 'StartLat', 'StartLng', 'StopTime', 'StopLat', 'StopLng', 'LocationID', 'GridIndex'])
    proLocationID = pd.DataFrame(columns=['ObjectID', 'LocationID', 'probability'])
    proGridIndex = pd.DataFrame(columns=['ObjectID', 'GridIndex', 'probability'])
    holiday = {1, 2, 8, 9, 15, 16, 22, 23, 24}
    if (way == 0):
        # sort for LocationID
        data = data.sort_values(by="LocationID", ascending=False, na_position='last')
        data = data.reset_index(drop=True)
        # fast and slow pointer
        slow = 0; fast = 0
        numbersWeekends = 0; numbers = 0
        print(len(data))
        print(data)
        while (slow < len(data) and fast < len(data)): 
            if (data.loc[fast,'LocationID'] == data.loc[slow, 'LocationID']):
                if (pd.to_datetime(data.loc[slow, 'StopTime']).day in holiday):
                    numbersWeekends += 1
                fast += 1
            else:
                numbers = fast - slow
                probability = numbersWeekends / numbers
                numbersWeekends = 0; numbers = 0
                proLocationID = proLocationID.append(pd.DataFrame({'ObjectID': [data.loc[slow, 'ObjectID']],
                                                                   'LocationID': [data.loc[slow, 'LocationID']],
                                                                   'probability': [probability]}))
                slow = fast
        return proLocationID
    if (way == 1):
        # sort for GridIndex
        data = data.sort_values(by='GridIndex', ascending=False, na_position='last')
        data = data.reset_index(drop=True)
        # fast and slow pointer
        slow = 0; fast = 0
        numbersWeekends = 0; numbers = 0
        while (slow < len(data) and fast < len(data)):
            if (data.loc[fast,'GridIndex'] == data.loc[slow, 'GridIndex']):
                if (pd.to_datetime(data.loc[slow, 'StopTime']).day in holiday):
                    numbersWeekends += 1
                fast += 1
            else:
                numbers = fast - slow
                probability = numbersWeekends / numbers
                numbersWeekends = 0; numbers = 0
                proGridIndex = proGridIndex.append(pd.DataFrame({'ObjectID': [data.loc[slow, 'ObjectID']],
                                                                   'GridIndex': [data.loc[slow, 'GridIndex']],
                                                                   'probability': [probability]}))
                slow = fast
        return proGridIndex
        
            
        
        