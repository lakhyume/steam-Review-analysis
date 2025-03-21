from utils.getPublicData import *
from utils.query import querys
from datetime import datetime


def getHomeData():
    maxUserLen = len(getAllUser())
    maxGames = len(getAllGames())

    gamesList = getAllGames()
    allUserList = getAllUser()

    minDiscountTitle = ''
    minDiscount = 100
    typeDic = {}
    timeDic = {}

    for i in gamesList:
        if int(i[6]) < minDiscount:
            minDiscount = int(i[6])
            minDiscountTitle = i[1]

        # 统计游戏类型出现的次数
        for j in i[9]:
            if typeDic.get(j, -1) == -1:
                typeDic[j] = 1
            else:
                typeDic[j] += 1

        # 上线时间个数
        if timeDic.get(i[3], -1) == -1:
            timeDic[i[3]] = 1
        else:
            timeDic[i[3]] += 1

    # 对类型出现的次数进行排序
    typeSort = list(sorted(typeDic.items(), key=lambda x: x[1], reverse=True))

    # 时间
    timeSort = list(sorted(timeDic.items(), key=lambda data: data[1], reverse=True))

    # print(timeSort)
    # print(maxUserLen, maxGames, minDiscountTitle, typeSort)

    # 上线时间排序  升序
    def get_timestamp(date):
        try:
            datetime.strptime(date, "%Y 年 %m 月 %d 日").timestamp()
            return datetime.strptime(date, "%Y 年 %m 月 %d 日").timestamp()
        except:
            return 0

    gamesTimeSort = sorted(gamesList, key=lambda date: get_timestamp(date[3]), reverse=True)
    # print(gamesTimeSort)

    xData = []
    yData = []
    for i in timeSort:
        xData.append(i[0])
        yData.append(i[1])

    # 表格
    gamesListData = list(gamesList)

    userDic = {}
    for i in allUserList:
        if userDic.get(str(i[3])[:10], -1) == -1:
            userDic[str(i[3])[:10]] = 1
        else:
            userDic[str(i[3])[:10]] += 1

    userData = []
    for key, value in userDic.items():
        userData.append({
            'name': key,
            'value': value,
        })
    # print(userData)

    typeData = []
    for i in typeSort:
        typeData.append({
            'name': i[0],
            'value': i[1],
        })
    # print(typeData)

    return typeSort[0][0], minDiscountTitle, maxUserLen, maxGames, xData[:10], yData[:10], gamesTimeSort[
                                                                                           :10], gamesListData, userData, typeData[
                                                                                                                          :10]


def getPriceCharData(year):
    gameList = getAllGames()
    x1Data = ['0-100元', '100-200元', '200-300元', '300-500元', '500-600元', '600及以上']
    y1Data = [0 for x in range(len(x1Data))]
    x2Data = ['0-10元', '10-50元', '50-100元', '100-150元', '150-200元', '200及以上']
    y2Data = [0 for x in range(len(x2Data))]

    for i in gameList:
        if i[3][:4] == year:
            if int(i[7]) < 100:
                y1Data[0] += 1
            elif int(i[7]) < 200:
                y1Data[1] += 1
            elif int(i[7]) < 300:
                y1Data[2] += 1
            elif int(i[7]) < 500:
                y1Data[3] += 1
            elif int(i[7]) < 600:
                y1Data[4] += 1
            else:
                y1Data[5] += 1
        if i[3][:4] == year:
            if int(i[8]) < 10:
                y2Data[0] += 1
            elif int(i[8]) < 50:
                y2Data[1] += 1
            elif int(i[8]) < 100:
                y2Data[2] += 1
            elif int(i[8]) < 150:
                y2Data[3] += 1
            elif int(i[8]) < 200:
                y2Data[4] += 1
            else:
                y2Data[5] += 1
    return x1Data, y1Data, x2Data, y2Data


def getTypeList():
    typeDic = {}
    gamesList = getAllGames()
    for i in gamesList:
        for j in i[9]:
            if j not in typeDic:
                typeDic[j] = 1
            else:
                typeDic[j] += 1
    typeSort = sorted(typeDic.items(), key=lambda x: x[1], reverse=True)
    # print(typeSort)
    x2Data = []
    y2Data = []
    for i in typeSort:
        x2Data.append(i[0])
        y2Data.append(i[1])
    return [x[0] for x in typeSort][:20], x2Data[:20], y2Data[:20]


def getTypeChar(defaultType):
    typeDic = {}
    gamesList = getAllGames()
    x1Data = []
    for i in gamesList:
        flag = False
        for j in i[9]:
            if j == defaultType:
                flag = True
            if j not in typeDic:
                typeDic[j] = 1
            else:
                typeDic[j] += 1
        if flag:
            x1Data.append(int(i[6]) / 10)  # 确保i[6]是整数类型

    x1Data = list(set(x1Data))
    y1Data = [0 for x in range(len(x1Data))]  # 初始化一个与x1Data长度相同的列表，初始值都为0

    for i in gamesList:
        flag = False
        for j in i[9]:
            if j == defaultType:
                flag = True
        if flag:
            for index, x in enumerate(x1Data):
                if x == (int(i[6]) / 10):
                    y1Data[index] += 1

    # print(x1Data, y1Data)
    return x1Data, y1Data


def getRateCharData():
    gameList = getAllGames()

    rateOne = {}
    for i in gameList:
        if rateOne.get(i[11], -1) == -1:
            rateOne[i[11]] = 1
        else:
            rateOne[i[11]] += 1
    # print(rateData)

    rateData1 = []
    for key, value in rateOne.items():
        rateData1.append({
            'name': key,
            'value': value,
        })

    rateTwoData = {}
    for i in gameList:
        if rateTwoData.get(i[12], -1) == -1:
            rateTwoData[i[12]] = 1
        else:
            rateTwoData[i[12]] += 1
    # print(rateData2)

    rateData2 = []
    for key, value in rateTwoData.items():
        rateData2.append({
            'name': key,
            'value': value,
        })

    # print(rateData1)
    return rateData1, rateData2


def getFirmCharData():
    gameList = getAllGames()

    dataOne = {}
    dataTwo = {}
    for i in gameList:
        if dataOne.get(i[13], -1) == -1:
            dataOne[i[13]] = 1
        else:
            dataOne[i[13]] += 1

        if dataTwo.get(i[14], -1) == -1:
            dataTwo[i[14]] = 1
        else:
            dataTwo[i[14]] += 1

    # print(list(rateOne.keys()))
    # print(list(rateOne.values()))

    return list(dataOne.keys()), list(dataOne.values()), list(dataTwo.keys()), list(dataTwo.values())


def getAnotherCharData():
    gameList = getAllGames()

    data = {}
    for i in gameList:
        for j in i[4]:
            if data.get(j, -1) == -1:
                data[j] = 1
            else:
                data[j] += 1
    # print(data)

    anotherdata = []
    for key, value in data.items():
        anotherdata.append({
            'name': key,
            'value': value
        })
    return anotherdata
