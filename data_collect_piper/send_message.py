import os
import requests
import re
import sys

def sc_send(sendkey, title, desp='', options=None):
    if options is None:
        options = {}
    # 判断 sendkey 是否以 'sctp' 开头，并提取数字构造 URL
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
    params = {
        'title': title,
        'desp': desp,
        **options
    }
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    response = requests.post(url, json=params, headers=headers)
    result = response.json()
    return result

args = sys.argv[1:]
if len(args) == 0:
    print("发送信息总得给个标题嘛, 调用格式python send_message.py title [detail]")
    exit(-1)
head = args[0]
detail = args[1] if len(args) > 1 else ''

print(f'Try to send message {head} <> {detail}')
#key = 'SCT275469TT6ZnaDBuet2T3ibczmBRQglK'
key = 'SCT279081TjpYjlgfVuheiHKBfZfx0ht1L'

try:
    ret = sc_send(key, head, detail)
    print(ret)
except Exception as e:
    print(e)


