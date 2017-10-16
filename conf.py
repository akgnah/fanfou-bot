#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

token = {
    'poems1': ({'key': 'consumer key', 'secret': 'consumer secret'},
               {'key': 'access_token key', 'secret': 'access_token secret'}),
    'poems2': ({'key': 'consumer key', 'secret': 'consumer secret'},
               {'key': 'access_token key', 'secret': 'access_token secret'}),
    'whale1': ({'key': 'consumer key', 'secret': 'consumer secret'},
               {'key': 'access_token key', 'secret': 'access_token secret'}),
    'whale2': ({'key': 'consumer key', 'secret': 'consumer secret'},
               {'key': 'access_token key', 'secret': 'access_token secret'}),
    'kissbot': ({'key': 'consumer key', 'secret': 'consumer secret'},
                {'key': 'access_token key', 'secret': 'access_token secret'})
}

curdir = os.path.dirname(os.path.abspath(__file__))
dbn = os.path.join(curdir, 'fanfou-bot.db')
