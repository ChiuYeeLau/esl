#!/usr/bin/env python
# encoding: utf-8

import os
import re
import ctypes
from pymongo import MongoClient
client = MongoClient('166.111.139.42')
db = client.test
db.authenticate('test', 'test')
cl = db.syntax
check_serve = ctypes.CDLL('./search/check_serve.so')


def get_query_disk(message):
    freq = open('studio/request.txt', 'w')
    freq.write(message + '\n')
    freq.close()
    os.system('./studio/check_serve')
    fres = open('studio/result.txt', 'r')
    strlist = fres.readlines()
    fres.close()
    return strlist


def extract_list(message):
    p = re.compile('\([^()]*\)')
    mlist = [st[1:-1] for st in p.findall(message) if st[1] != ' ']
    return mlist


def get_query_db(message):
    mlist = extract_list(message)
    rs = cl.find({'tokens.l': {'$all': mlist}})
    strlist = []
    cnt = 0
    for sen in rs:
        if cnt > 10:
            break
        msg = str(message)
        sent = str(sen['tree'])
        tp = check_serve.find(msg, sent)
        if tp != -1:
            strlist.append(sen['tree'])
            cnt = cnt + 1
    return strlist
