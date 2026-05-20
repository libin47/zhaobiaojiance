# This is a sample Python script.
from craw_and_send import crawmain
import time


if __name__ == '__main__':
    city = "张家口"
    # 初始化运行
    crawmain(city)
    # 定时执行
    while True:
        t = time.localtime()
        if t.tm_hour==8 and t.tm_min==00:
            crawmain(city)
            time.sleep(36000)
        time.sleep(30)