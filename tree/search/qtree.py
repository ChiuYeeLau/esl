#!/usr/bin/env python
# encoding: utf-8

from search.parse import transfer_Node_i, parse, tree_format
from search.util import getq, check_equal
from pymongo import MongoClient
client = MongoClient()
db = client.test
db.authenticate('test', 'test')
cl = db.syntax


class QtreeFinder(object):
    def __init__(self, keyNode, tk, cnt):
        self.result = []
        self.resultList = []
        self.resultSent = ""
        self.resultSent2 = ""
        self.keyNode = keyNode
        self.tk = tk
        self.cnt = cnt

    def check_point(self, c1, c2, elem):
        if len(c1) != len(c2):
            return False
        for i in range(len(c1)):
            flag = False
            for e in c2[i].match:
                if c1[i] is e[0]:
                    elem[1] += e[1]
                    flag = True
                    break
            if not flag:
                if c1[i].elem.isdigit():
                    return False
                if not check_equal(c1[i].elem, c2[i].elem):
                    return False
        return True

    def get_result(self, qtree, mtree, depth=0):
        for i, child in enumerate(qtree.children):
            flag = False
            if depth == 0:
                for e in child.match:
                    if mtree.children[i] is e[0]:
                        flag = True
            if flag:
                self.get_result(child, mtree.children[i], depth)
            else:
                self.get_result(child, None, depth + 1)
        if len(qtree.children) == 0:
            el = int(qtree.elem)
            if depth == 0:
                self.resultList.append(el)
            if depth <= 2:
                self.resultSent2 += self.tk[el]['l'] + ' '
        if depth == 2 and len(qtree.children) > 0:
            self.resultSent2 += qtree.elem + ' '

    def add_result(self, qtree, e):
        self.result.append(e[0])
        if not self.resultList:
            self.get_result(qtree, e[0])
            self.resultSent2 = self.resultSent2[:-1]
            resultSent = []
            for i in range(self.resultList[0], self.resultList[-1] + 1):
                resultSent.append(self.tk[i]['l'])
            self.resultSent = ' '.join(resultSent)

    def recur_check(self, qtree):
        qtree.match = []
        for child in qtree.children:
            self.recur_check(child)
        if len(qtree.children) > 0:
            match = set()
            for child in qtree.children:
                for e in child.match:
                    if e[0].parent is not None:
                        match.add(e[0].parent)
            for e in match:
                matchElem = [e, 0]
                if self.check_point(e.children, qtree.children, matchElem):
                    qtree.match.append(matchElem)
        else:
            lm = self.tk[int(qtree.elem)]['l']
            if lm in self.keyNode:
                # print self.tk[int(qtree.elem)]
                qtree.match = [[node, 1] for node in self.keyNode[lm]]
        for e in qtree.match:
            if e[1] == self.cnt:
                self.add_result(qtree, e)
                break

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


def check_find(keyNode, qtree, tk, cnt):
    qtreeFinder = QtreeFinder(keyNode, tk, cnt)
    # qtreeFinder.debug(qtree)
    qtreeFinder.recur_check(qtree)
    return qtreeFinder


def get_qtree_db(tree, tokens, keyNode, keys, cnt):
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
        tp = check_find(keyNode, qtree, tk, cnt)
        if len(tp.result) != 0:
            # senId = addCluster(senmap, senlist, tp.resultSent)
            senId2 = addCluster(senmap2, senlist2, tp.resultSent2)

            stplist = [str(ele) for ele in tp.resultList]
            resultDict = {'sentence': sen['sentence'], 'list': ' '.join(stplist), 'sen': senId2}

            strlist.append(resultDict)
    senlist2.sort(key=lambda word: -word['count'])
    return retJson


def key_Node(tree, key, tokens):
    keyNode = {}
    i = 0
    queue = [tree]
    while i < len(queue):
        p = queue[i]
        for child in p.children:
            queue.append(child)
        if len(p.children) == 0 and int(p.elem) in key:
            lm = tokens[int(p.elem)]['lemma']
            if lm not in keyNode:
                keyNode[lm] = []
            keyNode[lm].append(p)
        i += 1
    return keyNode


def get_qtree_inter(sentence, key):
    # print sentence, key
    rquest = parse(sentence)
    treeBracket = rquest['sentences'][0]['parse']
    tokens = rquest['sentences'][0]['tokens']
    keys = []
    for k in key:
        keys.append({'$elemMatch': {'l': tokens[k]['lemma'], 'q': getq(tokens[k]['pos'])}})
    # print treeBracket
    treeS = tree_format(treeBracket)
    # print treeS
    tree = transfer_Node_i(treeS)
    keyNode = key_Node(tree, key, tokens)

    return get_qtree_db(tree, tokens, keyNode, keys, len(key))
