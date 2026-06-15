import craw.yxbiangeng.caigouwang_yxbg
import asyncio

async def get_yixiang_bg():
    # 河北政府采购网
    await craw.yxbiangeng.caigouwang_yxbg.get_all()
