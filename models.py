#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import db


class _Ctx(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table ctx (key blob unique not null, val text)')
        self.commit()

    def get(self, key):
        res = self.query('select val from ctx where key = ?', (key,)).first()
        try:
            return json.loads(res[0])
        except:
            pass

    def set(self, key, val):
        rowcount = self.query('insert into ctx (key, val) values (?, ?)', (key, json.dumps(val))).first()
        if rowcount < 0:
            rowcount = self.query('update ctx set val = ? where key = ?', (json.dumps(val), key)).first()
        self.commit()
        return rowcount


class Ctx:
    _ctx = _Ctx()

    def __getattr__(self, key):
        return self._ctx.get(key)

    def __setattr__(self, key, val):
        return self._ctx.set(key, val)


ctx = Ctx()


class Poems_User(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table poems_user (user_id blob unique not null, user_name blob)')
        self.commit()

    def insert(self, user_id, user_name):
        rowcount = self.query('insert into poems_user (user_id, user_name) values (?, ?)', (user_id, user_name)).first()
        self.commit()
        return rowcount

    def delete(self, user_id):
        rowcount = self.query('delete from poems_user where user_id = ?', (user_id,)).first()
        self.commit()
        return rowcount

    def update(self, user_id, user_name):
        rowcount = self.query('update poems_user set user_name = ? where user_id = ?', (user_name, user_id)).first()
        self.commit()
        return rowcount

    def select(self, user_id):
        return self.query('select user_id from poems_user where user_id = ?', (user_id,)).list()

    def fetchall(self):
        return self.query('select user_id, user_name from poems_user')


class Poems_Sent(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table poems_sent (msg_id blob)')
        self.commit()

    def insert(self, msg_id):
        rowcount = self.query('insert into poems_sent (msg_id) values (?)', (msg_id,)).first()
        self.commit()
        return rowcount

    def select(self, msg_id):
        return self.query('select msg_id from poems_sent where msg_id = ?', (msg_id,)).first()


class Whale_Sent(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table whale_sent (msg_id blob)')
        self.commit()

    def insert(self, msg_id):
        rowcount = self.query('insert into whale_sent (msg_id) values (?)', (msg_id,)).first()
        self.commit()
        return rowcount

    def select(self, msg_id):
        return self.query('select msg_id from whale_sent where msg_id = ?', (msg_id,)).first()


class Whale_Talk(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table whale_talk (ask blob, ans blob)')
        self.commit()

    def insert(self, ask, ans):
        rowcount = self.query('insert into whale_talk (ask, ans) values (?, ?)', (ask, ans)).first()
        self.commit()
        return rowcount

    def fetchall(self):
        return self.query('select ask, ans from whale_talk')


class Whale_User(db.DB):
    def __init__(self):
        db.DB.__init__(self)
        self.execute('create table whale_user (user_id blob unique not null, custom text, block int)')
        self.commit()  # custom syntax is {'nick': '', 'mron': '', 'night': '', 'like': '', 'hate': ''}

    def insert(self, user_id, custom, block=0):
        rowcount = self.query('insert into whale_user (user_id, custom, block) values (?, ?, ?)',
                              (user_id, json.dumps(custom), block)).first()
        self.commit()
        return rowcount

    def delete(self, user_id):
        rowcount = self.query('delete from whale_user where user_id = ?', (user_id,)).first()
        self.commit()
        return rowcount

    def update(self, user_id, custom, block):
        _custom = self.select(user_id)[0]
        _custom.update(custom)
        rowcount = self.query('update whale_user set custom = ?, block = ? where user_id = ?',
                              (json.dumps(_custom), block, user_id)).first()
        self.commit()
        return rowcount

    def select(self, user_id):
        res = self.query('select custom, block from whale_user where user_id = ?', (user_id,)).first()
        try:
            res = (json.loads(res[0]), res[1])
            return res
        except:
            return ({}, 0)
