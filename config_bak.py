# 环境设置
# env = "master"
env = "dev"
city = "张家口"

# 强调的关键词
keyword = ["数字", "信息", "平台", "低空"]


# 钉钉机器人
if env=="master":
    ddurl_main = ""
    ddurl_debug = ""
else:
    ddurl_main = ""
    ddurl_debug = ""


# 请求头
header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "yunsuo_session_verify=c36b1e82f4969a52767d7b3763380253",
    "If-Modified-Since": "Mon, 14 Nov 2022 07:46:44 GMT",
    "If-None-Match": "e58b-5ed6970e4235d",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"
}
openai_enable = False
openai_url = "https://api.siliconflow.cn/v1"
openai_key = ""
openai_model = "deepseek-ai/DeepSeek-V3"
openai_pmt = "我公司创新业务涉及各种软件平台、系统建设、智慧城市等，不涉及纯硬件设备，请判断以下内容是否与我公司业务相关，请确保输出内容只有一个字：【是】 或者 【否】"