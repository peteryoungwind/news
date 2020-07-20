import random
import time

import requests, json
from lxml import etree
from redis import StrictRedis
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# # 36氪 快讯

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

class News:
    def __init__(self, title, date, content, link):
        self.title = title
        self.date = date
        self.content = content
        self.link = link

    def __str__(self):
        print(self.title, self.date, self.content, self.link)


class Spider(object):

    def __init__(self):
        self.url = "https://36kr.com/newsflashes"
        self.headers = {
            # 随机获取user_agent  降低风险，避免ip被封
            "User-Agent": random.choice(user_agent),
            "cookie": "krtoken=PssP2QSZCNxox2aZuQZgv2-W13mpsqJKBQFppE7xbQ5vpJKEPo84aAR3Z_gx247n; krnewsfrontcc=eyJ0eXAiOiJKV1QiLCJhbGciOiIzNmtyLWp3dCJ9.eyJpZCI6MTEzMDg2NzQ2MSwic2Vzc2lvbl9pZCI6Ijg2ZDA2NzQwZmYyYWUxN2YxOTBlZmU2YjRhYmU0MDdlIiwiZXhwaXJlX3RpbWUiOjE1ODQxNDk4MDYsInZlcnNpb24iOiJ2MSJ9.8efe98eb128157f8e0947beece7f768354927d7e28e354e75d7667f8acc468d7; acw_tc=2760826115949942682328936e84221e022bb74517c96b7604f74bb75aaf78; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221130867461%22%2C%22%24device_id%22%3A%221706fe2903517a-0deea1ef304356-39677b0e-2073600-1706fe290367c2%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%2C%22first_id%22%3A%221706fe2903517a-0deea1ef304356-39677b0e-2073600-1706fe290367c2%22%7D; Hm_lvt_713123c60a0e86982326bae1a51083e1=1594994269; Hm_lvt_1684191ccae0314c6254306a8333d090=1594994269; Hm_lpvt_713123c60a0e86982326bae1a51083e1=1594995238; Hm_lpvt_1684191ccae0314c6254306a8333d090=1594995238; SERVERID=6754aaff36cb16c614a357bbc08228ea|1594995238|1594994269",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "max-age=0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
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
        for i in range(1, 6, 1):
            # 打印标题
            item_title = html.xpath("//div[@class='newsflash-catalog-flow-list']/div[@class='flow-item'][" + str(i) + "]//a[@class='item-title']/text()")
            item_title = item_title[0]
            # print(item_title)
            # 打印标题
            item_link = html.xpath("//div[@class='newsflash-catalog-flow-list']/div[@class='flow-item'][" + str(i) + "]//a[@class='item-title']/@href")
            item_link = item_link[0]
            item_link = item_link.replace("/newsflashes/", "")
            # print(item_link)
            # 打印内容
            item_content = html.xpath("//div[@class='newsflash-catalog-flow-list']/div[@class='flow-item'][" + str(i) + "]//div[@class='item-desc']/span/text()")
            item_content = item_content[0]
            # print(item_content)
            new = News(item_title, "item_date", item_content, item_link)
            news_list.append(new)

        self.save_to_redis(news_list)

    def run(self):
        data = self.get_data()
        # 解析
        self.parse_data(data)

    def save_to_redis(self, data_list):

        # 小强快讯 测试群
        url1 = "https://oapi.dingtalk.com/robot/send?access_token=4fc053be3fa145a94a73054dff756fb7c307a25cdde14686abbbce8a8c0963e9"
        # 小强机器人
        url2 = "https://oapi.dingtalk.com/robot/send?access_token=53b83f1c6a2ef0c7822a91c9ac7019ee99a7a7a764733a4915a165a3cde1c133"
        # 快讯早知道
        url3 = "https://oapi.dingtalk.com/robot/send?access_token=891ebab37f0836c6912c35f6de05a5e8ca4ec072571902cbc49780c94cde3464"
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
                    print("发送消息 " + curr_time.strftime("%Y-%m-%d %H:%M") + news.title)
                    # 存储redis  去重  过期时间10小时
                    # sr.set("36kr" + news.link, news.title)
                    # sr.expire("36kr" + news.link, 36000)
                    send_list.append(news.link)
                    # 发送钉钉消息
                    message = "【" + news.title + "】" + "\n\n" + news.content
                    param = {'msgtype': 'markdown', 'markdown': {"title": "36kr快讯", "text": message}}
                    requests.post(url1, headers=headers, data=json.dumps(param))
                    # requests.post(url2, headers=headers, data=json.dumps(param))
                    # time.sleep(2)
                    # requests.post(url3, headers=headers, data=json.dumps(param))
        except Exception as e:
            print(e)


def task():

    # 范围时间  0：00至7：00不发送消息
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:01', '%Y-%m-%d%H:%M')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:00', '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()

    # 判断当前时间是否在范围时间内 满足条件不执行消息
    if d_time < n_time < d_time1:
        pass
    else:
        # 随机设置延迟时间0-30s  避免ip被封，降低风险
        time.sleep(random.randint(0, 30))
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
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔90S
    scheduler.add_job(task, 'interval', seconds=180, id='test_job1')
    scheduler.start()

# 开启任务
dojob()

