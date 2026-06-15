from dbbase import DB_ZhongB, DB_Log
from DrissionPage import SessionPage, ChromiumOptions, Chromium
from DrissionPage.errors import JavaScriptError
import datetime
from config import city as city_cfg
from utils.utils import get_area_byname, ContinuousDupBreaker, clear_date
import asyncio
import traceback
import random
import json

source = "河北政府采购网"
craw_type = "结果"
type_list = ["中标", "终止", "单一来源"]
urllib = {
    "中标":{
        "张家口": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=zhbggAAAS&admindivcode=1307&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page=",
        "雄安": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=zhbggAAAS&admindivcode=1399&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page="
    },
    "终止":{
        "张家口": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=fbggAAAS&admindivcode=1307&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page=",
        "雄安": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=fbggAAAS&admindivcode=1399&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page="

    },
    "单一来源":{
        "张家口": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=dylyAAAS&admindivcode=1307&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page=",
        "雄安": "https://www.ccgp-hebei.gov.cn/was5/web/search?&channelid=217003&lanmu=dylyAAAS&admindivcode=1399&purchaseWay=&procurementcode=&agencyfullname=&PurchaserName=&doctitle=&perpage=50&page="
    }
}


MAX_DUP = 5 # 监测重复阈值
MAX_TRY = 3 # 尝试次数阈值
co = ChromiumOptions()
co.headless()

def _check_exist(db:DB_ZhongB, data):
    count = db.count_source_href(data['source'], data['href'])
    return count>0

def _get_page_number(url):
    # 简化处理，只获取前三页
    return 3

def _parseContent(content):
    # 统一分隔符格式
    normalized = content.replace('#@_@', '#_@_@').replace("&quot;", '"').replace("？","")
    # 分离内容和附件
    contentParts = normalized.split('#detail#')
    mainContent = contentParts[0] if contentParts[0] else ''
    packData = []
    if len(contentParts) > 1:
        temp = contentParts[1]
        packDetail = temp.split('#filename#')[0] if temp.split('#filename#')[0] else ""
        if (packDetail):
            packData = packDetail.split('#_@_@')
    return mainContent, packData


def _get_zhongbiao(ann):
    data = ann["bidWinningAnnouncement"]
    mainContent, packData = _parseContent(ann["content"])
    # 新旧版本处理逻辑不同
    if data["ANNCVERSION"] == "V2020":
        if len(packData)<4:
            return [], [], [], [], []
        供应商名称 = packData[3].split('#_#')
        供应商地址 = packData[4].split('#_#')
        中标金额 = packData[10].split('#_#') if len(packData)>10 and packData[10] else []
        标包名称 = packData[27].split('#_#') if len(packData)>27 and packData[27] else []

        types = packData[0].split('#_#')
        itemNames = packData[5].split('#_#')
        # 货物
        货物品牌 = packData[15] if packData[15] else []
        规格型号 = packData[7] if packData[7] else []
        # 工程
        施工范围 = packData[17] if packData[17] else []
        # 服务
        服务标准 = packData[22] if packData[22] else []
        服务范围 = packData[21] if packData[21] else []
        服务要求 = packData[12] if packData[12] else []
        # 服务内容
        服务内容 = ["" for _ in range(len(标包名称))]
        for i in range(len(标包名称)):
            if types[i] == "A":
                服务内容[i] = itemNames[i] + "[货物品牌]:%s"%货物品牌 + "[规格型号]:%s"%规格型号
            elif types[i] == "B":
                服务内容[i] = itemNames[i] + "[施工范围]:%s"%施工范围
            elif types[i] == "C":
                服务内容[i] = itemNames[i] + "[服务标准]:%s"%服务标准 + "[服务范围]:%s"%服务范围 + "[服务要求]:%s"%服务要求
        for i in range(len(types)):
            if types[i] == "A":
                types[i] = "货物"
            elif types[i] == "B":
                types[i] = "工程"
            elif types[i] == "C":
                types[i] = "服务"
        return 标包名称, types, 供应商名称, 供应商地址, 中标金额, 服务内容
    else:
        标包名称 = packData[0].split('#_#')
        供应商名称 = packData[1].split('#_#')
        中标金额 = packData[2].split('#_#')
        供应商地址 = packData[3].split('#_#')
        服务标准 = packData[9].split('#_#') if len(packData)>9 and packData[9] else []
        主要标的名称 = packData[10].split('#_#') if len(packData)>10 and packData[10] else []
        质量标准 = packData[5].split('#_#') if len(packData)>5 and packData[5] else []
        规格型号 = packData[8].split('#_#') if len(packData)>8 and packData[8] else []
        服务内容 = ["" for i in range(len(供应商名称))]

        for i in range(len(供应商名称)):
            if 服务标准 and len(服务标准) == len(供应商名称):
                服务内容[i] = 服务内容[i] + "【服务标准】%s"%服务标准[i]
            if 主要标的名称 and len(主要标的名称) == len(供应商名称):
                服务内容[i] = 服务内容[i] + "【主要标的名称】%s"%主要标的名称[i]
            if 质量标准 and len(质量标准) == len(供应商名称):
                服务内容[i] = 服务内容[i] + "【质量标准】%s"%质量标准[i]
            if 规格型号 and len(规格型号) == len(供应商名称):
                服务内容[i] = 服务内容[i] + "【规格型号】%s"%规格型号[i]
        return 标包名称, ["" for _ in range(len(供应商名称))], 供应商名称, 供应商地址, 中标金额, 服务内容


