from dbbase import DB_ZB
import requests
from bs4 import BeautifulSoup
import time
import traceback
import datetime

head = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
    "Connection": "keep-alive",
    "Cookie": "__51uvsct__undefined=1; __51vcke__undefined=eefa9345-5b98-5fde-801d-75e20d4a4027; __51vuft__undefined=1750989034827; JSESSIONID=994CCFC645D5300D7731E0C9A354D268; __51cke__=; __tins__19687679=%7B%22sid%22%3A%201752136010368%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201752138531732%7D; __51laig__=8",
    "Host": "szj.hebei.gov.cn",
    "origin":"https://szj.hebei.gov.cn",
    "Referer": "https://szj.hebei.gov.cn/zbtbfwpt/tender/xxgk/list.do?selectype=zbgg",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}

url = "https://szj.hebei.gov.cn/zbtbfwpt/tender/xxgk/zbgg.do"
data = {
    "张家口": {
        "TimeStr": "",
        "allDq": "130700",
        "allHy": "reset1",
        "AllPtName": "",
        "KeyType": "ggname",
        "KeyStr": "",
        "page": "0",
    }
}


def get_page_number(url):
    # 简化处理，只获取前三页
    return 3


def get_all(city):
    global url
    base_url = url
    # 获取有多少页
    page_num = get_page_number(base_url)
    # db
    db = DB_ZB()
    newlist = []
    # 逐页爬取
    for j in range(page_num):
        chongfu = 0
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("河北省招标投标公共服务平台:尝试获取第%s页的数据"%(j+1))
                url = base_url
                pdata = data[city]
                pdata["page"] = str(j)
                result = requests.post(url, data=pdata, headers=head)
                soup = BeautifulSoup(result.content, 'html.parser')

                a =  soup.find_all("div", class_="publicont")
                for i in range(len(a)):
                    href = "https://szj.hebei.gov.cn" + a[i].find("a").get("href")
                    name = a[i].find("a").get("title").strip()
                    time_all = a[i].find("span", class_="span_o").text.strip().split("-")
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
                            "source": "ggfw",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents_herf("ggfw", href)==0:
                            continue
                        else:
                            print("河北省招标投标公共服务平台:遇到重复数据")
                            chongfu += 1
                            if chongfu >= 3:
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
        if chongfu>= 3:
            break
    db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")





















