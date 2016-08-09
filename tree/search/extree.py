#!/usr/bin/env python
# encoding: utf-8

import json
# from itertools import product, imap
from search.parse import transfer_Node_i, parse, tree_format, validpass
from search.clean_sentence import cleaned_sentence
from search.util import getq
from pymongo import MongoClient
# client = MongoClient('166.111.139.42')
client = MongoClient('127.0.0.1')
db = client.test
db.authenticate('test', 'test')
cl = db.syntax2
f = open('../script/newconjugate.json')
conjugateDict = json.load(f)
Gflag = True


def checksuit(strc, strp):
    return strc == strp or (getq(strc), strp) in validpass


def getextend(key, arg):
    if len(key.children) == 1 and len(key.children[0].children) == 0:
        key.extra['rep'] = [arg['tk'][int(key.children[0].elem)]['l']]
        return
    for child in key.children:
        getextend(child, arg)

    key.extra['rep'] = []
    for child in key.children:
        if checksuit(child.elem, key.elem):
            key.extra['rep'] += child.extra.get('rep', [])


def addCluster(inMap, retList, title, dictc={}):
    if title not in inMap:
        inMap[title] = len(retList)
        retId = len(retList)
        retList.append(dict({'id': retId, 'count': 1, 'title': title}, **dictc))
        # print 'newone'
        return (retId, True)
    else:
        retId = inMap[title]
        retList[retId]['count'] += 1
        # print 'wtfwtf'
        return (retId, retList[retId]['count'] <= 10)


def addResult(arg, title):
    (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title)
    # print arg['senmap'], title
    if flag:
        markSent = cleaned_sentence(arg['sent'], [])
        arg['strlist'].append({'sentence': markSent, 'sen': retId})


def wordget(last):
    return last.extra.get('rep', [''])[0] + ' '


def modeget(child, arg, c):
    if child.elem in ['IN', 'TO']:
        return arg['tk'][int(child.children[0].elem)]['l'] + ' '
    else:
        c[0] &= child.elem[0].isalpha()
        c[1] += 1
        return child.elem + ' '


def getrees(key, last, arg):
    modresult = ""
    wordresult = ""
    checker = [True, 0]
    for child in key.children:
        if child == last:
            modresult += wordget(last)
            wordresult += wordget(last)
        elif child.elem in ['PP', 'SBAR']:
            for child2 in child.children:
                modresult += modeget(child2, arg, checker)
                wordresult += wordget(last)
        else:
            modresult += modeget(child, arg, checker)
            wordresult += wordget(last)

    addResult(arg, modresult if checker[0] and checker[1] > 0 else '_others_')


def extreeFinder(tree, key, arg):
    last = key.parent
    last.extra['rep'] = [arg['tk'][int(key.elem)]['l']]
    key = key.parent.parent
    while key.elem != '@':
        for child in key.children:
            if child != last:
                getextend(key, arg)

        getrees(key, last, arg)
        if checksuit(last.elem, key.elem):
            key.extra['rep'] = last.extra['rep']
        else:
            break

        last = key
        key = key.parent


# [u'index', u'word', u'lemma', u'after', u'pos', u'characterOffsetEnd', u'characterOffsetBegin', u'originalText', u'before']


def check_find(key, tokens, qtree, arg):
    iterlist = []
    for i, t in enumerate(arg['tk']):
        if tokens[key]['lemma'] == t['l']:
            iterlist.append(i)

    for qkey in iterlist:
        extreeFinder(qtree[0], qtree[1][qkey], arg)


def result_part(retJson):
    if len(retJson['desc']['sen']) > 20:
        retJson['desc']['sen'] = retJson['desc']['sen'][:20] + retJson['desc']['sen'][-1:]
        senlist = [sen['id'] for sen in retJson['desc']['sen']]
        retJson['result'] = [result for result in retJson['result'] if result['sen'] in senlist]


def get_extree_db(tree, tokens, key):
    keys = [tokens[k]['lemma'] for k in key]
    keys.sort(key=lambda word: -len(word))
    rs = cl.find({'tokens.l': {'$all': keys}})

    retJson = {'result': [], 'desc': {'sen': []}}
    senmap = {}

    for sen in rs:
        sent = sen['tree0']
        tk = sen['tokens']
        qtree = transfer_Node_i(sent)
        halfSent = [w['t'] for w in tk]
        arg = {
            'tk': tk,
            'senmap': senmap,
            'senlist': retJson['desc']['sen'],
            'strlist': retJson['result'],
            'sent': halfSent
        }
        check_find(key[0], tokens, qtree, arg)

    retJson['desc']['sen'].sort(key=lambda word: -word['count'] * 100 if word['title'] != '_others_' else 0)
    result_part(retJson)
    return retJson


def get_extree_inter(sentence, key):
    # print sentence, key
    rquest = parse(sentence)
    tokens = rquest['sentences'][0]['tokens']

    treeBracket = rquest['sentences'][0]['parse']
    # print treeBracket
    treeS = tree_format(treeBracket)
    # print treeS
    tree = transfer_Node_i(treeS)

    return get_extree_db(tree, tokens, key)
