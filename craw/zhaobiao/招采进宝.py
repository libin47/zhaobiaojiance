from dbbase import DB_ZB, DB_Log
from DrissionPage import SessionPage
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json


typelist = ['政府采购', '建设工程', '企业采购']
categoryIdLib = {
    "建设工程": {
        "招标": "7282520",
        "变更": "7282530",
        "中标候选人公示": "7282540",
        "中标公告": "7282550",
        "其他公告": "7282560"
    },
    "政府采购": {
        "招标": "7282220",
        "变更": "7282230",
        "单一来源公示": "7282240",
        "中标公告": "7282250",
        "其他公告": "7282260"
    },
    "企业采购": {
        "招标": "7282120",
        "变更": "7282130",
        "单一来源公示": "7282140",
        "成交候选人公示": "7282141",
        "中标公告": "7282150",
        "其他公告": "7282160"
    }

}
cityLib = {
    "张家口": "130700",
    "雄安": "131400"
}
postdata = {
        "pageNo": 1,
        "pageSize": 10,
        "dto": {
            "categoryId": "",
            "city": "",
            "publishDate":"",
            "publishEndDate": "",
            "purchaseMode":"",
            "siteId": "728"
        }
    }


source = "招采进宝"
craw_type = "招标"
urllib = "https://hb.zcjb.com.cn/cms/api/dynamicData/queryContentPage"
MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值



def _check_exist(db:DB_ZB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    return 3


async def _get_data(db, page:int, tp:str):
    page_session = SessionPage()
    print("[招标公告-招采进宝-类型:%s-Page:%s]"%(tp, page))
    # 获取具体的数据
    pdata = postdata.copy()
    pdata['dto']['categoryId'] = categoryIdLib[tp][craw_type]
    pdata['dto']['city'] = cityLib[city_cfg]
    pdata['pageNo'] = page
    url = urllib
    post_result = page_session.post(url, json=pdata)
    assert post_result, "post请求失败"
    rdata = json.loads(page_session.raw_data)
    datas = rdata['res']['rows']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    for item in datas:
        name = item['packageName'].strip() if 'packageName' in item.keys() else item['title'].strip()
        href = "https://hb.zcjb.com.cn/cms/hb/webfile/detail/index.html?contentId=" + item['id'] # 获取具体链接
        date = datetime.datetime.strptime(item['publishDate'], '%Y-%m-%d %H:%M:%S')
        title = item['title']
        city = city_cfg
        people = item['tendereeOrgName'] if 'tendereeOrgName' in item.keys() else ""
        area = get_area_byname(title+people)
        purchaseName = item['purchaseName'] if 'tendereeOrgName' in item.keys() else "公开招标"

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
            "people": people,
            "source": source,
            "source_base": source,
            "send": False
        }
        data.append(d)
    return data, "完成"


async def get_all():
    base_url = urllib
    print("【招标公告-招采进宝】")  # 打印网站标题信息
    page_num = _get_page_number(base_url)  # 获取总页数
    # db
    with DB_ZB() as db:
        data = []
        for t in typelist:
            status = ""
            for i in range(page_num):  # 遍历每一页
                await asyncio.sleep(random.uniform(1.5, 3.5))
                trycount = 0
                while trycount<MAX_TRY:
                    try:
                        sub_data, status = await _get_data(db, i+1, t)
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

