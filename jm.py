import random
import time

import requests, json
from lxml import etree
# from redis import StrictRedis
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# import pymysql

# 界面新闻  快讯

user_agent = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
]

send_list = []

# def insertData(sql):
#     # 打开数据库连接
#     db = pymysql.connect("120.48.17.131", "root", "pzq18217074393", "news")
#     # 使用cursor()方法获取操作游标
#     cursor = db.cursor()
#
#     # SQL 插入语句
#     # sql = """INSERT INTO news(news_id, title, url, content, create_time) values('12','测试', 'http:', '暗示法挖而非瓦房挖而非瓦尔', '2020-09-18 21:22')"""
#     try:
#         # 执行sql语句
#         cursor.execute(sql)
#         # 提交到数据库执行
#         db.commit()
#     except:
#         # 如果发生错误则回滚
#         db.rollback()
#
#     # 关闭数据库连接
#     db.close()

class News:
    def __init__(self, title, date, content, link, origin_link):
        self.title = title
        self.date = date
        self.content = content
        self.link = link
        self.origin_link = origin_link

    def __str__(self):
        print(self.title, self.date, self.content, self.link, self.origin_link)


class Spider(object):

    def __init__(self):
        self.url = "https://www.jiemian.com/lists/4.html"
        self.headers = {
            # 随机获取user_agent  降低风险，避免ip被封
            "User-Agent": random.choice(user_agent)
        }
        self.post_data = {

        }

    def get_data(self):
        response = requests.post(self.url, headers=self.headers)
        # 默认返回bytes类型，除非确定外部调用使用str才进行解码操作
        return response.content.decode()

    def parse_data(self, data):
        html = etree.HTML(data)

        news_list = []

        for i in range(0, 5, 1):
            # 打印时间
            item_date = html.xpath('//div[@id="load-list"]//div[@class="columns-right-center__newsflash-date-node"]/text()')
            item_date = item_date[i]
            # 打印标题
            item_title = html.xpath('//div[@id="load-list"]//div[@class="columns-right-center__newsflash-content"]/h4/a/text()')
            item_title = item_title[i]
            # 打印链接
            item_link = html.xpath('//div[@id="load-list"]//div[@class="columns-right-center__newsflash-content"]/h4/a/@href')
            item_link = item_link[i]
            origin_link = item_link
            item_link = item_link.replace("https://www.jiemian.com/article/", "").replace(".html", "")
            item_link = "jm" + item_link
            # 打印内容
            item_content = html.xpath('//div[@id="load-list"]//div[@class="columns-right-center__newsflash-content"]/p/text()')
            item_content = item_content[i]
            item_content = item_content.replace("】", "").strip()
            new = News(item_title, item_date, item_content, item_link, origin_link)
            news_list.append(new)

        self.save_to_redis(news_list)

    def run(self):
        data = self.get_data()
        # 解析
        self.parse_data(data)

    def save_to_redis(self, data_list):

        # 小强快讯
        url1 = "https://oapi.dingtalk.com/robot/send?access_token=e0dc9bec54bb4ed2dd128fd197a08fe41799e219b6292300aba42d4e8dd91bbc"
        # 小强机器人
        url2 = "https://oapi.dingtalk.com/robot/send?access_token=9e7f21e8bf07c8a5afaa13a61cb8ea2458912d7f0bc6f6e475684744aa6c8eef"
        # 快讯早知道
        url3 = "https://oapi.dingtalk.com/robot/send?access_token=a08c8d50ce6ce28db08c93c7b1cf9242ecc9f48110e1c31bccea13188713acca"
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        # 连接redis
        try:
            # sr = StrictRedis(host='122.51.161.239', port=6379, db=0)
            curr_time = datetime.datetime.now()
            global send_list
            for news in data_list:
                if news.link in send_list:
                    continue
                else:
                    print("发送消息 " + curr_time.strftime("%Y-%m-%d %H:%M") + " " + news.title)
                    # 存储redis  去重 过期时间1小时
                    # sr.set(news.link, news.title)
                    # sr.expire(news.link, 18000)
                    # 把发送过的消息 保存起来
                    send_list.append(news.link)
                    # 发送钉钉消息
                    message = "[【" + news.title + "】]" + "(" + news.origin_link + ")" + "\n\n" + news.content
                    param = {'msgtype': 'markdown', 'markdown': {"title": "快讯", "text": message}}
                    # requests.post(url1, headers=headers, data=json.dumps(param))
                    # requests.post(url2, headers=headers, data=json.dumps(param))
                    # time.sleep(2)
                    requests.post(url3, headers=headers, data=json.dumps(param))

                    # 插入数据库
                    # sql = "INSERT INTO news(news_id, title, url, content, create_time, source) VALUES ('%s', '%s',  '%s',  '%s',  '%s',  '%s')" % (
                    #     news.link, news.title, news.origin_link, news.content, curr_time.strftime("%Y-%m-%d %H:%M"), '界面')
                    # insertData(sql)
        except Exception as e:
            print(e)


def task():
    # 范围时间
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:01', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:00', '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()

    # 判断当前时间是否在范围时间内
    if d_time < n_time < d_time1:
        pass
    else:
        # 随机暂停0-30秒  降低风险
        time.sleep(random.randint(0, 20))
        print("---开始执行任务---")

        global send_list
        # 只保留12条已经发送过的消息
        if len(send_list) > 12:
            print("清除消息，总共数量" + str(len(send_list)))
            del send_list[0]
            print(send_list)
        spider = Spider()
        spider.run()


def dojob():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    # 添加任务,时间间隔40S
    scheduler.add_job(task, 'interval', seconds=60, id='test_job1')
    scheduler.start()


dojob()



