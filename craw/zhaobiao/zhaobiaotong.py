import json
import traceback
from dbbase import DB_ZB
import requests
from bs4 import BeautifulSoup
import time
import re
import datetime

head = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "yunsuo_session_verify=c36b1e82f4969a52767d7b3763380253",
    "Host": "www.ccgp-hebei.gov.cn",
    "If-Modified-Since": "Mon, 14 Nov 2022 07:46:44 GMT",
    "If-None-Match": "e58b-5ed6970e4235d",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
}

urllib = {
    "张家口": "https://www.hebztb.com/zbxhcms/api/directive/contentList?categoryId=88&blurSearch=&count=10&startPublishDate=1998-08-20&area=%E5%BC%A0%E5%AE%B6%E5%8F%A3%E5%B8%82&signDate=&industryName=&pageIndex=",
    }


def get_page_number(url):
    return 3


def get_all(city, ac=""):
    base_url = urllib[city]
    # 获取有多少页
    page_num = get_page_number(base_url)
    # db
    db = DB_ZB()
    newlist = []
    # 逐页爬取
    for i in range(page_num):
        chongfu = False
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("招标通:尝试获取第%s页的数据"%(i+1))
                url = base_url + "%s"%(i+1)
                result = requests.request("get", url)

                a = json.loads(result.content)
                for r in a['page']['list']:
                    href = r['url']
                    name = r['title'].strip()
                    time_all = time.strftime("%Y-%m-%d", time.localtime(r['publishDate']/1000)).strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())
                    dbresult = db.count_documents_name(name)
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date": datetime.date(time_year, time_month, time_day),
                            "area": "",
                            "people": "",
                            "source": "zbt",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents_herf( "zbt", href)==0:
                            continue
                        else:
                            print("招标通:遇到重复数据")
                            chongfu = True
                            break
                time.sleep(10)
                break
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                trycount += 1
                if trycount > maxtry:
                    db.close()
                    return "ERROR!"
                time.sleep(100)
        if chongfu:
            break
    db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")