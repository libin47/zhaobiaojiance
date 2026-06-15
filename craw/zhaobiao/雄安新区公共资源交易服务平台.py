from dbbase import DB_ZB, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json
import time


source = "雄安新区公共资源交易服务平台"
craw_type = "招标"
urllib = {
    "政府采购": "https://www.xaprtc.com/queryContent-jyxx.jspx?inDates=&ext=&origin=&channelId=274&projectCode=&approvelArea=&title=",
    "工程建设": "https://www.xaprtc.com/queryContent-jyxx.jspx?inDates=&ext=&origin=&channelId=264&projectCode=&approvelArea=&title="
}
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值

def _check_exist(db:DB_ZB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前三页
    return 3

async def _get_data(db, page:int, key):
    page_session = SessionPage()
    print("[招标公告-%s-Page:%s]"%(source,page))
    # 获取具体的数据
    url = urllib[key]
    if page>1:
        url = url.replace("queryContent", "queryContent_%s"%page)
    page_session.get(url)
    rdata = page_session.ele("@class:sx-lieul").eles("tag:li")
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in rdata:
        href = item.ele("tag:a").link # 获取具体链接
        title = item.ele("tag:a").text.strip()
        date = datetime.datetime.strptime(item.eles("tag:p")[1].text.strip(), '%Y-%m-%d')
        name = title
        purchaseName = item.eles("tag:p")[-1].ele("tag:span").text.split("：")[-1]
        city = city_cfg
        area = get_area_byname(name)
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
            "city": city,
            "area": area,
            "purchaseName": purchaseName,
            "source": source,
            "source_base": source,
            "send": False
        }
        data.append(d)
    return data, "完成"


async def get_all():
    if city_cfg != "雄安":
        return []
    base_url = urllib
    print("【招标公告-%s】"%source)
    # 获取有多少页
    page_num = _get_page_number(base_url)
    with DB_ZB() as db:
        data = []
        for key in urllib.keys():
            status = ""
            for i in range(page_num):  # 遍历每一页
                await asyncio.sleep(random.uniform(1.5, 3.5))
                trycount = 0
                while trycount<MAX_TRY:
                    try:
                        sub_data, status = await _get_data(db, i+1, key)
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





















