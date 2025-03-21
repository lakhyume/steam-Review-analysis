from flask import Flask, request, render_template, session, redirect
import time
from utils.query import querys
from utils.getPublicData import *
from utils.getPageData import *
from utils.getHistoryData import *
from recommendation.machine import *
import random

# 编码
import sys
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdout = sys.stderr


@app.route('/')
def hello_world():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(dict(request.form))
        username = request.form.get('username')
        password = request.form.get('password')
        users = querys('select * from user where username = %s and password = %s', [username, password], 'select')
        # print(users)
        if users:
            session['username'] = username
            return redirect('/home')
        else:
            return "用户名或密码错误！"
    return render_template('pages-login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # print(dict(request.form))
        username = request.form.get('username')
        password = request.form.get('password')
        passwordChecked = request.form.get('passwordChecked')

        users = querys('select * from user where username = %s', [username], 'select')
        if users:
            return "账号已存在！"

        if passwordChecked == password:
            querys('insert into user(username,password) values (%s,%s)', [username, passwordChecked])
            return redirect('/login')
        else:
            return "两次密码不一致！"

    return render_template('pages-register.html')


# 退出登陆
@app.route('/loginout')
def loginout():
    session.clear()
    return redirect('/login')


# 首页
@app.route('/home')
def home():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames, xData, yData, gamesTimeSort, gamesListData, userData, typeData = getHomeData()
    return render_template(
        'index.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        xData=xData,
        yData=yData,
        gamesTimeSort=gamesTimeSort,
        gamesListData=gamesListData,
        userData=userData,
        typeData=typeData
    )


# 数据表格
@app.route('/tableData')
def tableData():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    categoryList = getAllGames()
    return render_template(
        'tableData.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        categoryList=categoryList
    )


# 购买游戏
@app.route('/addHistory/<int:gameId>', methods=['GET', 'POST'])
def addHistory(gameId):
    username = session['username']
    userId = querys('SELECT id FROM user WHERE username = %s', [username], 'select')[0][0]
    gameID = querys('SELECT id FROM games WHERE id = %s', [gameId], 'select')[0][0]
    gameurl = querys('select detailLink from games where id = %s', [gameId], 'select')[0][0]
    # print(userId, gameID)
    getData(userId, gameID)
    # 重定向到游戏详细链接
    return redirect(gameurl)


# 游戏搜索
@app.route('/search', methods=['GET', 'POST'])
def search():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    if request.method == 'POST':
        searchWord = request.form.get('searchIpt')
        print(searchWord)

        # 方法一 使用 LIKE 操作符进行模糊查询
        # searchData = list(querys('select * from games where title LIKE %s', ['%' + searchWord + '%'], 'select'))
        # def map_fn(item):
        #     item = list(item)
        #     item[15] = json.loads(item[15])
        #     return item
        # searchData = list(map(map_fn, searchData))

        # 方法二 filter
        def filter_fn(item):
            if item[1].find(searchWord) == -1:
                return False
            else:
                return True

        searchData = list(filter(filter_fn, getAllGames()))
        print(searchData)

        return render_template(
            'search.html',
            username=username,
            typeSort=typeSort,
            minDiscountTitle=minDiscountTitle,
            maxUserLen=maxUserLen,
            maxGames=maxGames,
            searchData=searchData
        )

    return render_template(
        'search.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
    )


# 价格分析
@app.route('/priceChar', methods=['GET', 'POST'])
def priceChar():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()

    yearList = ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016']
    defaultYear = yearList[0]

    if request.method == 'POST':
        year = request.form.get('year')
        # print(year)
        defaultYear = year

    x1Data, y1Data, x2Data, y2Data = getPriceCharData(defaultYear)
    resData = []
    for index, x in enumerate(x2Data):
        resData.append([x, y2Data[index]])
    # print(resData)

    return render_template(
        'priceChar.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        yearList=yearList,
        defaultYear=defaultYear,
        x1Data=x1Data,
        y1Data=y1Data,
        resData=resData
    )


# 类型分析
@app.route('/typeChar', methods=['GET', 'POST'])
def typeChar():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    typeList, x2Data, y2Data = getTypeList()
    defaultType = typeList[0]
    if request.args.get('type'):
        defaultType = request.args.get('type')
        # print(defaultType)
    x1Data, y1Data = getTypeChar(defaultType)

    return render_template(
        'typeChar.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        typeList=typeList,
        defaultType=defaultType,
        x1Data=x1Data,
        y1Data=y1Data,
        x2Data=x2Data,
        y2Data=y2Data
    )


# 评测分析
@app.route('/rateChar', methods=['GET', 'POST'])
def rateChar():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    rateData1, rateData2 = getRateCharData()
    return render_template(
        'rateChar.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        rateData1=rateData1,
        rateData2=rateData2
    )


# 数据分析
@app.route('/firmChar', methods=['GET', 'POST'])
def firmChar():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    x1Data, y1Data, x2Data, y2Data = getFirmCharData()
    return render_template(
        'firmChar.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        x1Data=x1Data,
        y1Data=y1Data,
        x2Data=x2Data,
        y2Data=y2Data
    )


# 操作系统分析
@app.route('/anotherChar', methods=['GET', 'POST'])
def anotherChar():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    anotherdata = getAnotherCharData()
    return render_template(
        'anotherChar.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        anotherdata=anotherdata
    )


# 游戏名词云图
@app.route('/titleCloud')
def titleCloud():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    return render_template(
        'titleCloud.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
    )


# 简介词云图
@app.route('/summaryCloud')
def summaryCloud():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    return render_template(
        'summaryCloud.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
    )


# 游戏推荐
@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    username = session['username']
    typeSort, minDiscountTitle, maxUserLen, maxGames = getHeadData()
    user_ratings = get_user_ratings()
    if username in user_ratings:  # 先判断用户名是否在字典中
        titledata = user_based_collaborative_filtering(username, user_ratings)
        if titledata:
            recommendationData = []
            for i in titledata:
                print(i)

                def filter_fn(item):
                    return i in item[1]  # 直接检查推荐游戏是否在游戏标题中

                filtered_games = list(filter(filter_fn, getAllGames()))
                recommendationData.extend(filtered_games)  # 使用 extend 而不是 append

            # print(recommendationData)
        else:
            recommendationData = random.sample(getAllGames(), 5)  # 使用 random.sample 随机选取 3 个元素
    else:
        recommendationData = random.sample(getAllGames(), 5)  # 使用 random.sample 随机选取 3 个元素

    return render_template(
        'recommendation.html',
        username=username,
        typeSort=typeSort,
        minDiscountTitle=minDiscountTitle,
        maxUserLen=maxUserLen,
        maxGames=maxGames,
        recommendationData=recommendationData
    )


if __name__ == '__main__':
    app.run()
