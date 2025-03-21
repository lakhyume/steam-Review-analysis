from utils.query import querys
import json


def getAllGames():
    gameList = querys('select * from games', [], 'select')

    def map_fn(item):
        item = list(item)

        # 检查 item[4], item[7], item[8], item[9], item[15] 是否为 None 或空字符串
        if item[4] is None or item[7] is None or item[7] == '' or item[8] is None or item[9] is None or item[15] is None:
            return None

        item[4] = json.loads(item[4])
        item[9] = json.loads(item[9])
        item[15] = json.loads(item[15])
        item[8] = round(float(item[8]), 1)
        return item

    # print(gameList)

    # # 使用 for 循环过滤掉 None 条目
    # gameLists = []
    # for item in gameList:
    #     if item is not None:
    #         gameList.append(item)

    # 使用 map 函数对 gameList 进行处理，并使用 filter 函数过滤掉 None 条目
    gameList = list(filter(None, map(map_fn, gameList)))

    return gameList


def getAllUser():
    gameList = querys('select * from user', [], 'select')
    # print(gameList)
    return gameList


def getHeadData():
    maxUserLen = len(getAllUser())
    maxGames = len(getAllGames())
    gamesList = getAllGames()

    minDiscountTitle = ''
    minDiscount = 100
    typeDic = {}

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

    # 对类型出现的次数进行排序
    typeSort = list(sorted(typeDic.items(), key=lambda x: x[1], reverse=True))

    return typeSort[0][0], minDiscountTitle, maxUserLen, maxGames


if __name__ == '__main__':
    # getAllGames()
    getAllUser()
