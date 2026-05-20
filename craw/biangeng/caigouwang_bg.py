from dbbase import DB_ZBBG
import requests
from bs4 import BeautifulSoup
import time
import traceback
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

urllib_shi = {
    "张家口": "http://www.ccgp-hebei.gov.cn/was5/web/search?channelid=240117&lanmu=gzggAAASAAAS&morelanmu=&syprovince=&sydoctitle=&admindivcode=130700000&purchaseWay1=&PurchaserName=&province=130700000&city=&purchaseWay=&txtcgbm=&titlename=&searchword1=&txtdljg=&fstarttime=&fendtime="
}
urllib_xian = {
    "张家口": "http://www.ccgp-hebei.gov.cn/zjk/zjk/index_751.html"
}

def get_page_number(url):
    # 简化处理，只获取前三页
    return 1

def get_shi(base_url, db, city):
    newlist = []
    # 获取有多少页
    page_num = get_page_number(base_url)
    # 逐页爬取
    for j in range(page_num):
        chongfu = 0
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("采购网:尝试获取第%s页的数据"%(j+1))
                url = base_url + "&page=%s"%(j+1)
                result = requests.request("get", url)
                soup = BeautifulSoup(result.content, 'html.parser')
                a = soup.find_all("tr", id="biaoti")
                b = soup.find_all("td", class_="txt1")
                assert len(a) == len(b)
                for i in range(len(a)):
                    href = a[i].find("a").get("href")
                    name = a[i].text.strip()
                    blist = b[i].find_all("span")
                    time_all = blist[0].text.strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())
                    area = blist[1].get("title").strip()
                    people = blist[2].get("title").strip()
                    dbresult = db.count_documents_name(name)
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date": datetime.date(time_year, time_month, time_day),
                            "area": area,
                            "people": people,
                            "source": "hbcg",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents_herf("hbcg", href)==0:
                            continue
                        else:
                            print("采购网:遇到重复数据")
                            chongfu += 1
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
        if chongfu>= 1:
            break
    return newlist


def get_xian(base_url, db, city):
    newlist = []
    # 获取有多少页
    page_num = get_page_number(base_url)
    # 逐页爬取
    for j in range(page_num):
        chongfu = 0
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("采购网:尝试获取第%s页的数据" % (j + 1))
                if j == 0:
                    url = base_url
                else:
                    url = base_url.replace(".html", "_%s.html"%j)
                result = requests.request("get", url)
                soup = BeautifulSoup(result.content, 'html.parser')
                table = soup.find_all("table", id="moredingannctable")[0]
                a = table.find_all("a")
                b = table.find_all("td", class_="txt1")
                assert len(a) == len(b)
                for i in range(len(a)):
                    href = url.replace(url.split("/")[-1], a[i].get("href"))
                    name = a[i].text.strip()
                    blist = b[i].find_all("span")
                    time_all = blist[0].text.strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())
                    area = blist[1].text.strip()
                    people = blist[2].text.strip()

                    if db.count_documents_herf("hbcg", href) == 0:
                        d = {
                            "name": name,
                            "href": href,
                            "date": datetime.date(time_year, time_month, time_day),
                            "area": area,
                            "people": people,
                            "source": "hbcg",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        print("采购网:遇到重复数据")
                        chongfu += 1
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
        if chongfu >= 1:
            break
    return newlist


def get_all(city):
    # db
    db = DB_ZBBG()
    newlist = []
    # 市区
    base_url = urllib_shi[city]
    newlist.extend(get_shi(base_url, db, city))
    # 县域
    base_url = urllib_xian[city]
    newlist.extend(get_xian(base_url, db, city))
    # close
    db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")





















