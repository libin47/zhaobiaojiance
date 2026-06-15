import craw.zhongbiao.河北政府采购网
import asyncio

async def get_zhongbiao():
    # 河北政府采购网
    await craw.zhongbiao.河北政府采购网.get_all()
