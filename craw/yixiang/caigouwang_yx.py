from dbbase import DB_YX, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker
import asyncio
import traceback
import random
import json

source = "河北政府采购网"
craw_type = "意向"
urllib = {
    "张家口": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=zfcgyx&admindivcode=1307&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page=",
    "雄安": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=zfcgyx&admindivcode=1399&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page="
}
urllib_old = {
    "张家口": "http://www.ccgp-hebei.gov.cn/zjk/zjk/zfcgyxgg/zfcgyx/",
}
MAX_DUP = 3 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值


def _check_exist(db:DB_YX, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_data_info(url):
    page_info = SessionPage()
    page_info.get(url)
    table_title = page_info.eles('#intentionAnnc')
    spans_info = page_info.eles('#intentionAnncInfos')

    if len(table_title)>0 and len(spans_info)>0:
        titles = table_title[0].text.split()
        texts = spans_info[0].text.strip().split("#_@_@")[:-1]
        if len(titles) == len(texts):
            subnum = len(texts[0].split('#_#'))
            if subnum == 1:
                title = ""
                money = ""
                pltime = ""
                for i in range(len(texts)):
                    if titles[i] == "采购项目名称":
                        title = texts[i]
                    if titles[i] == "预算金额（万元）":
                        money = texts[i]
                    if titles[i] == "预计采购时间":
                        pltime = texts[i]
                return [[title, pltime, money]]
            else:
                result = []
                for s in range(subnum):
                    title = ""
                    money = ""
                    pltime = ""
                    for i in range(len(texts)):
                        if titles[i] == "采购项目名称":
                            title = texts[i].split('#_#')[s]
                        if titles[i] == "预算金额（万元）":
                            money = texts[i].split('#_#')[s]
                        if titles[i] == "预计采购时间":
                            pltime = texts[i].split('#_#')[s]
                    result.append([title, pltime, money])
                return result

    return [["", "", ""]]


def _get_page_number(url):
    return 1

'''
# 旧版本，数据已不全
async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标意向-河北政府采购网-Page:%s]"%(page))
    # 获取具体的数据
    if page > 0:
        url = urllib[city_cfg] + "index_%s.html" % page
    else:
        url = urllib[city_cfg] + "index.html"
    page_session.get(url)
    items = page_session.eles('.list-item-content')
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in items:
        href = item.ele('tag:a').link # 获取具体链接
        _ce = _check_exist(db, {"source":source, "href":href })
        if breaker.check(_ce):
            return data, "重复"
        elif _ce:
            continue
        title = item.ele('tag:a').text
        dateraw = item.ele('@data-label:发布时间：').text
        date = datetime.datetime.strptime(dateraw, '%Y-%m-%d')
        people = item.ele('@data-label:采购人：').text
        subinfo = _get_data_info(href)
        for sub in subinfo:
            name, plan_time, plan_money = sub
            city = city_cfg
            area = get_area_byname(title+name)
            d = {
                "name": name,
                "href": href,
                "date": date,
                "title": title,
                "plan_time": plan_time,
                "plan_money": plan_money,
                "city": city,
                "area": area,
                "people": people,
                "source": source,
                "source_base": source,
                "send": False
            }
            data.append(d)
        await asyncio.sleep(random.uniform(1.5, 3.5))
    return data, "完成"
'''

async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标意向-河北政府采购网-Page:%s]"%(page))
    # 获取具体的数据
    url = urllib[city_cfg] + str(page)
    page_session.get(url)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['data']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        href = item['docPubUrl'] # 获取具体链接
        _ce = _check_exist(db, {"source":source, "href":href })
        if breaker.check(_ce):
            return data, "重复"
        elif _ce:
            continue
        title = item['docTitle']
        date = datetime.datetime.strptime(item['docRelTime'], '%Y/%m/%d %H:%M:%S')
        people = ''
        # 忽视变更的
        if '变更' in title:
            continue
        subinfo = _get_data_info(href)
        for sub in subinfo:
            name, plan_time, plan_money = sub
            city = city_cfg
            area = get_area_byname(title+name)
            d = {
                "name": name,
                "href": href,
                "date": date,
                "title": title,
                "plan_time": plan_time,
                "plan_money": plan_money,
                "city": city,
                "area": area,
                "people": people,
                "source": source,
                "source_base": source,
                "send": False
            }
            data.append(d)
        await asyncio.sleep(random.uniform(1.5, 3.5))
    return data, "完成"


async def get_all():
    # 定义获取所有数据的主函数
    base_url = urllib[city_cfg]  # 从配置中获取基础URL，这里city_cfg应该是某个配置项
    print("【招标意向-河北政府采购网】")  # 打印网站标题信息
    page_num = _get_page_number(base_url)  # 获取总页数
    # 获取所有数据
    with DB_YX() as db:
        data = []
        status = ""
        for i in range(page_num):  # 遍历每一页
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
                            "craw_url": urllib[city_cfg],
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
    # bglist = get_all("张家口")
    # bglist = get_all()
    bglist = asyncio.run(get_all())
    # bglist = _get_data_info("http://www.ccgp-hebei.gov.cn/zjk/zjk_zl/zfcgyxgg/zfcgyx/202605/t20260515_2366107.html")
    print(bglist)
