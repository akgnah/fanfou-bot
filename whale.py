#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import math
import json
import time
import random
import conf
import models
import fanfou
from datetime import datetime

sent = models.Whale_Sent()
user = models.Whale_User()
talk = models.Whale_Talk()


client1 = fanfou.OAuth(*conf.token['whale1'])
client2 = fanfou.OAuth(*conf.token['whale2'])
fanfou.bound(client1)
fanfou.bound(client2)

my_unique_id = '~YVRvMhrSZx0'


with open(os.path.join(conf.curdir, 'static', 'whale.json'), encoding='utf8') as f:
    whale_json = json.loads(f.read())


def htmlec(s):
    el = {'&lt;': '<', '&gt;': '>', '&quot;': '"', '&amp;': '&'}
    for k, v in el.items():
        s = s.replace(k, v)
    return s.strip()


def check():
    data = client1.account.notification({'mode': 'lite'}).json()
    if data['direct_messages']:
        learn()
    if data['mentions']:
        chat(data['mentions'])


def emoji():
    emojis = [':)', ':-)', ';-)']
    emoji = models.ctx.w_emoji or ':)'
    emojis.remove(emoji)
    emoji = random.choice(emojis)
    models.ctx.w_emoji = emoji
    return models.ctx.w_emoji


def cmd(item):
    text = htmlec(item['text'])[12:].strip()
    user_id = item['user']['unique_id']
    custom, block = user.select(user_id)
    update, flag = bool(custom), None

    if text.startswith('--like-') or text.startswith('--hate-'):
        mode, lang = text.split('-')[-2:]
        if lang in ['en', 'jp', 'zh']:
            custom[mode] = lang
            flag = 'save'
    elif text.startswith('--def-'):
        mode, val = re.search(r'--def-([^ ]*)(.*)', text).groups()
        if mode in ('morn', 'night', 'nick'):
            custom[mode] = val
            flag = 'save'
    elif text.startswith('--block'):
        block = abs(block - 1)
        flag = 'done'
    elif text.startswith('--del'):
        ori_id = item.get('repost_status_id') or item.get('in_reply_to_status_id')
        if ori_id:
            data = client1.statuses.show({'id': ori_id, 'mode': 'lite'}).json()
            ori_user_id = data.get('repost_user_id') or data.get('in_reply_to_user_id')
            if item['user']['id'] in (ori_user_id, 'home2'):
                client1.statuses.destroy({'id': ori_id, 'mode': 'lite'})
                flag = 'done'
    elif text.startswith('--reset'):
            user.delete(user_id)
            flag = 'done'

    if flag:
        if update and 'reset' not in text:
            user.update(user_id, custom, block)
        elif 'reset' not in text:
            user.insert(user_id, custom, block)
        sent.insert(item['id'])
        reply_text = '@%s %s %s' % (item['user']['name'], {'done': '操作完成', 'save': '我记住啦'}.get(flag), emoji())
        body = {'status': reply_text, 'mode': 'lite', 'in_reply_to_status_id': item['id']}
        client1.statuses.update(body)


def chat(amount):
    cmds = ['--like-', '--hate-', '--block', '--del', '--def-', '--reset']

    count = 60 if amount > 20 else 20
    pages = int(amount / count) + 2
    for page in range(1, pages):
        body = {'count': count, 'page': page, 'mode': 'lite'}
        for item in client1.statuses.mentions(body).json():
            if sent.select(item['id']) or item.get('repost_status_id'):
                continue

            text = htmlec(item['text'])
            if True in map(lambda s: text[12:].strip().startswith(s), cmds):
                try:
                    cmd(item)
                except:
                    continue
            else:
                reply_list = []
                for ask, ans in talk.fetchall():
                    if ask in text:
                        reply_list.append(ans)
                try:
                    reply_text = '@%s %s' % (item['user']['name'], random.choice(reply_list))
                    body = {'status': reply_text, 'in_reply_to_status_id': item['id'], 'mode': 'lite'}
                    client1.statuses.update(body)
                    sent.insert(item['id'])
                except:
                    continue


def learn():
    def fanli(item):
        # http://spacekid.me/spacefanfou/
        created_at = datetime.strptime(item['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        a = item['followers_count']
        b = (datetime.utcnow() - created_at).days
        y = item['statuses_count'] / float(b)
        K = 0.75 if item['protected'] else 1.0
        A = K if y > 20 else ((-y * y + 40 * y) / 400.0) * K
        N = A * ((a + b) / 100.0) + 10 * math.sqrt(a) / math.log(b + 100.0, math.e)
        return round(N)

    for item in client1.direct_messages.inbox({'count': 60, 'mode': 'lite'}).json():
        text = htmlec(item['text'])
        idx1, idx2 = [text.find(i) for i in ('Q:', 'A:')]
        if -1 in [idx1, idx2]:
            continue
        else:
            try:
                user_id = item['sender']['unique_id']
                data = client1.users.show({'id': user_id}).json()
                if fanli(data) > 10:
                    talk.insert(text[idx1 + 2: idx2].strip(), text[idx2 + 2:].strip())
                    client1.direct_messages.destroy({'id': item['id']})
                    body = {'user': user_id, 'text': '我学会啦（%s）' % text, 'mode': 'lite'}
                    client1.direct_messages.new(body)
            except:
                continue


def reply(mode, text, item):
    d_choice = lambda d: random.choice(random.choice(list(d.values())))

    ori_id = item.get('repost_status_id') or item.get('in_reply_to_status_id')
    if ori_id or sent.select(item['id']):
        return

    reply_dict = whale_json.get(mode)
    custom, block = user.select(item['user']['unique_id'])

    if block or item['user']['unique_id'] == my_unique_id:
        return

    if not custom:
        reply_text = d_choice(reply_dict)
    else:
        if mode == 'morn' and custom.get('mron'):
            reply_text = custom.get('mron')
        elif mode == 'night' and custom.get('night'):
            reply_text = custom.get('night')
        elif custom.get('like'):
            reply_text = random.choice(reply_dict[custom.get('like')])
        elif custom.get('hate'):
            reply_dict.pop(custom.get('hate'))
            reply_text = d_choice(reply_dict)
        elif custom['nick']:
            reply_text = '%s，%s' % (custom['nick'], d_choice(reply_dict))
        else:
            reply_text = d_choice(reply_dict)

    status = '%s 转@%s %s' % (reply_text, item['user']['name'], text)
    body = {'status': status, 'repost_status_id': item['id'], 'mode': 'lite'}
    client1.statuses.update(body)
    sent.insert(item['id'])


def greet(mode='morn'):
    def fetch():
        client = client1 if random.random() > 0.25 else client2
        if random.random() > 0.50:
            resp = client.statuses.home_timeline({'count': 60, 'mode': 'lite'})
        else:
            resp = client.statuses.public_timeline({'count': 60, 'mode': 'lite'})
        return resp.json()

    greet_words = whale_json['keywords']
    if mode == 'morn':
        greet_words.pop('night')
    else:
        greet_words.pop('morn')

    for item in fetch():
        text = htmlec(item['text'])
        for mode, words in greet_words.items():
            if True in map(lambda s: s in text, words):
                try:
                    reply(mode, text, item)
                    time.sleep(0.2)
                except:
                    continue


def hello(act='welcome', mode='morn'):
    client1.statuses.update({'status': whale_json[act][mode]})


if __name__ == '__main__':
    argv = sys.argv

    if argv[1] == 'check':
        check()
    elif argv[1] == 'greet':
        greet(argv[2])
    else:
        hello(argv[1], argv[2])
