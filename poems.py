#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import random
import fanfou
import conf
import models

user = models.Poems_User()
sent = models.Poems_Sent()

client1 = fanfou.OAuth(*conf.token['poems1'])
client2 = fanfou.OAuth(*conf.token['poems2'])
fanfou.bound(client1)
fanfou.bound(client2)

with open(os.path.join(conf.curdir, 'static', 'poems.txt'), encoding='utf8') as f:
    poems_txt = f.readlines()


def check():
    def argv(text):
        m = re.match(r'^@{1}.+ +(?P<opt>-\w+)\s*$', text)
        if m:
            return m.group('opt')

    print('poems: check')
    resp = client1.account.notification({'mode': 'lite'})
    data = resp.json()
    amount = data['mentions']
    count = 60 if amount > 20 else 20
    pages = int(amount / count) + 2
    for page in range(1, pages):
        body = {'count': count, 'page': page, 'mode': 'lite'}
        resp = client1.statuses.mentions(body)
        for item in resp.json():
            opt = argv(item['text'])
            user_id = item['user']['unique_id']
            user_name = item['user']['name']
            if sent.select(item['id']):
                continue
            if opt == '-join' and not user.select(user_id):
                user.insert(user_id, user_name)
                sent.insert(item['id'])
                info(user_id, user_name, opt)
            elif opt == '-quit' and user.select(user_id):
                user.delete(user_id)
                sent.insert(item['id'])
                info(user_id, user_name, opt)


def emoji():
    emojis = [':)', ':-)', ';-)']
    emoji = models.ctx.p_emoji or ':)'
    emojis.remove(emoji)
    emoji = random.choice(emojis)
    models.ctx.p_emoji = emoji
    return models.ctx.p_emoji


def info(user_id, user_name, opt):
    msg = {'-join': '欢迎加入', '-quit': '退出成功'}.get(opt)
    body = {
        'status': '@%s %s %s' % (user_name, msg, emoji()),
        'in_reply_to_user_id': user_id,
        'mode': 'lite'
    }
    client2.statuses.update(body)


def update(user_id, user_name):
    body = {'id': user_id, 'mode': 'lite'}
    resp = client1.users.show(body)
    user_name = resp.json()['name']
    user.update(user_id, user_name)
    time.sleep(0.2)


def send(user_id, user_name):
    poem = random.choice(poems_txt).strip()
    body = {
        'status': '@%s %s' % (user_name, poem),
        'in_reply_to_user_id': user_id,
        'mode': 'lite'
    }
    client1.statuses.update(body)
    time.sleep(0.4)


def work(mode):
    print('poems: %s' % mode)
    func = globals().get(mode)
    for user_id, user_name in user.fetchall():
        try:
            func(user_id, user_name)
        except:
            continue


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        check()
    else:
        work(sys.argv[1])
