from bak.database import getdb
import requests
from bs4 import BeautifulSoup
import time
import traceback

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
    "张家口": "http://hbzjk.86ztb.com/finddata.htm"
}

data = {
    "org.apache.struts.taglib.html.TOKEN": "b4774dc76c78ca28d6761dba9a8409e1",
    "htm": "dataList",
    "postmode": "2",
    "id": "0",
    "ids": "",
    "ordername": ["t.id", "t.id"],
    "order": ["desc", "desc"],
    "isorder": "no",
    "tempordername": "",
    "systemtype": "100",
    "findTemp": "",
    "tempId": "",
    "pf": "hbzjk",
    "indexid": "",
    "indexid2": "0",
    "tendertype2": "",
    "property": "",
    "province": "河北省",
    "city": "张家口市",
    "xian": "",
    "opentype": "",
    "fromday": "",
    "endday": "",
    "findText": "名称",
    "state": "2",
    "pageSize": "0"
}


def get_page_number(url):
    # result = requests.request("post", url, data=data)
    # soup = BeautifulSoup(result.content, 'html.parser')
    # 先不获取总数量，只爬前面10页的
    return 3


def get_all(city, ac=""):
    assert city=="张家口"
    base_url = urllib[city]
    # 获取有多少页
    page_num = get_page_number(base_url)
    # db
    db = getdb()
    # 报告结果
    newlist = []
    # 逐页爬取
    for i in range(page_num):
        chongfu = False
        trycount = 0
        maxtry = 5

        while True:
            try:
                print("ycg:尝试获取第%s页的数据"%(i+1))
                url = base_url
                data["currentPage"] = i + 1
                result = requests.request("post", url, data=data)
                soup = BeautifulSoup(result.content, 'html.parser')
                r = soup.find_all("tr", class_="middle")
                for i in r:
                    a = i.find("td", class_="autoline")
                    href = a.a['onclick'].strip()[13:-3]
                    name = a.a['title'].strip()

                    b = i.find_all("td")
                    time_all = b[-1].text.strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())

                    style = b[4].text.strip()
                    code = b[1].text.strip()
                    people = b[3].text.strip()
                    type = b[5].next.next.next.strip()
                    price = b[7].text.strip()

                    # dbresult = db.count_documents({"source": "ycg", "href":href})
                    dbresult = db.count_documents({"name": name})
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date_y": time_year,
                            "date_m": time_month,
                            "date_d": time_day,
                            "style": style,
                            "people": people,
                            "code": code,
                            "type": type,
                            "price": price,
                            "source": "ycg",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents({"source": "ycg", "href":href})==0:
                            continue
                        else:
                            print("云采供:遇到重复数据")
                            chongfu = True
                            break
                time.sleep(10)
                break
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                trycount += 1
                if trycount > maxtry:
                    db.db.close()
                    return "ERROR!"
                time.sleep(100)
        if chongfu:
            break
    db.db.close()

    return newlist

if __name__ == "__main__":
    get_all("张家口")
    # get_page_number(urllib['张家口'])