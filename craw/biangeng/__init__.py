import craw.biangeng.caigouwang_bg
import craw.biangeng.gongongfuwu_bg
import asyncio

async def get_biangeng():
    # 河北政府采购网
    await craw.biangeng.caigouwang_bg.get_all()
    await craw.biangeng.gongongfuwu_bg.get_all()
