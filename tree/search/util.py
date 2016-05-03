#!/usr/bin/env python
# encoding: utf-8

import os
import re
import ctypes
from search.parse import *
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

def state_plus(state):
    if state[0] == 1:
        state[0] = 0
        state[1] += 1

def get_pos_list(message, sentence, pos):
    i, j = 0, pos
    state = [0, 0]
    plist = []
    for i in range(pos):
        if sentence[i] == '(':
            state[0] = 1
        elif sentence[i] == ')':
            state_plus(state)
    state[0] = 0
    #print pos, state[1]
    i = 0
    while i < len(message):
        if message[i] == ' ':
            level = 0
            while level > 1 or sentence[j] != ')':
                if sentence[j] == '(':
                    level += 1
                    state[0] = 1
                elif sentence[j] == ')':
                    level -= 1
                    state_plus(state)
                j += 1
            state_plus(state)
            i += 1
        else:
            if message[i] == ')':
                if state[0] == 1:
                    plist.append(state[1])
                    state[1] += 1
                    state[0] = 0
            elif message[i] == '(':
                state[0] = 1
            i += 1
            j += 1
    return plist

def get_query_db2(tree, message):
    mlist = extract_list(message)
    rs = cl.find({'tokens.l': {'$all': mlist}})
    strlist = []
    cnt = 0
    msg = str(message)
    for sen in rs:
        #if cnt > 10:
        #    break
        sent = str(sen['tree'])
        tp = check_serve.find(msg, sent)
        if tp != -1:
            tplist = get_pos_list(msg, sent, tp)
            stplist = [str(ele) for ele in tplist]
            strlist.append({'sentence': sen['sentence'], 'list': ' '.join(stplist)})
            #strlist.append((str(sen['sentence']), tplist))
            #strlist.append(sen['sentence'])
            #print sen['sentence'], tplist
            cnt = cnt + 1
    return strlist

def get_query_db(message):
    mlist = extract_list(message)
    mlist.sort(key = lambda x: -len(x))
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
            strlist.append(str(sen['sentence']))
            cnt = cnt + 1
    return strlist

def get_message_cur(tree, key, var):
    ret = ''
    mlist = []
    for child in tree.children:
        mlist.append(get_message_cur(child, key, var))
    clist = [msg for msg in mlist if msg != '']
    if len(clist) > 0 and tree.depth >= var[2]:
        for i, child in enumerate(tree.children):
            if mlist[i] == '':
                mlist[i] = '( )'
            if len(child.children) == 0:
                ret = ret + mlist[i]
            else:
                ret = ret + '(%s%s)' % (child.elem, mlist[i])
    elif len(clist) > 0 and tree.depth < var[2]:
        ret = clist[0]
    elif len(tree.children) == 0:
        if var[0] < len(key) and var[1] == key[var[0]]:
            var[0] += 1
            ret = '(%s)' % tree.elem
        var[1] += 1
    return ret

def get_depth(tree, key, var):
    cnt = 0
    for child in tree.children:
        if get_depth(child, key, var) > 1:
            cnt = cnt + 1
    if cnt > 2:
        var[2] = min(var[2], tree.depth)
    if len(tree.children) == 0:
        if var[0] < len(key) and var[1] == key[var[0]]:
            var[0] += 1
            cnt = 1
            if len(key) == 1:
                var[2] = tree.depth
        var[1] += 1
    return cnt

def get_message(tree, key):
    init = [0, 0, 0]
    get_depth(tree, key, init)
    #print init[2]
    init[0], init[1] = 0, 0
    return get_message_cur(tree, key, init)

def get_parse(sentence):
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    treeS = tree_format(treeBracket)
    return treeS

def get_query_inter(sentence, key):
    #print sentence, key
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    #print treeBracket
    treeS = tree_format(treeBracket)
    #print treeS
    tree_example = transfer_Node(treeS)

    msg = get_message(tree_example[0], key)
    #print 'msg:', msg
    return get_query_db2(tree_example[0], msg)
