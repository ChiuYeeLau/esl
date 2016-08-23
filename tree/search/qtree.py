#!/usr/bin/env python
# encoding: utf-8

import json
from itertools import product, imap
from search.parse import transfer_Node_i, parse, tree_format
from search.clean_sentence import cleaned_sentence
from search.util import getq, check_equal
from pymongo import MongoClient
# client = MongoClient('166.111.139.42')
client = MongoClient('127.0.0.1')
db = client.test
db.authenticate('test', 'test')
cl = db.syntax2
f = open('search/stemmer.json')
stemmerDict = json.load(f)
Gflag = True


class QtreeFinder(object):
    def __init__(self, tree, key, qtree, qkey, tk, ctype=0):
        self.result = None
        self.resultSent = ""
        self.resultList2 = []
        self.resultSent2 = ""
        self.cost = 0
        self.checker = True
        self.outputArg = -1
        self.tree = tree
        self.key = key
        self.qtree = qtree
        self.qkey = qkey
        self.tk = tk
        self.ctype = ctype

    def check_point(self, n1, n2, lt, lq):
        if not check_equal(n1.elem, n2.elem):
            return False
        c1, c2 = n1.children, n2.children
        if self.ctype == 0:
            if len(c1) != len(c2):
                return False
            for cc1, cc2 in imap(None, c1, c2):
                p1, p2 = cc1 in lt, cc2 in lq
                if p1 != p2:
                    return False
                if not p1 and not check_equal(cc1.elem, cc2.elem):
                    return False
        else:
            ltc, lqc = [], []
            for cc1 in c1:
                if cc1 in lt:
                    ltc.append(lt.index(cc1))
            for cc2 in c2:
                if cc2 in lq:
                    lqc.append(lq.index(cc2))
            if cmp(ltc, lqc) != 0:
                return False
        return True

    def get_result(self):
        if self.ctype == 2:
            listq = [self.qtree[1][i] for i in self.qkey]
            self.nodeList = listq[:]
            while len(listq) > 1:
                nodeq = reduce(lambda x, y: x if x.depth > y.depth else y, listq, listq[0]).parent
                listq = [x for x in listq if x.parent is not nodeq] + [nodeq]
                self.nodeList.append(nodeq)
            self.add_result(listq[0])
            return

        listt = [self.tree[1][i] for i in self.key]
        listq = [self.qtree[1][i] for i in self.qkey]
        self.nodeList = listq[:]
        tqd = listt[0].depth - listq[0].depth
        if not reduce(lambda x, y: x and (y[0].depth - y[1].depth == tqd), imap(None, listt, listq), True):
            return
        while len(listt) > 1:
            nodet = reduce(lambda x, y: x if x.depth > y.depth else y, listt, listt[0]).parent
            nodeq = reduce(lambda x, y: x if x.depth > y.depth else y, listq, listq[0]).parent
            if not self.check_point(nodet, nodeq, listt, listq):
                return False
            listt = [x for x in listt if x.parent is not nodet] + [nodet]
            listq = [x for x in listq if x.parent is not nodeq] + [nodeq]
            self.nodeList.append(nodeq)

        self.add_result(listq[0])

    def deep_check(self, qtree):
        if qtree.elem in ['_comma_', '.']:
            self.checker = False
        for child in qtree.children:
            if self.checker:
                self.deep_check(child)

    def get_more_result(self, qtree, childcnt, depth=0):
        if not qtree.children:
            self.cost += 1
            self.resultList2.append(self.tk[int(qtree.elem)]['l'])
            self.outputArg += 1
            return
        elif self.ctype == 0 and depth == 2 or self.ctype != 0 and depth == 1:
            if self.outputArg >= len(self.qkey) - 1:
                self.outputArg += 1
                if self.outputArg > len(self.qkey):
                    return
            elif self.outputArg < 0:
                return
            if childcnt[0] == 0:
                self.resultList2.append('...')
                childcnt[0] += 1
                self.cost += 1
            if self.checker:
                self.deep_check(qtree)
            return

        childcnt[0] = 0
        for child in qtree.children:
            self.get_more_result(child, childcnt, depth if depth == 0 and child in self.nodeList else depth + 1)

        if self.outputArg < len(self.qkey) - 1:
            if self.resultList2 and self.resultList2[-1] not in ['', '...', '|']:
                self.resultList2.append('')
            else:
                self.resultList2.append('|')
                self.cost += 1

    def add_result(self, qtree):
        self.result = qtree
        self.get_more_result(qtree, [0, 0])

        if self.checker and self.cost <= max(len(self.qkey) * 2, 5):
            self.resultSent2 = ' '.join(self.resultList2)
        else:
            self.resultSent2 = '_others_'

        self.resultSent = ' '.join([self.tk[i]['l'] for i in range(self.qkey[0], self.qkey[-1] + 1)])

    def debug(self, qtree, depth=0):
        print '\t' * depth + qtree.elem
        for child in qtree.children:
            self.debug(child, depth + 1)


