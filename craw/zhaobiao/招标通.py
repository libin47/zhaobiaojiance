from dbbase import DB_ZB, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json


source = "招标通"
craw_type = "招标"
urllib = "https://www.hebztb.com/zbxhcms/api/directive/contentList?count=10&startPublishDate=2001-09-30&signDate=&precise="
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值
arealib = {
    "张家口":"%E5%BC%A0%E5%AE%B6%E5%8F%A3%E5%B8%82",
    "保定": "%E4%BF%9D%E5%AE%9A%E5%B8%82"
}
typelib = {
    "招标": "88",
    "变更": "89"
}


def _check_exist(db:DB_ZB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前三页
    return 3

async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标公告-招标通-Page:%s]"%(page))
    # 获取具体的数据
    if city_cfg in arealib.keys():
        url = urllib + "&area=" + arealib[city_cfg]
    else:
        url = urllib + "&blurSearch=" + arealib[city_cfg]
    url = url + "&pageIndex=" + str(page)
    url = url + "&categoryId=" + typelib[craw_type]
    page_session.get(url)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['page']['list']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        href = item['url'] # 获取具体链接
        title = item['title']
        date = datetime.datetime.fromtimestamp(item['publishDate'] / 1000)

        name = item['title']
        city = city_cfg
        purchaseName = ""
        address = ""
        code = ""
        people = ""
        classify = ""

        if item['blurSearch'] and len(item['blurSearch'].split('{'))>1:
            blurSearch = json.loads('{' + item['blurSearch'].split('{')[1])
            address = blurSearch['buyersLinkerAddress'] if 'buyersLinkerAddress' in blurSearch.keys() else ""
            code = blurSearch['tenderno'] if 'tenderno' in blurSearch.keys() else ""
            people = blurSearch['buyersName'] if 'buyersName' in blurSearch.keys() else ""
            classify = blurSearch['projectIndustryName'] if 'projectIndustryName' in blurSearch.keys() else ""
            purchaseName = blurSearch['tendermethod'] if 'tendermethod' in blurSearch.keys() else ""
        area = get_area_byname(title+address)
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
            "code": code,
            "city": city,
            "area": area,
            "address": address,
            "classify": classify,
            "purchaseName": purchaseName,
            "people": people,
            "source": source,
            "source_base": source,
            "send": False
        }
        data.append(d)
    return data, "完成"


async def get_all():
    base_url = urllib
    print("【招标公告-招标通】")
    # 获取有多少页
    page_num = _get_page_number(base_url)
    with DB_ZB() as db:
        data = []
        status = ""
        for i in range(page_num):  # 遍历每一页
            await asyncio.sleep(random.uniform(1.5, 3.5))
            trycount = 0
            while trycount<MAX_TRY:
                try:
                    sub_data, status = await _get_data(db, i+1)
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





















