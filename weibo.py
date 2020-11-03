import os

import pymysql
import requests, json
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime

def searchData():
    print("-----发送钉钉消息开始-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    # 打开数据库连接
    db = pymysql.connect("122.51.161.239", "root", "pzq18217074393", "weibo")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # SQL 查询语句  30分钟内的数据
    sql = "SELECT * FROM `weibo` WHERE publish_time > date_add(now(),interval -30 minute)"
    print(sql)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        results = cursor.fetchall()
        # 小强快讯
        url1 = "https://oapi.dingtalk.com/robot/send?access_token=e0dc9bec54bb4ed2dd128fd197a08fe41799e219b6292300aba42d4e8dd91bbc"
        headers = {"Content-Type": "application/json;charset=UTF-8"}

        for row in results:
            id = row[0]
            userId = row[1]
            content = row[2]
            link = row[3]
            pict = row[4]

            content = content.replace("原图", "").replace(" ", "").replace("显示地图", "").replace("视频", "")

            index = content.find("[组图")
            if index != -1:
                content = content[0:index]

            # SQL 查询语句
            sql = "SELECT nickname FROM `user` WHERE id = '%s'" % (userId)
            print(sql)
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            userResults = cursor.fetchall()
            userName = userResults[0][0]

            pictList = pict.split(",")

            # 发送钉钉消息
            #循环遍历图片，追加输出
            for picture in pictList:
                content = content + "![](" + picture + ")"

            message = "【" + userName + "】\n\n>" + content
            print(message)
            param = {'msgtype': 'markdown', 'markdown': {"title": "快讯", "text": message}}
            requests.post(url1, headers=headers, data=json.dumps(param))
    except:
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()
    print("-----发送钉钉消息结束-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

def getWeibo():
    print("-----爬取微博信息开始-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    os.system('python -m weiboSpider')
    print("-----爬取微博信息结束-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    searchData()

def dojob():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔30分组  60*30  爬取微博信息
    scheduler.add_job(getWeibo, 'interval', seconds=300, id='test_job1')
    scheduler.start()


dojob()
# getWeibo()
