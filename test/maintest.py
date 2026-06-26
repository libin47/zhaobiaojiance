import asyncio
import inspect

def craw():
    print("爬取数据")
    return "爬取数据完成"

def send():
    print("发送数据")
    return "发送数据完成"

async def _craw_loop():
    result = craw()
    await asyncio.sleep(2)
    await _craw_loop()

async def _send_loop():
    result = send()
    await asyncio.sleep(3)
    await _send_loop()

async def _send_time(i):
    print(i)
    await asyncio.sleep(1)
    await _send_time(i+1)

async def main():
    await asyncio.gather(_craw_loop(), _send_loop(), _send_time(1))

asyncio.run(main())

