from dbbase import DB_ZBBG, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json

source = "河北政府采购网"
craw_type = "变更"
urllib = {
    "张家口": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=gzggAAAS&admindivcode=1307&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page=",
    "雄安": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=gzggAAAS&admindivcode=1399&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page="
}

MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值


def _check_exist(db:DB_ZBBG, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前三页
    return 3


async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标变更-河北政府采购网-Page:%s]"%(page))
    # 获取具体的数据
    url = urllib[city_cfg] + str(page)
    page_session.get(url)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['data']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        href = item['docPubUrl'] # 获取具体链接
        title = item['docTitle']
        date = datetime.datetime.strptime(item['docRelTime'], '%Y/%m/%d %H:%M:%S')

        name = item['docTitle']
        money = ""
        city = city_cfg
        address = item['purchaserAddr']
        people = item['purchaserName']
        area = get_area_byname(title+people+address)

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
            "money": money,
            "city": city,
            "area": area,
            "address": address,
            "people": people,
            "source": source,
            "source_base": source,
            "send": False
        }
        data.append(d)
    return data, "完成"


async def get_all():
    # 定义获取所有数据的主函数
    base_url = urllib[city_cfg]  # 从配置中获取基础URL，这里city_cfg应该是某个配置项
    print("【招标变更-河北政府采购网】")  # 打印网站标题信息
    page_num = _get_page_number(base_url)  # 获取总页数
    # 获取所有数据
    with DB_ZBBG() as db:
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
    bglist = asyncio.run(get_all())
    print(bglist)




















