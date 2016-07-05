#!/usr/bin/env python
# encoding: utf-8

import os
import re
import ctypes
from search.parse import *
from pymongo import MongoClient
#client = MongoClient('166.111.139.42')
client = MongoClient()
db = client.test
db.authenticate('test', 'test')
cl = db.syntax

#cl = MongoClient('127.0.0.1').local.syntax

'''
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
'''

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
    for c in message:
        if c == ' ':
            level = 0
            while level > 0 or sentence[j] != ')':
                if sentence[j] == '(':
                    level += 1
                    state[0] = 1
                elif sentence[j] == ')':
                    level -= 1
                    state_plus(state)
                j += 1
            state_plus(state)
        else:
            if c == ')':
                if state[0] == 1:
                    plist.append(state[1])
                    state[1] += 1
                    state[0] = 0
            elif c == '(':
                state[0] = 1
            if c in ('(', ')'):
                j += 1
            else:
                while sentence[j] not in ('(', ')'):
                    j += 1
    return plist

def getq(tmp):
    return tmp if len(tmp) < 2 else tmp[:2]

def check_equal(tmp, tmps):
    str1 = tmp if len(tmp) < 2 else tmp[:2]
    str2 = tmps if len(tmps) < 2 else tmps[:2]
    return str1 == str2

def check_find_j(msg, tokens, sent, tk, j):
    tmp, tmps = '', ''
    for c in msg:
        if j == len(sent):
            return False
        if c == ' ':
            level = 0
            while level > 0 or j < len(sent) and sent[j] != ')':
                if sent[j] == '(':
                    level += 1
                elif sent[j] == ')':
                    level -= 1
                j += 1
            if j == len(sent):
                return False
            tmp = ''
            tmps = ''
            continue
        if c in ('(' ,')'):
            if sent[j] != c:
                return False
            if tmp != '':
                flag = tmp.isdigit()
                if flag != tmps.isdigit():
                    return False
                if flag and tokens[int(tmp)]['lemma'] != tk[int(tmps)]['l']:
                    return False
                if not flag and not check_equal(tmp, tmps):
                    return False
            tmp = ''
            tmps = ''
            j += 1
        else:
            tmp += c
            while j < len(sent) and sent[j] not in ('(', ')'):
                tmps += sent[j]
                j += 1
    return True

def check_find(msg, tokens, sent, tk):
    for j in range(len(sent)):
        if check_find_j(msg, tokens, sent, tk, j):
            return j
    return -1

def get_query_db2(tree, msg, tokens, keys):
    keys.sort(key = lambda word: -len(word['$elemMatch']['l']))
    rs = cl.find({'tokens': {'$all': keys}})
    retJson = {'result':[], 'desc':{}}
    strlist = retJson['result']
    cnt = 0
    for sen in rs:
        sent = sen['tree0']
        tk = sen['tokens']
        tp = check_find(msg, tokens, sent, tk)
        if tp != -1:
            tplist = get_pos_list(msg, sent, tp)
            stplist = [str(ele) for ele in tplist]
            strlist.append({'sentence': sen['sentence'], 'list': ' '.join(stplist)})
            #print sen['sentence'], tplist
            cnt = cnt + 1
    return retJson

'''
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
'''

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
                ret += mlist[i]
            elif mlist[i] == '( )':
                ret += '( )'
            else:
                ret += '(%s%s)' % (child.elem, mlist[i])
    elif len(clist) > 0 and tree.depth < var[2]:
        ret = clist[0]
    elif len(tree.children) == 0:
        if var[0] < len(key) and var[1] == key[var[0]]:
            # ret = '(%s)' % tree.elem
            ret = '(%d)' % var[1]
            var[0] += 1
        var[1] += 1
    # print ret
    return ret

def get_depth(tree, key, var):
    cnt = 0
    for child in tree.children:
        if get_depth(child, key, var) > 0:
            cnt = cnt + 1
    if cnt >= 2:
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
    init = [0, 0, 1024]
    get_depth(tree, key, init)
    # print init[2]
    init[0], init[1] = 0, 0
    return get_message_cur(tree, key, init)

def get_parse(sentence):
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    tokens = rquest['sentences'][0]['tokens']
    tokens_sim = [{'p' : token['pos'], 't' : token['word'], 'l' : token['lemma']} for token in tokens]
    treeS = tree_format(treeBracket)
    treeC = tree_transfer(treeS)
    return {'tokens' : tokens_sim , 'tree' : treeC}

def get_query_inter(sentence, key):
    # print sentence, key
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    tokens = rquest['sentences'][0]['tokens']
    keys = []
    for k in key:
        keys.append({'$elemMatch' : {'l' : tokens[k]['lemma'], 'q': getq(tokens[k]['pos'])}})
    # print treeBracket
    treeS = tree_format(treeBracket)
    # print treeS
    tree = transfer_Node(treeS)

    msg = get_message(tree, key)
    print 'msg, keys:', msg, keys
    return get_query_db2(tree, msg, tokens, keys)
