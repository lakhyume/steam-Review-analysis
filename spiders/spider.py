import re
import time
from pymysql import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import os
import json
from utils.query import querys


# https://store.steampowered.com/search/?specials=1&page=1


def init():
    conn = connect(
        host='localhost',
        user='root',
        password='123456',
        database='steamdata',
        port=3306,
        charset='utf8mb4'
    )

    try:
        sql = '''
            CREATE TABLE games (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(255),
            icon VARCHAR(2555),  
            time VARCHAR(255),
            compatible VARCHAR(255),
            evaluate VARCHAR(255),
            discount VARCHAR(255),
            origin_price VARCHAR(255),
            now_price VARCHAR(255),
            types VARCHAR(2555), 
            summary TEXT,
            recentlyComment VARCHAR(255),
            alicomment VARCHAR(255),
            firm VARCHAR(255),
            publisher VARCHAR(255),  
            imgList TEXT,
            video TEXT,
            detailLink varchar(2555)
            );
        '''
        cusor = conn.cursor()
        cusor.execute(sql)
        conn.commit()
    except:
        pass

    if not os.path.exists('temp1.csv'):
        with open('temp1.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "title", "icon", "time", "compatible", "evaluate",
                "discount", "origin_price", "now_price", "detailLink"
            ])
    print('初始化文件成功~')


def save_to_csv(rowData):
    with open('temp1.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(rowData)
    print('保存成功~')


# 保存数据库
def save_to_sql():
    with open('temp1.csv', 'r', encoding='utf-8') as r_f:
        reader = csv.reader(r_f)
        for i in reader:
            if i[0] == 'title':
                continue
            querys('''
                insert into games (title, icon, time, compatible, evaluate, discount, origin_price, now_price, detailLink)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ''', [i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]])
        print('导入数据成功~')


def spider(spiderTarget, startPage):
    print('列表页面URL' + spiderTarget % startPage)
    browser = startBrowser()
    browser.get(spiderTarget % startPage)
    time.sleep(5)  # 等待页面加载

    # 滚动
    scroll_position = 0
    scroll_amount = 200
    max_scroll = 2000
    while scroll_position < max_scroll:
        scroll_script = f"window.scrollBy(0,{scroll_amount})"
        browser.execute_script(scroll_script)
        scroll_position += scroll_amount
        time.sleep(0.5)

    game_list = browser.find_elements(By.XPATH,
                                      "//a[@class='search_result_row ds_collapse_flag  app_impression_tracked']")
    print(len(game_list))
    for game in game_list:
        try:
            title = game.find_element(By.XPATH,
                                      "./div[@class='responsive_search_name_combined']/div[1]/span[@class='title']").text  # 获取游戏的标题属性
            # print(title)  # 打印游戏标题
            icon = game.find_element(by=By.XPATH, value="./div[@class='col search_capsule']/img").get_attribute("src")
            # print(icon)

            compatibleList = game.find_elements(by=By.XPATH,
                                                value="./div[@class='responsive_search_name_combined']/div[1]/div/span")
            compatible = []
            for i in compatibleList:
                if re.search('win', i.get_attribute("class")):
                    compatible.append(re.search('win', i.get_attribute("class")).group())
                elif re.search('mac', i.get_attribute("class")):
                    compatible.append(re.search('mac', i.get_attribute("class")).group())
                elif re.search('linux', i.get_attribute("class")):
                    compatible.append(re.search('linux', i.get_attribute("class")).group())

            # print(compatible)

            times = game.find_element(by=By.XPATH, value="./div[@class='responsive_search_name_combined']/div[2]").text
            # print(times)
            evaluate = ''
            element_class = game.find_element(by=By.XPATH,
                                              value="./div[@class='responsive_search_name_combined']/div[3]/span").get_attribute(
                "class")
            if re.search('mixed', element_class):
                evaluate = "一般"
            else:
                evaluate = "好评！"

            # print(evaluate)

            discount = 0
            try:
                discount_text = game.find_element(by=By.XPATH, value=".//div[@class='discount_pct']").text
                discount_match = re.search(r'\d+', discount_text)
                if discount_match:
                    discount = 100 - int(discount_match.group())
            except Exception as e:
                discount = 0
            # print(discount)

            origin_price_match = re.search(r'[\d,]+', game.find_element(by=By.XPATH,
                                                                        value=".//div[@class='discount_original_price']").text)
            now_price_match = re.search(r'[\d,]+', game.find_element(by=By.XPATH,
                                                                     value=".//div[@class='discount_final_price']").text)
            if origin_price_match:
                origin_price = int(origin_price_match.group())
            else:
                origin_price = None

            if now_price_match:
                now_price = int(now_price_match.group())
            else:
                now_price = None

            # print(origin_price, now_price)

            detailLink = game.get_attribute("href")
            # print(detailLink)

            print(title, icon, times, compatible, evaluate, discount, origin_price, now_price, detailLink)

            # 调用save_to_csv函数，将数据写入CSV文件
            save_to_csv(
                [title, icon, times, json.dumps(compatible), evaluate, discount, origin_price, now_price, detailLink]
            )

        except:
            pass


def startBrowser():
    service = Service('./chromedriver.exe')
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')  # 添加无头模式参数
    option.add_experimental_option('debuggerAddress', 'localhost:9222')  # 指定远程调试端口
    browser = webdriver.Chrome(service=service, options=option)  # 创建浏览器实例
    # browser.get('https://www.baidu.com/')  # 访问百度首页
    return browser


def main(spiderTarget):
    init()
    for i in range(1, 491):
        spider(spiderTarget, i)
    # 保存到数据库
    save_to_sql()


if __name__ == '__main__':
    # startBrowser()
    # init()
    # save_to_sql()
    spiderTarget = 'https://store.steampowered.com/search/?specials=1&page=%s'
    main(spiderTarget)
