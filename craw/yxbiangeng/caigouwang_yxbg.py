from dbbase import DB_YXBG
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
urllib = {
    "张家口": "http://www.ccgp-hebei.gov.cn/zjk/zjk/zfcgyxgg/zfcgyx/",
}
urllib_bg = {
    "张家口": "http://www.ccgp-hebei.gov.cn/zjk/zjk/zfcgyxgg/zfcgyxbg/"
}


def get_info(url):
    # 获取具体的意向内容
    result = requests.request("get", url, headers=head)
    soup = BeautifulSoup(result.content, 'html.parser')
    spans = soup.find_all("span", id="intentionAnncInfos")
    if len(spans)>0:
        text = spans[0].text.strip()
        result = text.split("#_@_@")
        title = result[1]
        return title
    else:
        return ""



def get_page_number(url):
    # 意向数据一般很少，只爬第一页就可以了
    return 1


def get_all(city):
    base_url = urllib_bg[city]
    print("招标意向变更爬取……")
    page_num = get_page_number(base_url)
    # db
    db = DB_YXBG()
    newlist = []
    for j in range(2):
        if j==0:
            print("市级数据")
        else:
            print("县级数据")
        for i in range(page_num):
            chongfu = False
            trycount = 0
            maxtry = 5
            while True:
                try:
                    print("采购网:尝试获取第%s页的数据"%(i+1))
                    if j==0:
                        print()
                        if i>0:
                            url = base_url + "index_%s.html"%i
                        else:
                            url = base_url + "index.html"
                    else:
                        if i>0:
                            url = base_url + "index_1048_%s.html"%i
                        else:
                            url = base_url + "index_1048.html"
                    result = requests.request("get", url)
                    soup = BeautifulSoup(result.content, 'html.parser')
                    # table = soup.find_all("table", id="moredingannctable")[0]
                    # name_a = table.find_all("a", class_="a3") # 名字及链接
                    # time_td = table.find_all("td", class_="txt1") # 发布时间和单位
                    # assert len(name_a)==len(time_td) # 二者应该长度相等（都等于50）
                    # for i in range(len(name_a)):
                    #     href = base_url+name_a[i]['href'] # [2:]
                    #     name = get_info(href)
                    #     title = name_a[i].text.strip()
                    #     blist = time_td[i].find_all("span")
                    #     time_all = blist[0].text.strip().split("-")
                    #     time_year = int(time_all[0].strip())
                    #     time_month = int(time_all[1].strip())
                    #     time_day = int(time_all[2].strip())
                    #     area = blist[1].text.strip()
                    result = soup.find_all("div", class_="list-item")
                    for r in result:
                        href = base_url+r.find("a")['href']
                        info = get_info(href)
                        name = info
                        title = base_url+r.find("a")['title']
                        blist = r.find_all("span")
                        time_all = blist[0].text.strip().split("-")
                        time_year = int(time_all[0].strip())
                        time_month = int(time_all[1].strip())
                        time_day = int(time_all[2].strip())
                        area = blist[3].text.strip()
                        if db.count_documents_herf("hbcg", href)==0:
                            d = {
                                "name": name,
                                "href": href,
                                "date": datetime.date(time_year, time_month, time_day),
                                "title": title,
                                "area": area,
                                "source": "hbcg",
                                "people": "",
                                "city": city
                            }
                            db.insert_one(d)
                            newlist.append(d)
                        else:
                            print("采购网:遇到重复数据")
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
    # get_all("张家口")
    bglist = get_all("张家口")
    print(bglist)
