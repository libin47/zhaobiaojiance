import craw.zhaobiao.河北政府采购网
import craw.zhaobiao.CEC电子采购平台
import craw.zhaobiao.河北招标投标公共服务平台
import craw.zhaobiao.招标通
import craw.zhaobiao.招采进宝
import craw.zhaobiao.易联供应链平台
import craw.zhaobiao.雄安新区公共资源交易服务平台
import craw.zhaobiao.中国雄安集团电子招标采购平台
import craw.zhaobiao.大唐商务
import craw.zhaobiao.河北公共资源交易服务平台
import asyncio

async def get_zhaobiao():
    await 河北政府采购网.get_all()
    await CEC电子采购平台.get_all()
    await 河北招标投标公共服务平台.get_all()
    await 招标通.get_all()
    await 招采进宝.get_all()
    await 易联供应链平台.get_all()
    await 雄安新区公共资源交易服务平台.get_all()
    await 中国雄安集团电子招标采购平台.get_all()
    await 大唐商务.get_all()
    await 河北公共资源交易服务平台.get_all()
