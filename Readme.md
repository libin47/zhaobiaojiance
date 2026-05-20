
# 安装依赖
requirement.txt里面可能不全，运行报错就装什么依赖吧

# 配置文件
复制 config_bak.py 为 config.py


# 网站数据情况
| 网站           | 地址                                    | 招标    | 意向    | 招标变更  | 意向变更  | 中标    |
|--------------|---------------------------------------|-------|-------|-------|-------|-------|
| 河北政府采购网      | http://www.ccgp-hebei.gov.cn/zjk/zjk/ | √     | √     | √     | √     | √     |
| 招标通          | http://www.hebztb.com                 | √     | ×     | 没区分地市 | ×     | 没区分地市 |
| 招采进宝河北专区     | http://hb.zcjb.com.cn                 | √     | ×     | √     | ×     | √     |
| 河北招标投标公共服务平台 | http://www.hebeieb.com                | √     | √     | √     | √     | √     |
| 大唐商务         | https://www.cdt-ec.com/               | 没区分地市 | 没区分地市 | 没区分地市 | 没区分地市 | 没区分地市 |


# 已完成情况
| 网站           | 地址                                    | 招标 | 意向 | 招标变更 | 意向变更 | 中标 |
|--------------|---------------------------------------|----|----|------|------|----|
| 河北政府采购网      | http://www.ccgp-hebei.gov.cn/zjk/zjk/ |    | √  |      |      |    |
| 招标通          | http://www.hebztb.com                 |    | ×  |      | ×    |    |
| 招采进宝河北专区     | http://hb.zcjb.com.cn                 |    | ×  |      | ×    |    |
| 河北招标投标公共服务平台 | http://www.hebeieb.com                |    |    |      |      |    |
| 大唐商务         | https://www.cdt-ec.com/               |    |    |      |      |    |




# 其他网站
云采供(没啥数据)
http://hbzjk.86ztb.com


河北省公共资源交易服务平台张家口电子交易系统 
http://ggzy.hebei.gov.cn/hbggfwpt/
http://ggzy.hebei.gov.cn/hbjyzx/

招采云
http://www.zcbidding.com/

惠招标
https://www.hbidding.com/

E招冀成
http://www.hebeibidding.com/

# 文件
- 根目录/
  - bak/ 之前旧的文件备份
  - craw/ 爬取程序主程序，具体涵盖的网站见上
    - biangeng/ 招标变更爬取程序
    - yixiang/ 招标意向爬取程序
    - yxbiangeng/ 招标意向变更爬取程序
    - zhaobiao/ 招标爬取程序
  - dbbase/ 数据库配置目录，试用sqllite
  - utils/ 工具，没用起来
  - config.py   环境配置
  - main.py     程序入口
  - maintest.py 测试程序入口，多线程+爬取发送分离的方式
  - craw.py     主要功能运行程序入口及钉钉发送
  - sqlite.db   数据库文件

# 说明
- 参考 craw/yixiang/caigouwang_yx.py编写其他网站/类型的爬取程序
- craw/目录下每个网站/类型爬取程序需包含get_all() 函数，且为异步函数
- 请勿使用time.sleep()，使用asyncio.sleep()代替
- 数据库文件可以用SQLiteStudio打开