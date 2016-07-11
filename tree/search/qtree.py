#!/usr/bin/env python
# encoding: utf-8

from itertools import product, imap
from search.parse import transfer_Node_i, parse, tree_format
from search.util import getq, check_equal
from pymongo import MongoClient
client = MongoClient()
db = client.test
db.authenticate('test', 'test')
cl = db.syntax


class QtreeFinder(object):
    def __init__(self, tree, key, qtree, qkey, tk):
        self.result = None
        self.resultSent = ""
        self.resultSent2 = ""
        self.nodeList = []
        self.tree = tree
        self.key = key
        self.qtree = qtree
        self.qkey = qkey
        self.tk = tk

    def check_point(self, n1, n2, lt, lq):
        if not check_equal(n1.elem, n2.elem):
            return False
        c1, c2 = n1.children, n2.children
        if len(c1) != len(c2):
            return False
        for cc1, cc2 in imap(None, c1, c2):
            p1, p2 = cc1 in lt, cc2 in lq
            if p1 != p2:
                return False
            if not p1 and not check_equal(cc1.elem, cc2.elem):
                return False
        return True

    def get_result(self):
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

    def get_more_result(self, qtree, depth=0):
        if not qtree.children:
            self.resultSent2 += self.tk[int(qtree.elem)]['l'] + ' '
        elif depth == 2:
            self.resultSent2 += qtree.elem
            return

        for child in qtree.children:
            self.get_more_result(child, depth if depth == 0 and child in self.nodeList else depth + 1)

    def add_result(self, qtree):
        self.result = qtree
        self.get_more_result(qtree)
        self.resultSent2 = self.resultSent2[:-1]
        self.resultSent = ' '.join([self.tk[i]['l'] for i in range(self.qkey[0], self.qkey[-1] + 1)])

    def debug(self, qtree, depth=0):
        print '\t' * depth + qtree.elem
        for child in qtree.children:
            self.debug(child, depth + 1)


def addCluster(inMap, retList, title):
    if title not in inMap:
        inMap[title] = len(inMap)
    retId = inMap[title]
    flag = False
    for desc in retList:
        if desc['id'] == retId:
            desc['count'] += 1
            flag = True
    if not flag:
        retList.append({'id': retId, 'count': 1, 'title': title})
    return retId


def check_find(tree, key, tokens, qtree, tk):
    iterlists = []
    for k in key:
        iterlist = []
        for i, t in enumerate(tk):
            if tokens[k]['lemma'] == t['l']:
                iterlist.append(i)
        iterlists.append(iterlist)

    for qkey in product(*iterlists):
        if reduce(lambda x, y: (x[0] and x[1] < y, y), qkey, (True, -1))[0]:
            qtreeFinder = QtreeFinder(tree, key, qtree, qkey, tk)
            qtreeFinder.get_result()
            if qtreeFinder.result:
                return qtreeFinder

    return None


def get_qtree_db(tree, tokens, key):
    keys = []
    for k in key:
        keys.append({'$elemMatch': {'l': tokens[k]['lemma'], 'q': getq(tokens[k]['pos'])}})
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
        tp = check_find(tree, key, tokens, qtree, tk)
        if tp:
            # senId = addCluster(senmap, senlist, tp.resultSent)
            senId2 = addCluster(senmap2, senlist2, tp.resultSent2)

            stplist = [str(ele) for ele in tp.qkey]
            resultDict = {'sentence': sen['sentence'], 'list': ' '.join(stplist), 'sen': senId2}

            strlist.append(resultDict)
    senlist2.sort(key=lambda word: -word['count'])
    return retJson


def get_qtree_inter(sentence, key):
    # print sentence, key
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    tokens = rquest['sentences'][0]['tokens']
    # print treeBracket
    treeS = tree_format(treeBracket)
    # print treeS
    tree = transfer_Node_i(treeS)

    return get_qtree_db(tree, tokens, key)
