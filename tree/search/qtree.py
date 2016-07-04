#!/usr/bin/env python
# encoding: utf-8

from search.parse import *
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
        self.keyNode = keyNode
        self.tk = tk
        self.cnt = cnt

    def check_point(self, c1, c2, elem):
        if len(c1) != len(c2):
            return False
        for i in range(len(c1)):
            if hasattr(c2[i], 'match'):
                flag = False
                for e in c2[i].match:
                    if c1[i] is e[0]:
                        elem[1] += e[1]
                        flag = True
                        break
                if not flag:
                    return False
            else:
                if not check_equal(c1[i].elem, c2[i].elem):
                    return False
        return True

    def recur_check(self, qtree):
        for child in qtree.children:
            self.recur_check(child)
        if len(qtree.children) > 0:
            match = set()
            for child in qtree.children:
                if hasattr(child, 'match'):
                    for e in child.match:
                        if e[0].parent is not None:
                            match.add(e[0].parent)
            for e in match:
                matchElem = [e, []]
                if self.check_point(e.children, qtree.children, matchElem):
                    if not hasattr(qtree, 'match'):
                        qtree.match = []
                    qtree.match.append(matchElem)
        else:
            lm = self.tk[int(qtree.elem)]['l']
            if lm in self.keyNode:
                qtree.match = [[node, [int(qtree.elem)]] for node in self.keyNode[lm]]
        if hasattr(qtree, 'match'):
            for e in qtree.match:
                if len(e[1]) == self.cnt:
                    self.result.append(e[0])
                    self.resultList = e[1]
                    break

def check_find(keyNode, qtree, tk, cnt):
    qtreeFinder = QtreeFinder(keyNode, tk, cnt)
    qtreeFinder.recur_check(qtree)
    return qtreeFinder

def get_qtree_db(tree, tokens, keyNode, keys, cnt):
    keys.sort(key = lambda word: -len(word['$elemMatch']['l']))
    rs = cl.find({'tokens': {'$all': keys}})
    retJson = {'result':[], 'desc':{}}
    strlist = retJson['result']
    simset = set()
    for sen in rs:
        sent = sen['tree0']
        tk = sen['tokens']
        qtree = transfer_Node_i(sent)
        tp = check_find(keyNode, qtree, tk, cnt)
        if len(tp.result) != 0:
            stplist = [str(ele) for ele in tp.resultList]
            strlist.append({'sentence': sen['sentence'], 'list': ' '.join(stplist), 'sim': len(tp.result)})
            simset.add(len(tp.result))
            #print sen['sentence'], tplist
    retJson['desc']['sim'] = list(simset)
    return retJson

def key_Node(tree, key, tokens):
    keyNode = {}
    i, j = 0, 0
    queue = [tree]
    while i < len(queue):
        p = queue[i]
        for child in p.children:
            queue.append(child)
        if len(p.children) == 0 and j < len(key) and int(p.elem) == key[j]:
            lm = tokens[int(p.elem)]['lemma']
            if lm not in keyNode:
                keyNode[lm] = []
            keyNode[lm].append(p)
            j += 1
        i += 1
    return keyNode

def get_qtree_inter(sentence, key):
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
    tree = transfer_Node_i(treeS)
    keyNode = key_Node(tree, key, tokens)

    return get_qtree_db(tree, tokens, keyNode, keys, len(key))
