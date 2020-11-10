import os

import pymysql
import requests, json
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime


# 获取用户信息
def getUserData():
    print("-----发送钉钉消息开始-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    # 打开数据库连接
    db = pymysql.connect("122.51.161.239", "root", "pzq18217074393", "weibo")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # 查询要发送的用户列表
    sql = "SELECT * FROM `dd_send` WHERE status = '0'"
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()

    for user in results:
        userId = user[1]
        userName = user[2]
        ddLink = user[3]
        getWeiboData(userId, userName, ddLink, cursor)

    # 关闭数据库连接
    db.close()
    print("-----发送钉钉消息结束-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))


# 获取用户的微博信息
def getWeiboData(userId, userName, ddLink, cursor):
    # SQL 查询语句  10分钟内的数据
    sql = "SELECT * FROM `weibo` WHERE user_id = '%s' and publish_time >= '%s'" % (
        userId, (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M"))
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    for row in results:
        id = row[0]
        userId = row[1]
        content = row[2]
        link = row[3]
        pict = row[4]
        sendMessage(userName, ddLink, content, pict)


# 发送钉钉消息
def sendMessage(userName, ddLink, content, pict):
    content = content.replace("原图", "").replace(" ", "").replace("显示地图", "").replace("视频", "")

    index = content.find("[组图")
    if index != -1:
        content = content[0:index]

    if pict != "无":
        pictList = pict.split(",")

        # 发送钉钉消息
        # 循环遍历图片，追加输出
        for picture in pictList:
            content = content + "![](" + picture + ")"

    message = "【" + userName + "】\n\n>" + content
    print(message)
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    param = {'msgtype': 'markdown', 'markdown': {"title": "微博", "text": message}}
    requests.post(ddLink, headers=headers, data=json.dumps(param))


# 执行脚本任务  开始运行程序
def getWeibo():
    print("-----爬取微博信息开始-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    os.system('cd weiboSpider;python3 -m weibo_spider')
    print("-----爬取微博信息结束-----" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    getUserData()


# 执行定时任务
def dojob():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔10分组  60*10  爬取微博信息
    scheduler.add_job(getWeibo, 'interval', seconds=600, id='test_job1')
    scheduler.start()


dojob()
# getUserData()
