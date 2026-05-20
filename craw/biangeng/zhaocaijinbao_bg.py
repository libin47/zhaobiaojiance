from dbbase import DB_ZBBG
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import traceback
import json


head = {
    "authority": "hb.zcjb.com.cn",
    "method": "POST",
    "path":"/cms/api/dynamicData/queryContentPage",
    "scheme":"https",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "content-length":"146",
    "content-type": "application/json; charset=UTF-8",
"referer":"https://hb.zcjb.com.cn/cms/hb/webfile/zdhb=jyxx/index.html?bulletinType=&projectType=7282500&city=130700",
"x-requested-with":"XMLHttpRequest"
}

typelist = ['政府采购', '建设工程', '企业采购']
datas = [
    {
        "pageNo": 1,
        "pageSize": 10,
        "dto": {
            "categoryId": "7282530",
            "city": "130700",
            "publishDate":"",
            "publishEndDate": "",
            "purchaseMode":"",
            "siteId": "728"
        }
    },
    {
        "pageNo": 1,
        "pageSize": 10,
        "dto": {
            "categoryId": "7282230",
            "city": "130700",
            "publishDate": "",
            "publishEndDate": "",
            "purchaseMode": "",
            "siteId": "728"
        }
    },
    {
        "pageNo": 1,
        "pageSize": 10,
        "dto": {
            "categoryId": "7282130",
            "city": "130700",
            "publishDate": "",
            "publishEndDate": "",
            "purchaseMode": "",
            "siteId": "728"
        }
    }
]

urllib = {
    "张家口": "https://hb.zcjb.com.cn/cms/api/dynamicData/queryContentPage"
}


def get_page_number(url):
    return 3


def get_all(city, ac=""):
    base_url = urllib[city]
    # db
    db = DB_ZBBG()
    newlist = []
    data_copy = datas.copy()
    # 逐类爬取
    for ddd in data_copy:
        # 获取有多少页
        page_num = get_page_number(base_url)
        # 逐页爬取
        for i in range(page_num):
            chongfu = False
            trycount = 0
            maxtry = 5
            ddd["pageNo"] = i+1
            while True:
                try:
                    print("zcjb:尝试获取第%s页的数据"%(i+1))
                    url = base_url
                    result = requests.post(url, json=ddd, headers=head)
                    print(result)
                    if result.status_code == 200:
                        zbdata = json.loads(result.content)
                        for r in zbdata["res"]["rows"]:
                            id = r["id"]
                            name = r['title'].strip()
                            date = r['publishDate']
                            city = r['cityName']
                            people = r['tendereeOrgName'] if 'tendereeOrgName' in r.keys() else ""
                            href = "https://hb.zcjb.com.cn/cms/hb/webfile/detail/index.html?contentId="+id

                            if db.count_documents_herf("zcjb", href)==0:
                                d = {
                                    "name": name,
                                    "href": href,
                                    "date": datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
                                    "area": "",
                                    "source": "zcjb",
                                    "city": city,
                                    "people": people
                                }
                                db.insert_one(d)
                                newlist.append(d)
                            else:
                                print("招采进宝:遇到重复数据")
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
    # get_page_number('http://hb.zcjb.com.cn/cms/channel/zfcggg/index.htm')
