from DrissionPage.common import Settings
Settings.set_language('zh_cn')

from craw.yixiang import get_yixiang
from craw.yxbiangeng import get_yixiang_bg
from craw.zhaobiao import get_zhaobiao
from craw.biangeng import get_biangeng
from craw.zhongbiao import get_zhongbiao

import asyncio

# 不搞变更了，无意义
async def craw():
    await asyncio.gather(get_yixiang(), get_yixiang_bg(), get_zhaobiao())
    await asyncio.sleep(120)
    await get_zhongbiao()
    await asyncio.sleep(10800)
    await craw()
