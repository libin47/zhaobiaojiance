from dbbase import DB_ZB, DB_Log
from DrissionPage import SessionPage, Chromium, ChromiumOptions
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json


source = "大唐商务"
craw_type = "招标"
main_url = "https://www.cdt-ec.com/home/"
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
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值



def _check_exist(db:DB_ZB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

co = ChromiumOptions()
co.headless()
async def _get_data(db):
    browser = Chromium(co)
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    try:
        tab = browser.new_tab(url=main_url)
        await asyncio.sleep(5)
        tab.ele("text:公告公示").hover()
        await asyncio.sleep(1)
        tab.ele("text:招标公告").click()
        await asyncio.sleep(3)
        tab = browser.latest_tab
        tab.ele("#title").input(city_cfg)
        tab.ele("@class=layui-btn layui-btn-primary").click()
        await asyncio.sleep(1)
        tab = browser.latest_tab
        table = tab.ele("tag:tbody")
        trs = table.eles("tag:tr")
        for tr in trs:
            td1 = tr.eles("tag:td")[0]
            td2 = tr.eles("tag:td")[1]
            href = td1.ele("tag:a").link
            title = td1.ele("tag:a").text
            zbbm_list = td1.eles("tag:li")[0].text.split("：")
            zbbm = zbbm_list[1] if len(zbbm_list)>1 and zbbm_list[0]=="招标编码" else ""
            zbdw_list = td1.eles("tag:li")[1].text.split(":")
            zbdw = zbdw_list[1] if len(zbdw_list)>1 and zbdw_list[0]=="招标单位" else ""
            date = datetime.datetime.strptime(td2.text, '%Y-%m-%d %H:%M:%S')
            _ce = _check_exist(db, {"source": source, "href": href})
            if breaker.check(_ce):
                break
            elif _ce:
                continue
            d = {
                "href": href,
                "title": title,
                "name": title,
                "date": clear_date(date),
                "code":zbbm,
                "city": city_cfg,
                "people": zbdw,
                "source": source,
                "source_base": source,
            }
            data.append(d)
    except:
        traceback.print_exc()
    browser.quit()
    return data



async def get_all():
    print("【招标公告-%s】"%source)
    url = main_url
    with DB_ZB() as db:
        data = []
        trycount = 0
        while trycount<MAX_TRY:
            try:
                data = await _get_data(db)
                break
            except Exception as e:
                with DB_Log() as error_db:
                    error_data = {
                        "log_time": datetime.datetime.now(),
                        "source": source,
                        "craw_type": craw_type,
                        "craw_url": url,
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
    bglist = asyncio.run(get_all())
    print(bglist)





















