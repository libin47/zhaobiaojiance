from dbbase import DB_YX, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker
import asyncio
import traceback
import random

source = "河北政府采购网"
craw_type = "意向"
urllib = {
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
            return title, pltime, money

    return "", "", ""


def _get_page_number(url):
    return 1


async def _get_data(db, page:int, area:str='市'):
    page_session = SessionPage()
    print("[招标意向-河北政府采购网-%s级数据-Page:%s]"%(area, page))
    # 获取具体的数据
    if area == '市':
        if page > 0:
            url = urllib[city_cfg] + "index_%s.html" % page
        else:
            url = urllib[city_cfg] + "index.html"
    elif area == '县':
        if page > 0:
            url = urllib[city_cfg] + "index_1048_%s.html" % page
        else:
            url = urllib[city_cfg] + "index_1048.html"
    else:
        print("只能是市或者县")
        return
    page_session.get(url)
    items = page_session.eles('.list-item-content')
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in items:
        href = item.ele('tag:a').link # 获取具体链接
        title = item.ele('tag:a').text
        dateraw = item.ele('@data-label:发布时间：').text
        date = datetime.datetime.strptime(dateraw, '%Y-%m-%d')
        people = item.ele('@data-label:采购人：').text
        name, plan_time, plan_money = _get_data_info(href)
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
        if breaker.check(_check_exist(db, d)):
            break
        data.append(d)
        await asyncio.sleep(random.uniform(1.5, 3.5))
    return data




async def get_all():
    # 定义获取所有数据的主函数
    base_url = urllib[city_cfg]  # 从配置中获取基础URL，这里city_cfg应该是某个配置项
    print("【招标意向-河北政府采购网】")  # 打印网站标题信息
    page_num = _get_page_number(base_url)  # 获取总页数
    # 获取所有数据
    with DB_YX() as db:
        data = []
        for i in range(page_num):  # 遍历每一页
            for a in ["市", "县"]:  # 遍历市和县两个级别
                trycount = 0
                while trycount<MAX_TRY:
                    try:
                        sub_data = await _get_data(db, i, a)
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
    print(bglist)
