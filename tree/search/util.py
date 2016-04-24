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


class Node(object):
    def __init__(self, elem="", parent=None, depth=-1):
        self.elem = elem
        self.children = []
        self.parent = parent
        self.size = 1
        self.depth = depth


class Tree(object):
    def __init__(self):
        self.root = Node()


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
            strlist.append(tuple(sent, str(sen['sentence']), tp))
            cnt = cnt + 1
    return strlist


def get_message(tree, key, var):
    ret = ''
    mlist = []
    for child in tree.children:
        mlist.append(get_message(tree, key, var))
    cnt = len([0 for msg in mlist if msg != ''])
    if cnt > 0 and var[2] <= tree.depth:
        for i, child in enumerate(tree.children):
            if mlist[i] == '':
                mlist[i] = '( )'
            ret = ret + '(%s%s)' % (child.elem, mlist[i])
    if len(tree.children) == 0:
        if var[1] == key[var[0]]:
            var[0] = var[0] + 1
            ret = '(%s)' % tree.elem
        var[1] = var[1] + 1
    return ret


def get_depth(tree, key, var):
    cnt = 0
    for child in tree.children:
        if get_depth(tree, key, var) > 1:
            cnt = cnt + 1
    if cnt > 2:
        var[2] = min(var[2], tree.depth)
    if len(tree.children) == 0:
        if var[1] == key[var[0]]:
            var[0] = var[0] + 1
            cnt = 1
            if len(key) == 1:
                var[2] = tree.depth
        var[1] = var[1] + 1
    return cnt


def get_query_inter(message, tree_example, key, sentence):
    init = [0, 0, 0]
    get_depth(tree_example[0], key, init)
    init[0], init[1] = 0, 0
    msg = get_message(tree_example[0], key, init)
    return get_query_db(msg)
