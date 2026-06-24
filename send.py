import time
import requests
import json
from config import keyword,ddurl_main,ddurl_debug, city
from openai import OpenAI
from config import openai_url, openai_key, openai_pmt, openai_model, openai_enable, send_when_start

import asyncio
from dbbase import DB_ZhongB, DB_Log, DB_ZB, DB_ZBBG, DB_YX, DB_YXBG
from sqlalchemy import inspect

if openai_enable:
    client = OpenAI(api_key=openai_key, base_url=openai_url)

def model_to_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }

def get_data(type, send=False):
    if type == "招标新增":
        DB = DB_ZB
    elif type == "招标变更":
        DB = DB_ZBBG
    elif type == "意向新增":
        DB = DB_YX
    elif type == "意向变更":
        DB = DB_YXBG
    elif type == "中标":
        DB = DB_ZhongB
    elif type == "日志":
        DB = DB_Log
    else:
        return []
    with DB() as db:
        result = db.find_no_send(city)
        result = [model_to_dict(r) for r in result]
        db.batch_update_send_true([r["id"] for r in result])
    return result



def _is_attention(name):
    for k in keyword:
        if k in name:
            return True
    return False

def _is_attention_ai(name):
    if openai_enable:
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": openai_pmt},
                    {"role": "user", "content": name}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            if response.choices[0].message.content == '是':
                return True
            else:
                return False
        except:
            return _is_attention(name)
    else:
        return _is_attention(name)


class SendMd(object):
    def __init__(self, result, type):
        self.type = type
        self.adds = []
        self.result = {}
        self._clear_area(result)
        self.add_now = ""
        self.send_now = ""

    def _clear_area(self, result):
        for r in result:
            if r["area"]:
                if r["area"] not in self.adds:
                    self.adds.append(r["area"])
                if r["area"] not in self.result.keys():
                    self.result[r["area"]] = [r]
                else:
                    self.result[r["area"]].append(r)
            else:
                if "其他" not in self.adds:
                    self.adds.append("其他")
                if "其他" not in self.result.keys():
                    self.result["其他"] = [r]
                else:
                    self.result["其他"].append(r)

    def _send_once(self):
        # 发送
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": self.type,
                "text": self.send_now
            }}
        data_json = json.dumps(data)
        r = requests.post(url=ddurl_main,
                      data=data_json,
                      headers={'content-type': 'application/json'})
        # clear
        self.add_now = ""
        self.send_now = ""

    def _build_once(self, area, r):
        if len(self.send_now) == 0:
            self.send_now = "# 【%s】    \n" % self.type
        if area!= self.add_now:
            self.send_now = self.send_now + "## 【%s】    \n" % area
            self.add_now = area
        if _is_attention_ai(r["name"]):
            self.send_now += "- [%s]👇<font color='Red'>请重点关注</font>👇    \n [%s](%s)    \n" % (r['date'].strftime("%Y-%m-%d"), r['name'] if r['name'].strip() else r['title'], r['href'])
        else:
            self.send_now += "- [%s][%s](%s)    \n" % (r['date'].strftime("%Y-%m-%d"), r['name'] if r['name'].strip() else r['title'], r['href'])
        if len(self.send_now) > 15000:
            self._send_once()


    def send(self):
        for a in self.adds:
            for r in self.result[a]:
                self._build_once(a, r)
        if len(self.send_now) > 0:
            self._send_once()


class SendLog(object):
    def __init__(self, result, type):
        self.type = type
        self.result = {}
        self._clear_source(result)

    def _clear_source(self, result):
        for r in result:
            if r["source"] not in self.result.keys():
                self.result[r["source"]] = [r]
            else:
                self.result[r["source"]].append(r)


    def send(self):
        raw = "# 【%s】    \n" % self.type
        for k in self.result.keys():
            raw = raw + "%s: %s条     \n "%(k, len(self.result[k]))
        # 发送
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": self.type,
                "text": raw
            }}
        data_json = json.dumps(data)
        r = requests.post(url=ddurl_debug,
                      data=data_json,
                      headers={'content-type': 'application/json'})


class SendError(object):
    def __init__(self, result):
        self.result = {}
        self._clear_source_type(result)

    def _clear_source_type(self, result):
        result_source = {}
        for r in result:
            if r["source"] not in result_source.keys():
                result_source[r["source"]] = [r]
            else:
                result_source[r["source"]].append(r)
        for s in result_source.keys():
            result_type = {}
            for r in result_source[s]:
                if r["craw_type"] not in result_type.keys():
                    result_type[r["craw_type"]] = [r]
                else:
                    result_type[r["craw_type"]].append(r)
            self.result[s] = {}
            for t in result_type.keys():
                self.result[s][t] = len(result_type[t])

    def send(self):
        raw = "# 【爬虫错误日志】    \n"
        for k in self.result.keys():
            raw = raw + "【%s】    \n "%k
            for t in self.result[k].keys():
                raw = raw + "%s: %s条     \n "%(t, self.result[k][t])
        # 发送
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "错误日志",
                "text": raw
            }}
        data_json = json.dumps(data)
        r = requests.post(url=ddurl_debug,
                      data=data_json,
                      headers={'content-type': 'application/json'})


def send_sub(type="招标新增"):
    result = get_data(type)
    SendMd(result, type).send()
    SendLog(result, type).send()
    return result


def send_bug(type="日志"):
    result = get_data(type)
    SendError(result).send()
    return result

def _send():
    for type in ["招标新增", "意向新增", "意向变更"]:
        send_sub(type)
    send_bug("日志")



async def send():
    if send_when_start:
        _send()
    while True:
        t = time.localtime()
        if t.tm_hour==8 and t.tm_min==5:
            _send()
            await asyncio.sleep(3600)
        await asyncio.sleep(59)




if __name__ == "__main__":
    # crawmain("张家口")
    send_sub("招标新增")