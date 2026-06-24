from dbbase import DB_ZB, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json

# TODO
source = "河北公共资源交易服务平台"
craw_type = "招标"
# https://szj.hebei.gov.cn/hbggfwpt/jydt/salesPlat.html
urllib = "https://szj.hebei.gov.cn/inteligentsearchnew/rest/esinteligentsearch/getFullTextDataNew"
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值

datalib = {
    "张家口": {"token":"","pn":0,"rn":10,"sdt":"","edt":"","wd":" ","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\"webdate\":0}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","equal":"003","notEqual":None,"equalList":None,"notEqualList":None,"isLike":True,"likeType":2},{"fieldName":"infoc","equal":"1307","notEqual":None,"equalList":None,"notEqualList":None,"isLike":True,"likeType":2}],"time":None,"highlights":"title","statistics":None,"unionCondition":None,"accuracy":"","noParticiple":"0","searchRange":None,"isBusiness":"1"},
    "雄安": {"token":"","pn":0,"rn":10,"sdt":"","edt":"","wd":" ","inc_wd":"","exc_wd":"","fields":"title","cnum":"001","sort":"{\"webdate\":0}","ssort":"title","cl":200,"terminal":"","condition":[{"fieldName":"categorynum","equal":"003","notEqual":None,"equalList":None,"notEqualList":None,"isLike":True,"likeType":2},{"fieldName":"infoc","equal":"133100","notEqual":None,"equalList":None,"notEqualList":None,"isLike":True,"likeType":2}],"time":None,"highlights":"title","statistics":None,"unionCondition":None,"accuracy":"","noParticiple":"0","searchRange":None,"isBusiness":"1"},

}

def _check_exist(db:DB_ZB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前6页
    return 8

async def _get_data(db, page:int):
    page_session = SessionPage()
    print("[招标公告-%s-Page:%s]"%(source, page))
    # 获取具体的数据
    url = urllib
    pdata = datalib[city_cfg].copy()
    pdata["pn"] = str(int(page*10))
    page_session.post(url, json=pdata)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['result']['records']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        purchaseName = item["categoryname"]
        if "招标" not in purchaseName and "资审" not in purchaseName and "采购" not in purchaseName: # 只获取招标公告
            continue
        href = "https://szj.hebei.gov.cn/hbggfwpt%s"%item['linkurl'] # 获取具体链接
        title = item['titlenew']
        date = datetime.datetime.strptime(item['infodate'], '%Y-%m-%d %H:%M:%S')
        name = item['title']
        city = city_cfg
        area = get_area_byname(title+item["infod"])

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
    base_url = urllib
    print("【招标公告-%s】"%source)
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





















