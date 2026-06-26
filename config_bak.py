# 环境设置，线上改成master
# env = "master"
env = "dev"
# 城市，不同网站的爬取策略有所差异，除修改这里之外，craw下的文件大多也需要修改其相关url或参数
city = "张家口"

# 钉钉webhook机器人url，debug是发送日志和错误日志的，main是大群的
if env=="master":
    ddurl_main = ""
    ddurl_debug = ""
else:
    ddurl_main = ""
    ddurl_debug = ""

# 启动程序时是否发送
send_when_start = True
# 是否使用大模型判别为需关注项目
openai_enable = False
# 不用大模型时所匹配的关键词
keyword = ["数字", "信息", "平台", "低空"]
# 大模型配置
openai_url = "https://api.siliconflow.cn/v1"
openai_key = ""
openai_model = "deepseek-ai/DeepSeek-V3"
openai_pmt = "我公司创新业务涉及各种软件平台、系统建设、智慧城市等，不涉及纯硬件设备，请判断以下内容是否与我公司业务相关，请确保输出内容只有一个字：【是】 或者 【否】"