def addCluster(inMap, retList, title, dictc):
    if title not in inMap:
        inMap[title] = len(inMap)
    retId = inMap[title]
    flag1, flag2 = False, False
    for desc in retList:
        if desc['id'] == retId:
            desc['count'] += 1
            flag2 = True
            if desc['count'] <= 10:
                flag1 = True
            break
    if not flag2:
        flag1 = True
        retList.append(dict({'id': retId, 'count': 1, 'title': title}, **dictc))
    return (retId, flag1)


# [u'index', u'word', u'lemma', u'after', u'pos', u'characterOffsetEnd', u'characterOffsetBegin', u'originalText', u'before']
def is_upper(token):
    tt = str(token['word'])
    return tt.isalpha() and tt.isupper()


def stemmer_value(token):
    tt = str(token['lemma'])
    return stemmerDict.get(tt, tt)


def check_find(tree, key, tokens, qtree, tk, ctype):
    iterlists = []
    for k in key:
        flag = is_upper(tokens[k])
        iterlist = []
        for i, t in enumerate(tk):
            # if flag and check_equal(tokens[k]['word'], t['p']) or not flag and stemmer_value(tokens[k]) == t['s']:
            if flag and check_equal(tokens[k]['word'], t['p']) or not flag and tokens[k]['lemma'] == t['l']:
                iterlist.append(i)
        iterlists.append(iterlist)

    retFinder = None

    # print reduce(lambda x, y: x*len(y), iterlists, 1)
    for qkey in product(*iterlists):
        if ctype == 2 or reduce(lambda x, y: (x[0] and x[1] < y, y), qkey, (True, -1))[0]:
            qtreeFinder = QtreeFinder(tree, key, qtree, qkey, tk, ctype)
            qtreeFinder.get_result()
            if ctype != 2 and qtreeFinder.result:
                retFinder = qtreeFinder
                break
            if ctype == 2 and (not retFinder or qtreeFinder.cost < retFinder.cost):
                retFinder = qtreeFinder

    return retFinder


def result_part(retJson):
    if len(retJson['desc']['sen']) > 20:
        retJson['desc']['sen'] = retJson['desc']['sen'][:20] + retJson['desc']['sen'][-1:]
        senlist = [sen['id'] for sen in retJson['desc']['sen']]
        retJson['result'] = [result for result in retJson['result'] if result['sen'] in senlist]


def get_qtree_db(tree, tokens, key, ctype):
    nkey = []
    for k in key:
        if not is_upper(tokens[k]):
            nkey.append(k)
    if ctype == 2:
        # keys = [stemmer_value(tokens[k]) for k in nkey]
        keys = [tokens[k]['lemma'] for k in nkey]
        keys.sort(key=lambda word: -len(word))
        # rs = cl.find({'tokens.s': {'$all': keys}})
        rs = cl.find({'tokens.l': {'$all': keys}})
    else:
        # keys = [{'$elemMatch': {'s': stemmer_value(tokens[k]), 'q': getq(tokens[k]['pos'])}} for k in nkey]
        # keys.sort(key=lambda word: -len(word['$elemMatch']['s']))
        # rs = cl.find({'tokens': {'$all': keys}})
        keys = [{'$elemMatch': {'l': tokens[k]['lemma'], 'q': getq(tokens[k]['pos'])}} for k in nkey]
        keys.sort(key=lambda word: -len(word['$elemMatch']['l']))
        rs = cl.find({'tokens': {'$all': keys}})

    # retJson = {'result': [], 'desc': {'sen': []}}
    # senmap = {}
    # senlist = retJson['desc']['sen']
    retJson = {'result': [], 'desc': {'sen': []}}
    senmap2 = {}
    senlist2 = retJson['desc']['sen']

    strlist = retJson['result']
    for sen in rs:
        sent = sen['tree0']
        tk = sen['tokens']
        qtree = transfer_Node_i(sent)
        tp = check_find(tree, key, tokens, qtree, tk, ctype)
        if tp:
            # senId = addCluster(senmap, senlist, tp.resultSent)
            (senId2, flag1) = addCluster(senmap2, senlist2, tp.resultSent2, {'len': tp.cost})
            if flag1:
                markSent = cleaned_sentence([w['t'] for w in tk], tp.qkey)
                resultDict = {'sentence': markSent, 'sen': senId2}
                strlist.append(resultDict)

    senlist2.sort(key=lambda word: -word['count'] * 100 + word['len'] if word['title'] != '_others_' else 0)
    result_part(retJson)
    return retJson


def get_qtree_inter(sentence, key, ctype):
    # print sentence, key
    rquest = parse(sentence)
    tokens = rquest['sentences'][0]['tokens']

    treeBracket = rquest['sentences'][0]['parse']
    # print treeBracket
    treeS = tree_format(treeBracket)
    # print treeS
    tree = transfer_Node_i(treeS)

    return get_qtree_db(tree, tokens, key, ctype)
