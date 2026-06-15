from dbbase import DB_YX, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json




source = "河北公共资源服务平台"
craw_type = "意向"
urllib = "https://szj.hebei.gov.cn/zbtbfwpt/tender/xxgk/zbjhgg.do"
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值

datalib = {
    "张家口": {
        "TimeStr": "",
        "allDq": "130700",
        "allHy": "reset1",
        "AllPtName": "",
        "KeyType": "ggname",
        "KeyStr": "",
        "page": "0",
    },
    "雄安": {
        "TimeStr": "",
        "allDq": "131400",
        "allHy": "reset1",
        "AllPtName": "",
        "KeyType": "ggname",
        "KeyStr": "",
        "page": "0",
    }
}

def _check_exist(db:DB_YX, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前三页
    return 3

async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标意向-河北公共资源服务平台-Page:%s]"%(page))
    # 获取具体的数据
    url = urllib
    pdata = datalib[city_cfg]
    pdata["page"] = str(page)
    page_session.post(url, data=pdata)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['t']['search_ZbJhGg']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        href = "https://szj.hebei.gov.cn/zbtbfwpt/infogk/detail.do?categoryid=zbjhgg&infoid=%s&bdcodes=%s&laiyuan=%s"%(item['planbulletincode'], item['bmcode'], item['escapesource']) # 获取具体链接
        title = item['bulletinname']
        date = datetime.datetime.strptime(item['bulletinissuetime'], '%Y-%m-%d %H:%M')

        name = item['bulletinname']
        money = ""
        city = city_cfg
        address = item['regioncode']
        people = ""
        classify = item['tenderprojectclassifycode']
        area = get_area_byname(title+address)
        sourcename = item['sourcename'][1:-1]

        _ce = _check_exist(db, {"source":source, "href":href })
        if breaker.check(_ce):
            return data, "重复"
        elif _ce:
            continue

        d = {
            "name": name,
            "href": href,
            "date": clear_date(date),
            "title": title,
            "plan_time": "",
            "plan_money": money,
            "city": city,
            "area": area,
            "classify": classify,
            "people": people,
            "source": source,
            "source_base": sourcename,
            "send": False
        }
        data.append(d)
    return data, "完成"


async def get_all():
    base_url = urllib
    print("【招标意向-河北公共资源服务平台】")
    # 获取有多少页
    page_num = _get_page_number(base_url)
    with DB_YX() as db:
        data = []
        status = ""
        for i in range(page_num):  # 遍历每一页
            await asyncio.sleep(random.uniform(1.5, 3.5))
            trycount = 0
            while trycount<MAX_TRY:
                try:
                    sub_data, status = await _get_data(db, i)
                    data.extend(sub_data)
                    break
                except Exception as e:
                    with DB_Log() as error_db:
                        error_data = {
                            "log_time": datetime.datetime.now(),
                            "source": source,
                            "craw_type": craw_type,
                            "craw_url": urllib,
                            "log_type": "error",
                            "log_text": str(e),
                            "send": False
                        }
                        error_db.insert_one(error_data)
                    traceback.print_exc()
                    trycount += 1
                    await asyncio.sleep(60)
            if status == "重复":
                break
        # 插入数据库
        if len(data) > 0:
            for d in data:
                db.insert_one_check(d)
    return data



if __name__ == "__main__":
    # get_all("张家口")
    bglist = asyncio.run(get_all())
    print(bglist)





















