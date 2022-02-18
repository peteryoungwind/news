import random
import time

import requests, json
from lxml import etree
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from jsonpath import jsonpath


# 东方财富 快讯

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
    def __init__(self, title, date, content, link, origin_link):
        self.title = title
        self.date = date
        self.content = content
        self.link = link
        self.origin_link = origin_link

    def __str__(self):
        print(self.title, self.date, self.content, self.link)


class Spider(object):

    def __init__(self):
        self.url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html?r=0.1711645623562963&_="
        self.headers = {
            # 随机获取user_agent  降低风险，避免ip被封
            "User-Agent": random.choice(user_agent),
            "cookie": "em-quote-version=topspeed; HAList=a-sh-600015-%u534E%u590F%u94F6%u884C%2Ca-sz-300059-%u4E1C%u65B9%u8D22%u5BCC; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; ct=Xqz2tJcvfg5yKT3rXOpMH54ppz9nBXuWU2IJzcDcu2HqI2G-aaBl-Qj5urIh8x1yFoCB2YBRPwUjdQ5mKOVxDQCzfzFoigmAq23MredqgdOMlPlP_muaQ1OqxY59FI_Us6JpJMiGRlbSd5NsZjLqXvL2Bz0_dMxetzdgApQbaXw; ut=FobyicMgeV44-elHX7PY7IudLN5pGuUQZF1tw4i0eB3dBvJ87qE98KCxxNBtnfBuuFyhhYvozy_-HgMOAesV78DOiJKdgcbZhOJNbeZZfqmZcoRxuOXTUBXkGdnEo5dPpfvqUfpjZOSgelonyGJIsGMI9QSGcFo6RV5Rnxbl-i-WcJLvEgIyASnbui0YsTm1-sJXGk6p9MsgZnvkMIy-3LbwFSG9xLhGotB_M9uBncgavmYYBruj8ZO85GmbHE5l2a7Kn_kYxKgwTcJDJ1anaHTZAQuZNqpY9wEG9ncOSfYvSaZKnymuw-jXYW5ggVzlhe4jiTyt4f2dPCGVa_2m48-I-8zpxXaD3hqiKgDQ4QdOFjMOQTdUyIalSn2sCIPBkB1Ei_oZDjumnAA6ywnJ04WQdcS26pp5fYqBeX36W7Hpq_bm2dpw1RneOP-KBEyGSNTj6te-708V4SLM1aVs1CGjcIsYreJvfdL9r-NgprvxAdBgjVKTsw; pi=9606345878213960%3bg9606345878213960%3bMartin_pan%3bFL1NQS13eXpTbQgKI%2bUPK2ht4sClg7vHSR7ezcDyKsZZuxrRyCATvx37hNYXAjp3EQIzx%2fJG9fAd9NbvtNbSwKbGAndlknejAvlPsYQ9a37Vv9N0a%2bacB4QDnd8U4xFT5QPiPqeYgpWcnBEvIwFY8CWDxpP9fhnwvjmBvNx3%2fsDTD0EbjVTorkLWNEGj1ApAHEVV5D0D%3barMAoTzGfZl%2bJtVqwy4UrSoX0BM7YtcFEN253TBmbZbtMTyXXo4FjT2mCMgE4W26fRpMWYOJypIJPVTAqQJMmvBgCaSDkKca79LW7KanSNOhqRv0DCbGJf%2b2QCtiKQ6Q5JYiVHVhIfi6gircXxiCHQ%2bjKmColg%3d%3d; uidal=9606345878213960Martin_pan; sid=145380459; vtpst=|; fund_trade_trackid=M8KghoT37xpvBZlSfjzQK6FAFT9rK+jaBVTXfwnOmxn7uZf+UDzArjVnEmzDsftqDkqAfgt316rCw4rPuU74NA==; EMFUND0=null; EMFUND8=07-12%2018%3A12%3A32@%23%24%u5E7F%u53D1%u7535%u5B50%u4FE1%u606F%u4F20%u5A92%u80A1%u7968@%23%24005310; EMFUND9=07-14 22:05:06@#$%u524D%u6D77%u5F00%u6E90%u518D%u878D%u8D44%u80A1%u7968@%23%24001178; waptgshowtime=2020717; qgqp_b_id=682030916dcf1edfbbb705a82a00b45f; st_si=69517463757569; st_pvi=57501768486839; st_sp=2020-02-21%2021%3A07%3A49; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20200717230244241-113103303721-2349129884; st_asi=20200717230244241-113103303721-2349129884-dfcfwsy_dfcfwxsy_ycl_ewmxt-1",
            "accept-encoding": "gzip, deflate, br",
            "cache-control": "max-age=0",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "upgrade-insecure-requests": "1"
        }
        self.post_data = {

        }

    def get_data(self):
        get_url = self.url + str(int(time.time() * 1000))
        response = requests.post(get_url, headers=self.headers)
        # 默认返回bytes类型，除非确定外部调用使用str才进行解码操作
        return response.content.decode()

    def parse_data(self, data):

        data_dict = json.loads(data)

        title_list = jsonpath(data_dict, '$..title')
        url_list = jsonpath(data_dict, '$..url_w')
        content_list = jsonpath(data_dict, '$..digest')

        news_list = []
        for i in range(0, 5, 1):
            item_title = title_list[i]
            item_link = url_list[i]
            origin_link = item_link
            item_link = item_link.replace("http://finance.eastmoney.com/news/", "").replace(".html", "").replace(",", "")
            item_content = content_list[i]
            index = item_content.find("】") + 1
            item_content = item_content[index:len(item_content)]

            new = News(item_title, "item_date", item_content, item_link, origin_link)
            news_list.append(new)

        self.save_to_redis(news_list)

    def run(self):
        data = self.get_data()
        data = data.replace("var ajaxResult=","")
        # print(data)
        # 解析
        self.parse_data(data)

    def save_to_redis(self, data_list):


        # 小强快讯 测试群
        url1 = "https://oapi.dingtalk.com/robot/send?access_token=c7860c345fa6b7d858c16c74eddc0c6508a24cf688a6183633665f0c4baa510c"
        # 小强机器人
        url2 = "https://oapi.dingtalk.com/robot/send?access_token=69c8915d30dc778b10171577b1e4f59f3541dfb93d05975c2ee5d46d5bb5619c"
        # 快讯早知道
        url3 = "https://oapi.dingtalk.com/robot/send?access_token=12e0bd2e72fc328c4e29762f747b29ada8678dc2520eaea6b58f0216c40e848a"
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        # 连接redis
        try:
            # sr = StrictRedis(host='122.51.161.239', port=6379, db=0)
            global send_list
            curr_time = datetime.datetime.now()
            for news in data_list:
                if news.link in send_list:
                    continue
                else:
                    print("发送消息 " + curr_time.strftime("%Y-%m-%d %H:%M") + " " + news.title)
                    # 存储redis  去重  过期时间5小时
                    # sr.set("dfcf" + news.link, news.title)
                    # sr.expire("dfcf" + news.link, 18000)
                    # 发送钉钉消息
                    send_list.append(news.link)
                    message = "[【" + news.title + "】]" + "(" + news.origin_link + ")" + "\n\n" + news.content
                    param = {'msgtype': 'markdown', 'markdown': {"title": "东财快讯", "text": message}}
                    requests.post(url2, headers=headers, data=json.dumps(param))
                    # requests.post(url2, headers=headers, data=json.dumps(param))
                    # time.sleep(2)
                    # requests.post(url3, headers=headers, data=json.dumps(param))
        except Exception as e:
            print(e)


def task():

    # 随即暂停0-30秒  降低风险
    time.sleep(random.randint(0, 3))
    print("---开始执行任务---")
    global send_list
    # 只保留12条已经发送过的消息
    if len(send_list) > 12:
        print("清除消息，总共数量" + str(len(send_list)))
        del send_list[0]
        print(send_list)
    spider = Spider()
    spider.run()

    # # 范围时间  0：30至6：00不发送消息
    # d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:30', '%Y-%m-%d%H:%M')
    # d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '6:00', '%Y-%m-%d%H:%M')
    # # 当前时间
    # n_time = datetime.datetime.now()
    #
    # # 判断当前时间是否在范围时间内 满足条件不执行消息
    # if d_time < n_time < d_time1:
    #     pass
    # else:
    #     # 随机设置延迟时间0-30s  避免ip被封，降低风险
    #     time.sleep(random.randint(0, 30))
    #     spider = Spider()
    #     spider.run()


def dojob():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    # 添加任务,时间间隔90S
    scheduler.add_job(task, 'interval', seconds=10, id='test_job1')
    scheduler.start()

# 开启任务
dojob()

