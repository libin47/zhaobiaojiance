from bak.database import getdb
import requests
import time
import traceback
import json
from selenium import webdriver
from datetime import datetime

main_url = "https://www.cdt-ec.com/notice/moreController/toMore"
api_url = "https://www.cdt-ec.com/notice/moreController/getList"
detail_url = "https://www.cdt-ec.com/notice/moreController/moreall?id="
postdata = {
    "page": 1,
    "limit": 10,
    "messagetype": 0,
    "pro_bidding_mothod": 0,
    "message_title": "张家口",
    "purchase_type": 0,
    "purchase_unit": "",
    "purchase_unit_agent":  "",
    "message_no":  "",
    "purchase_code":  "",
    "startDate":  "",
    "endDate":  ""
}
head = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "191",
    "Origin": "https://www.cdt-ec.com",
    "Host": "www.cdt-ec.com",
    "Referer": "https://www.cdt-ec.com/notice/webpage/jsp/more.jsp",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua":'"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform":"Windows",
}


def get_cookies():
    try:
        # 初始化浏览器驱动
        driver = webdriver.Edge()
        # 打开网页
        driver.get(main_url)
        time.sleep(5)
        # 获取浏览器Cookies
        cookies = driver.get_cookies()
    except:
        # 尝试Chrome
        driver = webdriver.Chrome()
        driver.get(main_url)
        time.sleep(5)
        cookies = driver.get_cookies()
    call = ""
    for cookie in cookies:
        csub = "%s=%s;"%(cookie["name"], cookie["value"])
        call = call + csub
    # 关闭浏览器
    driver.quit()
    return call

def get_page_number(url):
    return 3


def get_all(city, ac=""):
    # 获取有多少页
    page_num = get_page_number(api_url)
    postdata["message_title"] = city
    head["Cookie"] = get_cookies()
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
                print("大唐集团:尝试获取第%s页的数据"%(i+1))
                postdata["page"] = i+1
                result = requests.post(api_url, data=postdata, headers=head)
                data = json.loads(result.text)
                data = data["data"]
                for i in range(len(data)):
                    href = detail_url + data[i]["id"]
                    name = data[i]["message_title"]

                    publish_time = data[i]["publish_time"]
                    time_date = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')

                    time_year = int(time_date.year)
                    time_month = int(time_date.month)
                    time_day = int(time_date.day)
                    area = ""
                    people = data[i]["bid_tenderer"]

                    dbresult = db.count_documents({"name": name})
                    if dbresult==0:
                        d = {
                            "name": name,
                            "href": href,
                            "date_y": time_year,
                            "date_m": time_month,
                            "date_d": time_day,
                            "area": area,
                            "people": people,
                            "source": "datang",
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents({"source": "datang", "href": href})==0:
                            continue
                        else:
                            print("大唐网:遇到重复数据")
                            chongfu = True
                            break
                time.sleep(10)
                break
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                trycount += 1
                # 更新cookie
                head["Cookie"] = get_cookies()
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





















