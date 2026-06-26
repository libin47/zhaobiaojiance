import time
import requests
import json
import sys
from config import keyword,ddurl_main,ddurl_debug
import craw
from openai import OpenAI
from config import openai_url, openai_key, openai_pmt, openai_model

client = OpenAI(api_key=openai_key, base_url=openai_url)


area_list = ["宣化", "下花园", "万全", "崇礼", "张北", "康保", "沽源", "尚义", "蔚县", "阳原", "怀安", "怀来", "涿鹿", "赤城"]

def clear_area(result):
    rl = []
    for a in area_list:
        rl.append("## 【%s】    \n" % a)
    rl.append("## 【其他】    \n")
    rlbool = [False for _ in range(len(rl))]
    for r in result:
        find = False
        for i in range(len(area_list)):
            if area_list[i] in r['name']:
                rl[i] += get_md_by_ai(r) + "[%s](%s)    \n" % (r['name'], r['href'])
                rlbool[i] = True
                find = True
        if not find:
            rl[-1] += get_md_by_ai(r) + "[%s](%s)    \n" % (r['name'], r['href'])
            rlbool[-1] = True
    resultnew = []
    for i in range(len(rlbool)):
        if rlbool[i]:
            resultnew.append(rl[i])
    result = "    \n".join(resultnew)
    return result


def sendmsg(r, name):
    if len(r)>0:
        result = clear_area(r)
        if name=="招标新增":
            # result = "![](http://image.wind-watcher.cn/5f76064b8ba71bda4613a17b40a190fd)\n" + result
            result = "# 【%s】    \n" % name + result
        else:
            result = "# 【%s】    \n"%name + result
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": name,
                "text": result
            }}
        data_json = json.dumps(data)
        # 如果字数过长分成两次发送
        if sys.getsizeof(data_json) > 19900:
            index = len(r)//2
            print("字数过长，分成两次发送！%s+%s"%(index, len(r)-index))
            sendmsg(r[:index], name)
            sendmsg(r[index:], name)
            return
        # 否则正常一次发
        else:
            r = requests.post(url=ddurl_main,
                          data=data_json,
                          headers={'content-type': 'application/json'})
            print(r)
    return


def senddebug(result, name):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": name,
            "text": "# 【%s】    \n"%name + result
        }}
    requests.post(url=ddurl_debug,
                  data=json.dumps(data),
                  headers={'content-type': 'application/json'})
    return


def get_md(d):
    r = "- [%s]"%(d['date'].strftime("%Y-%m-%d"))
    for k in keyword:
        if k in d['name']:
            r = "- %s👇<font color='Red'>请重点关注</font>👇    \n"%r
            break
    return r

def get_md_by_ai(d):
    try:
        r = "- [%s]" % (d['date'].strftime("%Y-%m-%d"))

        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": openai_pmt},
                {"role": "user", "content": d['name']}
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        if response.choices[0].message.content == '是':
            r = "- %s👇<font color='Red'>请重点关注</font>👇    \n" % r
    except:
        r = get_md(d)
    return r


def update2str(result, name):
    r = []
    debug = ""
    if type(result)==list and len(result)>0:
        # r += "### " + name + "    \n"
        # for i in range(len(result)):
        #     r += "%s、%s [%s](%s)    \n"%(i + 1, get_md(result[i]), result[i]['name'], result[i]['href'])
        # r += '    \n'
        r = result
        debug = name + ":" + str(len(result)) + "条    \n"
    elif type(result) != list:
        debug = name + ":" + "程序错误"
    return r, debug


def get_zb(city):
    result, debug = [], []
    result.append(update2str(craw.zhaobiao.caigouwang.get_all(city), "河北政府采购网"))
    result.append(update2str(craw.zhaobiao.gongongfuwu.get_all(city), "河北招标投标公共服务平台"))
    result.append(update2str(craw.zhaobiao.zhaobiaotong.get_all(city), "招标通"))
    result.append(update2str(craw.zhaobiao.zhaocaijinbao.get_all(city), "招采进宝"))
    result.append(update2str(craw.zhaobiao.datang.get_all(city), "大唐商务平台"))

    mes, debug = [], []
    for i in range(len(result)):
        mes.extend((result[i][0]))
        debug.append((result[i][1]))
    debug = "".join(debug)
    sendmsg(mes, "招标新增")
    senddebug(debug, "招标新增")


def get_yx(city):
    a = craw.yixiang.caigouwang_yx.get_all(city)
    mes, debug = update2str(a, "新增意向[河北政府采购网]")
    sendmsg(mes, "意向新增")
    senddebug(debug, "意向新增")


def get_zb_bg(city):
    result, debug = [], []
    result.append(update2str(craw.biangeng.caigouwang_bg.get_all(city), "河北政府采购网"))
    result.append(update2str(craw.biangeng.gongongfuwu_bg.get_all(city), "河北招标投标公共服务平台"))
    result.append(update2str(craw.biangeng.zhaocaijinbao_bg.get_all(city), "招采进宝"))

    mes, debug = [], []
    for i in range(len(result)):
        mes.extend((result[i][0]))
        debug.append((result[i][1]))
    debug = "".join(debug)
    sendmsg(mes, "招标变更")
    senddebug(debug, "招标变更")

def get_yx_bg(city):
    a = craw.yxbiangeng.caigouwang_yxbg.get_all(city)
    mes, debug = update2str(a, "意向变更[河北政府采购网]")
    sendmsg(mes, "意向变更")
    senddebug(debug, "意向变更")


def crawmain(city):
    get_yx(city)
    print(time.asctime(), ":意向complete")
    time.sleep(120)

    get_yx_bg(city)
    print(time.asctime(), ":意向变更complete")
    time.sleep(120)

    get_zb(city)
    print(time.asctime(), ":招标公告complete")

    get_zb_bg(city)
    print(time.asctime(), ":招标公告complete")

    print(time.asctime(), ":等待下次执行")

if __name__ == "__main__":
    crawmain("张家口")