def _get_zhongbiao_old(page):
    con = page.ele("#con")
    content = con.text
    content = content.replace('#@_@', '#_@_@')
    temp = content.split("#detail#")[1]
    packdetail = temp.split("#filename#")[0]
    pack = packdetail.split("#_@_@")
    annc_version = page.ele("@id=AnncVersion").text
    if annc_version == "V2020":
        供应商名称 = pack[3].split("#_#")
        供应商地址 = pack[4].split("#_#")
        类型 = pack[0].split("#_#")
        中标金额 = pack[10].split("#_#") if len(pack)>10 else []
        标包名称 = pack[5].split("#_#")
        # 货物
        货物名称 = pack[5].split("#_#")
        货物品牌 = pack[15].split("#_#") if len(pack)>15 else []
        规格型号 = pack[7].split("#_#") if len(pack)>7 else []
        # 工程
        施工范围 = pack[17].split("#_#") if len(pack)>17 else []
        # 服务
        服务标准 = pack[22].split("#_#") if len(pack)>22 else []
        服务范围 = pack[21].split("#_#") if len(pack)>21 else []
        服务要求 = pack[12].split("#_#") if len(pack)>12 else []
        服务内容 = ["" for _ in range(len(标包名称))]
        for i in range(len(标包名称)):
            if 类型[i] == "A":
                服务内容[i] = "【货物名称】%s"%货物名称 +"【货物品牌】%s"%货物品牌 + "【规格型号]】%s"%规格型号
            elif 类型[i] == "B":
                服务内容[i] =  "【施工范围】%s"%施工范围
            elif 类型[i] == "C":
                服务内容[i] = "【服务标准】%s"%服务标准 + "【服务范围】%s"%服务范围 + "【服务要求】%s"%服务要求
        for i in range(len(类型)):
            if 类型[i] == "A":
                类型[i] = "货物"
            elif 类型[i] == "B":
                类型[i] = "工程"
            elif 类型[i] == "C":
                类型[i] = "服务"
        return 标包名称, 类型, 供应商名称, 供应商地址, 中标金额, 服务内容
    else:
        if len(pack)<13 and len(pack)>9:
            标包名称 = pack[10].split("#_#")
            类型 = ["" for _ in range(len(标包名称))]
            供应商名称 = pack[1].split("#_#")
            供应商地址 = ["" for _ in range(len(标包名称))]
            中标金额 = pack[2].split("#_#")
            服务标准 = pack[9].split("#_#")
            质量标准 = pack[5].split("#_#")
            规格型号 = pack[8].split("#_#")
            服务内容 = ["" for _ in range(len(标包名称))]
            for i in range(len(标包名称)):
                服务内容[i] = "【服务标准】%s"%服务标准[i] + "【质量标准】%s"%质量标准[i] + "【规格型号】%s"%规格型号[i]
            return 标包名称, 类型, 供应商名称, 供应商地址, 中标金额, 服务内容
        elif len(pack)==9:
            标包名称 = pack[0].split("#_#")
            类型 = ["" for _ in range(len(标包名称))]
            供应商名称 = pack[1].split("#_#")
            供应商地址 = ["" for _ in range(len(标包名称))]
            中标金额 = pack[2].split("#_#")
            质量标准 = pack[5].split("#_#")
            规格型号 = pack[8].split("#_#")
            服务内容 = ["" for _ in range(len(标包名称))]
            for i in range(len(标包名称)):
                服务内容[i] = "【质量标准】%s"%质量标准[i] + "【规格型号】%s"%规格型号[i]
            return 标包名称, 类型, 供应商名称, 供应商地址, 中标金额, 服务内容
        else:
            类型 = pack[0].split("#_#")
            for i in range(len(类型)):
                if 类型[i] == "A":
                    类型[i] = "货物"
                elif 类型[i] == "B":
                    类型[i] = "工程"
                elif 类型[i] == "C":
                    类型[i] = "服务"
            标包名称 = pack[5].split("#_#")
            供应商名称 = pack[3].split("#_#")
            供应商地址 = pack[4].split("#_#")
            标的基本情况 = pack[6].split("#_#")
            规格型号 = pack[7].split("#_#")
            服务要求 = pack[12].split("#_#")
            中标金额 = pack[10].split("#_#")
            服务内容 = ["" for _ in range(len(标包名称))]
            for i in range(len(标包名称)):
                服务内容[i] = 标的基本情况[i] + "【服务要求】%s"%服务要求[i] + "【规格型号】%s"%规格型号[i]
            return 标包名称, 类型, 供应商名称, 供应商地址, 中标金额, 服务内容


