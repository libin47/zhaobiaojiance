import json
import traceback
from bak.database import getdb
import requests
import time

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

# "https://www.hebztb.com/zbxhcms/category/bulletinList.html?searchDate=1997-12-19&dates=300&word=&word2=&categoryId=88&industryName=&projectAreaName=%E5%BC%A0%E5%AE%B6%E5%8F%A3%E5%B8%82&status=&dates2=300&tabName=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&searchDate2=NaN-aN-aN"
urllib = {
    "张家口": "https://www.hebztb.com/zbxhcms/api/directive/contentList?categoryId=88&blurSearch=&count=10&startPublishDate=1998-08-20&area=%E5%BC%A0%E5%AE%B6%E5%8F%A3%E5%B8%82&signDate=&industryName=&pageIndex=",
    }


def get_page_number(url):
    # result = requests.request("get", url)
    # soup = BeautifulSoup(result.content, 'html.parser')
    # text = soup.find_all("script")[18].text
    # allpage = re.findall("total: [1-9]+,", text)[0]
    # allpage = int(allpage.replace("total: ","").replace(",", ""))//10+1
    return 3


def get_all(city, ac=""):
    base_url = urllib[city]
    # 获取有多少页
    page_num = get_page_number(base_url)
    # db
    db = getdb()
    newlist = []
    # 逐页爬取
    for i in range(page_num):
        chongfu = False
        trycount = 0
        maxtry = 5
        while True:
            try:
                print("zbt:尝试获取第%s页的数据"%(i+1))
                url = base_url + "%s"%(i+1)
                result = requests.request("get", url)

                a = json.loads(result.content)
                # soup = BeautifulSoup(result.content, 'html.parser')
                # a = soup.find("div", class_="clearboth").find_all("ul", class_="newslist")[0].find_all("li", recursive=False)
                for r in a['page']['list']:
                    href = r['url']
                    name = r['title'].strip()
                    time_all = time.strftime("%Y-%m-%d", time.localtime(r['publishDate']/1000)).strip().split("-")
                    time_year = int(time_all[0].strip())
                    time_month = int(time_all[1].strip())
                    time_day = int(time_all[2].strip())

                    # dbresult = db.count_documents({"source": "zbt", "href":href})
                    dbresult = db.count_documents({"name": name})
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date_y": time_year,
                            "date_m": time_month,
                            "date_d": time_day,
                            "source": "zbt",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents({"source": "zbt", "href":href})==0:
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
                    db.db.close()
                    return "ERROR!"
                time.sleep(100)
        if chongfu:
            break
    db.db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")