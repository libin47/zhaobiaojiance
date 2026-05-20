from bak.database import getdb
import requests
from bs4 import BeautifulSoup
import time
import traceback
from config import header

url = "http://www.hebeieb.com/tender/xxgk/zbgg.do"
url_base = "http://www.hebeieb.com"
maxtry = 3
source = "hebeizt"
data = {
    "page": 0,
    "TimeStr": "",
    "allDq": 130700,
    "allHy": "reset1",
    "AllPtName": "",
    "KeyStr": "",
    "KeyType": "ggname"
}



max_page_number = 3


def get_all(city, ac=""):
    db = getdb()
    newlist = []
    chongfu = False
    for i in range(max_page_number):
        while True:
            trycount = 0
            try:
                data["page"] = i
                result = requests.request("post", url, data=data, headers=header)
                soup = BeautifulSoup(result.content, 'html.parser')

                publicont = soup.find_all("div", class_="publicont")
                for j in range(len(publicont)):
                    title = publicont[j].find("a").get("title")
                    href = url_base + publicont[j].find("a").get("href")
                    date = publicont[j].find("span", class_="span_o").text
                    date_y, date_m, date_d = date.split("-")[:3]
                    area = publicont[j].find("span", class_="span_on").text.replace("[", "").replace("]", "").split("-")[-1]

                    # dbresult = db.count_documents({"source": source, "href":href})
                    dbresult = db.count_documents({"name": title})
                    if dbresult==0:
                        d = {
                            "name": title,
                            "href": href,
                            "date_y": date_y,
                            "date_m": date_m,
                            "date_d": date_d,
                            "area": area,
                            "source": source,
                            "city": city
                        }
                        db.insert_one(d)
                        newlist.append(d)
                    else:
                        if db.count_documents({"source": source, "href":href})==0:
                            continue
                        else:
                            print("河北招投标：遇到重复数据")
                            chongfu = True
                            break
                time.sleep(15)
                break
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                trycount += 1
                if trycount > maxtry:
                    db.db.close()
                    return "ERROR!"
                else:
                    time.sleep(50)
        if chongfu:
            break
    db.db.close()
    return newlist