async def _get_info(url, page_ss_headless):
    tab = page_ss_headless.get_tab()
    tab.get(url)
    try:
        ann = tab.run_js(script='return announcementData;')
        项目名称 = ann['baseInfo']["projectName"]
        项目编号 = ann['baseInfo']["projectCode"]
        公示类型 = ann['type']
        标包名称, 标包类型, 供应商名称, 供应商地址, 中标金额, 服务内容 = _get_zhongbiao(ann)
    except JavaScriptError:
        await asyncio.sleep(1)
        page = SessionPage()
        page.get(url)
        # infos = page.eles("@@tag()=span@@class=txt7")[-1]
        # 项目名称 = infos.eles("@tag()=span")[3].text
        # 项目编号 = infos.eles("@tag()=span")[1].text
        # 公示类型 = page.ele("@@bgcolor=#bfdff1@@tag()=table").eles("tag:td")[3].text
        标包名称, 标包类型, 供应商名称, 供应商地址, 中标金额, 服务内容 = _get_zhongbiao_old(page)
        项目名称 = 标包名称[0]
        项目编号 = ""
        公示类型 = ""


    data = []
    for i in range(len(标包名称)):
        d = {
            "公示类型": 公示类型,
            "项目名称": 项目名称,
            "项目编号": 项目编号,
            "标包名称": 标包名称[i],
            "标包类型": 标包类型[i],
            "供应商名称": 供应商名称[i],
            "供应商地址": 供应商地址[i],
            "中标金额": 中标金额[i],
            "项目内容": 服务内容[i]
        }
        data.append(d)
    return data


async def _get_data(db, page:int, type:str):
    page_session = SessionPage()
    print("[%s-%s-Page:%s]"%(type, source, page))
    # 获取具体的数据
    url = urllib[type][city_cfg] + str(page)
    page_session.get(url)
    rdata = json.loads(page_session.raw_data)
    datas = rdata['data']
    data = []
    breaker = ContinuousDupBreaker(max_dup=3)
    page_ss_headless = Chromium(co)
    for item in datas:
        href = item['docPubUrl'] # 获取具体链接
        title = item['docTitle']
        date = datetime.datetime.strptime(item['docRelTime'], '%Y/%m/%d %H:%M:%S')
        _ce = _check_exist(db, {"source":source, "href":href })
        if breaker.check(_ce):
            return data, "重复"
        elif _ce:
            continue
        city = city_cfg
        address = item['purchaserAddr']
        people = item['purchaserName']
        area = get_area_byname(title+people+address)
        trycount = 0
        result = []
        while trycount < MAX_TRY:
            try:
                # print("获取：%s"%href)
                result = await _get_info(href, page_ss_headless)
                break
            except Exception as e:
                with DB_Log() as error_db:
                    error_data = {
                        "log_time": datetime.datetime.now(),
                        "source": source,
                        "craw_type": craw_type,
                        "craw_url": href,
                        "log_type": "error",
                        "log_text": str(e),
                        "send": False
                    }
                    error_db.insert_one(error_data)
                traceback.print_exc()
                trycount += 1
                await asyncio.sleep(66)
        for r in result:
            d = {
                "name": r["项目名称"],
                "nameBag": r["标包名称"],
                "href": href,
                "date": clear_date(date),
                "info": r["项目内容"],
                "title": title,
                "code": r["项目编号"],
                "money": r["中标金额"],
                "city": city,
                "area": area,
                "address": address,
                "purchaseName": r["公示类型"],
                "type": r["标包类型"],
                "people": people,
                "candidate": r["供应商名称"],
                "winner": r["供应商名称"],
                "winnerAddress": r["供应商地址"],
                "source": source,
                "source_base": source,
                "send": False
            }
            data.append(d)
        await asyncio.sleep(random.uniform(2.5, 5.5))
    return data, "完成"


async def get_all():
    # 定义获取所有数据的主函数
    print("【招标结果-河北政府采购网】")  # 打印网站标题信息
    page_num = _get_page_number("")  # 获取总页数
    # 获取所有数据
    with DB_ZhongB() as db:
        data = []
        status = ""
        for type in ["中标"]:
            for i in range(page_num):  # 遍历每一页
                await asyncio.sleep(random.uniform(1.5, 3.5))
                trycount = 0
                while trycount<MAX_TRY:
                    try:
                        sub_data, status = await _get_data(db, i+1, type)
                        data.extend(sub_data)
                        break
                    except Exception as e:
                        with DB_Log() as error_db:
                            error_data = {
                                "log_time": datetime.datetime.now(),
                                "source": source,
                                "craw_type": craw_type,
                                "craw_url": urllib[type][city_cfg],
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
    # url = "https://www.ccgp-hebei.gov.cn/zjk/zjk_yy/cggg/zhbggAAAA/202605/t20260513_2364460.html"
    # page_ss_headless = Chromium(co)
    # print(asyncio.run(_get_info(url, page_ss_headless)))



















