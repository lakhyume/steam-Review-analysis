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


# 定义Spider类
class Spider(object):
    # 类的构造函数
    def __init__(self, spiderUrl):
        self.spiderUrl = spiderUrl

    def startBrowser(self):
        service = Service('./chromedriver.exe')
        option = webdriver.ChromeOptions()
        # option.add_argument('--headless')  # 添加无头模式参数
        option.add_experimental_option('debuggerAddress', 'localhost:9222')  # 指定远程调试端口
        browser = webdriver.Chrome(service=service, options=option)  # 创建浏览器实例
        # browser.get(self.spiderUrl)  # 访问游戏详情列表
        return browser

    def main(self, id):
        browser = self.startBrowser()
        print('详情页面URL：' + self.spiderUrl)
        browser.get(self.spiderUrl)
        time.sleep(1)

        types = []
        for type in browser.find_elements(By.XPATH, '//div[@class="glance_tags popular_tags"]/a'):
            if type.text:
                types.append(type.text)
        # print(types)

        try:
            # 提取游戏描述
            summary = browser.find_element(By.XPATH, '//div[@class="game_description_snippet"]').text
        except:
            summary = '无'

        # 初始化评论变量
        recentlyComment = ''
        aliComment = ''

        try:
            # 分析最近评论
            if re.search('mixed',
                         browser.find_element(By.XPATH, '//*[@id="userReviews"]/div[1]/div[2]/span[1]').get_attribute(
                             "class")):
                recentlyComment = '一般'
            else:
                recentlyComment = '好评'
        except:
            recentlyComment = '暂无'

        try:
            # 分析所有评论
            if re.search('mixed',
                         browser.find_element(By.XPATH, '//*[@id="userReviews"]/div[2]/div[2]/span[1]').get_attribute(
                             "class")):
                aliComment = '一般'
            else:
                aliComment = '好评'
        except:
            aliComment = '暂无'

        # 打印结果
        # print(summary, recentlyComment, aliComment)

        # 提取公司名称
        try:
            firm = browser.find_elements(By.XPATH, '//div[@class="summary column"]/a')[0].text
        except:
            print('该游戏为套装,跳过成功~')
            print()
            return

        # 提取发行商名称
        try:
            publisher = browser.find_elements(By.XPATH, '//div[@class="summary column"]/a')[1].text
        except:
            publisher = ''

        # 提取图片列表
        imgList = [img.get_attribute('src') for img in browser.find_elements(By.XPATH,
                                                                             '//div[@class="highlight_strip_item highlight_strip_screenshot"]/img')]
        try:
            video = browser.find_element(By.XPATH,
                                         '//video[@class="highlight_player_item highlight_movie"]').get_attribute('src')
        except:
            video = ''

        # print(firm, publisher, imgList, video)

        # 执行更新操作
        querys(
            'UPDATE games SET types = %s, summary = %s,recentlyComment = %s,aliComment = %s,firm = %s,publisher = %s,imgList = %s,video = %s WHERE id = %s',
            [json.dumps(types), summary, recentlyComment, aliComment, firm, publisher, json.dumps(imgList), video, id])

        print(types, recentlyComment, aliComment, firm, publisher, video)
        print()


if __name__ == '__main__':
    gameList = querys('select * from games', [], 'select')

    # 遍历游戏详情列表
    for i in gameList[0:]:
        spiderObj = Spider(i[-1])
        spiderObj.main(i[0])
