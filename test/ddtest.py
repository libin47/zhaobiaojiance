import requests
import json
text = """
![](http://image.wind-watcher.cn/5f76064b8ba71bda4613a17b40a190fd)
# 一级标题
## 二级标题
- 第一项巴拉巴拉巴拉八零八零八    
- 第二项巴拉巴拉巴拉巴拉巴拉巴拉巴拉巴拉巴拉巴拉巴拉巴拉     
啊啊啊啊啊啊啊啊啊啊   
> A man who stands for nothing will fall for anything.
**bold**
*italic*
"""

ddurl_main = "https://oapi.dingtalk.com/robot/send?access_token=fdec336d85e1e9f8e88f0ed22afa6acc28978d2bd6208208ff87841edfa28534"

data = {
    "msgtype": "markdown",
    "markdown": {
        "title": "测试",
        "text": text
    }}
r = requests.post(url=ddurl_main,
                  data=json.dumps(data),
                  headers={'content-type': 'application/json'})

print(r)