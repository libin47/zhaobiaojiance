import craw.yixiang.caigouwang_yx

import asyncio

async def get_yixiang():
    # 河北政府采购网
    await craw.yixiang.caigouwang_yx.get_all()

