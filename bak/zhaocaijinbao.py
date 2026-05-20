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

typelist = ['政府采购', '建设工程', '企业采购']

urllib = {
    "张家口":
        {
            '政府采购': 'http://hb.zcjb.com.cn/cms/channel/zfcggg/index.htm',
            "建设工程": "http://hb.zcjb.com.cn/cms/channel/jsgcgg/index.htm",
            '企业采购': 'http://hb.zcjb.com.cn/cms/channel/qycggg/index.htm'
        }
}


def get_page_number(url):
    # result = requests.request("get", url)
    # soup = BeautifulSoup(result.content, 'html.parser')
    # text = soup.find("div", class_="pages").find_all("span")[-1].text
    # allpage = int(text)
    return 3


def get_all(city, ac=""):
    base_url_dict = urllib[city]
    # db
    db = getdb()
    newlist = []
    # 逐类爬取
    for t in typelist:
        # 获取有多少页
        base_url = base_url_dict[t]
        page_num = get_page_number(base_url)
        # 逐页爬取
        for i in range(page_num):
            chongfu = False
            trycount = 0
            maxtry = 5
            while True:
                try:
                    print("zcjb:尝试获取第%s页的数据"%(i+1))
                    url = base_url + "?pageNo=%s&city=130700&bidType=&timeType="%(i+1)
                    result = requests.request("get", url)
                    soup = BeautifulSoup(result.content, 'html.parser')
                    a = soup.find("div", class_="infolist-main bidlist").find_all("a")
                    for r in a:
                        href = "http://hb.zcjb.com.cn" + r['href'].replace("\n", "").replace("\t", "")
                        name = r['title'].strip()
                        time_all = r.em.text.strip().split("-")
                        time_year = int(time_all[0].strip())
                        time_month = int(time_all[1].strip())
                        time_day = int(time_all[2].strip())
                        area = r.span.span.find_all('span')[1].text.strip()

                        # dbresult = db.count_documents({"source": "zcjb", "href":href})
                        dbresult = db.count_documents({"name": name})
                        if dbresult==0:
                            d = {
                                "name": name,
                                "href": href,
                                "date_y": time_year,
                                "date_m": time_month,
                                "date_d": time_day,
                                "area": area,
                                "source": "zcjb",
                                "city": city
                            }
                            db.insert_one(d)
                            newlist.append(d)
                        else:
                            if db.count_documents({"source": "zcjb", "href":href}):
                                continue
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
                        db.db.close()
                        return "ERROR!"
                    time.sleep(100)
            if chongfu:
                break
    db.db.close()
    return newlist


if __name__ == "__main__":
    get_all("张家口")
    # get_page_number('http://hb.zcjb.com.cn/cms/channel/zfcggg/index.htm')
