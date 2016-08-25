#!/usr/bin/env python
# encoding: utf-8

import json
from itertools import product
from search.parse import transfer_Node_i, parse
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
disp = {'SBAR': 'S', 'ADVP': 'ADV', 'ADJP': 'ADJ', 'JJ': 'ADJ', 'RB': 'ADV',
        'NN': 'N', 'NP': 'N', 'VP': 'V', 'VB': 'V'}


def dfs_root_tree(tree, arg):
    tree.extra['tag'] = -1
    for child in tree.children:
        dfs_root_tree(child, arg)
    if len(tree.children) == 0:
        tree.extra['rep'] = [arg['tk'][int(tree.elem)]['l'], '']
    elif len(tree.children[0].children) == 0:
        tree.extra['rep'] = [tree.children[0].extra['rep'][0], tree.elem]
    else:
        tree.extra['rep'] = ['', '']
        tex = tree.extra
        te = tree.elem
        tk = arg['tk']
        stat = [0] * 5
        for child in tree.children:
            cexr = child.extra['rep']
            if te == 'NP':
                if getq(child.elem) in ['NN', 'NP']:
                    tex['rep'] = cexr
                elif child.elem == 'PP':
                    c = child.children[0]
                    if c.elem == 'IN':
                        tkcc = tk[int(c.children[0].elem)]['l']
                        if tkcc == 'of':
                            tex['rep'][0] = ''
            elif te == 'VP':
                if child.elem == 'TO':
                    stat[0] = 1
                elif getq(child.elem) == 'VB':
                    tex['rep'] = cexr
                    tkc = tk[int(child.children[0].elem)]['l']
                    if tkc == 'have':
                        stat[0] = 2
                    elif tkc == 'be':
                        stat[0] = 3
                    elif tkc == 'do':
                        stat[0] = 4
                elif child.elem == 'MD':
                    tkc = tk[int(child.children[0].elem)]['l']
                    if tkc in ['will', 'would']:
                        stat[0] = 5
                elif child.elem == 'VP':
                    if stat[0] == 2 and cexr[1] == 'VBN' or \
                            stat[0] == 3 and cexr[1] == 'VBN' or \
                            stat[0] == 5 and cexr[1] == 'VBP':
                        tex['rep'] = cexr
                    elif stat[0] == 4 and cexr[1] == 'VBP':
                        tex['rep'] = cexr
                    elif stat[0] == 3 and cexr[1] == 'VBG':
                        tex['rep'] = cexr
                    elif stat[0] != 0:
                        tex['rep'][0] = ''
                    else:
                        tex['rep'] = cexr

            elif te == 'ADJP':
                if child.elem in ['ADJP', 'JJ']:
                    tex['rep'] = cexr
            elif te == 'ADVP':
                if child.elem in ['ADVP', 'RB', 'RBR']:
                    tex['rep'] = cexr

        if tree.children[-1].elem == 'POS':
            tree.elem = 'PRP$'
            tex['rep'][0] = ''


def get_common_ans(tree, arg):
    if len(tree.children) == 0:
        arg['ansl'] += arg['tk'][int(tree.elem)]['l'] + ' '
        arg['anst'] = arg['tk'][int(tree.elem)]['t'] + ' ' \
            if tree.parent.elem in ['VBG', 'VBN'] else arg['ansl']
    for child in tree.children:
        if child.extra['tag'] == arg['tag']:
            get_common_ans(child, arg)
        else:
            arg['anst'] += child.elem + ' '
            arg['ansl'] += child.elem + ' '


def get_root_tree(arg):
    dfs_root_tree(arg['tree'], arg)


def addCluster(inMap, retList, title, dictc={}):
    if title not in inMap:
        retId = inMap[title] = len(retList)
        retList.append(dict({'id': retId, 'count': 1, 'title': title}, **dictc))
        flag = True
    else:
        retId = inMap[title]
        retList[retId]['count'] += 1
        flag = retList[retId]['count'] <= 10
    return (retId, flag)


def addResult(arg, q):
    title = q['mod']
    if arg['type'] == 0:
        (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title)
        if flag:
            markSent = cleaned_sentence(arg['sent'], arg['keypos'])
            arg['strlist'].append({'sentence': markSent, 'sen': retId})
    elif arg['type'] == 1:
        if title == arg['title']:
            title = q['word']
            (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title)
            if flag:
                markSent = cleaned_sentence(arg['sent'], arg['keypos'])
                arg['strlist'].append({'sentence': markSent, 'sen': retId})


def modeget(child, arg, q, ad=''):
    c = q['ch']
    c['v'] &= child.elem[0].isalpha()
    c['v'] &= child.elem not in ['MD', 'CC']
    c['w'] += 1
    e = child.elem
    r = child.extra['rep'][0]
    if not r:
        r = '_other_'
    if e in ['CD', 'PDT', 'QP', 'PRN', 'DT', 'PRP$', 'POS']:
        c['w'] -= 1
    elif ad == 'V N' and e in ['PRT']:
        c['w'] -= 1
    elif ad == 'VBG' and e in ['VBG', 'VBN']:
        c['g'] |= 1
        q['mod'] += e + ' '
        q['word'] += r + ' '
    elif e in ['ADVP']:
        c['sv'] -= 1
        if c['sv'] >= 0:
            q['mod'] += disp.get(e, e) + ' '
            q['word'] += r + ' '
        else:
            c['w'] -= 1
    elif len(child.children) == 1 and len(child.children[0].children) == 0:
        tk = arg['tk'][int(child.children[0].elem)]['l']
        e = getq(child.elem)
        if e in ['IN', 'TO']:
            q['mod'] += tk + ' '
            q['word'] += tk + ' '
        elif e in ['NN', 'JJ'] or (ad == 'N V' and child.elem in ['VBG', 'VBN']):
            if e == 'NN':
                c['sn'] -= 1
            if e == 'JJ' or (ad == 'N V' and child.elem in ['VBG', 'VBN']):
                c['sj'] -= 1
                e = 'JJ'
            if c['sn'] >= 0 and c['sj'] >= 0:
                q['mod'] += disp.get(e, e) + ' '
                q['word'] += r + ' '
            else:
                c['w'] -= 1
        elif e in ['RB']:
            if tk == 'not' or c['sv'] <= 0:
                c['w'] -= 1
            else:
                c['sv'] -= 1
                q['mod'] += disp.get(e, e) + ' '
                q['word'] += r + ' '
        elif e in ['VB']:
            if tk in ['be']:
                c['w'] -= 1
            elif tk in ['have']:
                c['w'] -= 1
            else:
                q['mod'] += disp.get(e, e) + ' '
                q['word'] += r + ' '
        else:
            q['mod'] += disp.get(e, e) + ' '
            q['word'] += r + ' '
    else:
        if e == 'ADJP':
            c['sj'] -= 1
        if c['sj'] >= 0:
            q['mod'] += disp.get(e, e) + ' '
            q['word'] += r + ' '
        else:
            c['w'] -= 1


def comnex_add(node, arg):
    q = {'mod': "", 'word': "", 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
    comone = arg['common'].elem
    ad = ''
    ed = vm = br = advp = False
    childe = [child.elem for child in node.children]
    if node.parent.elem == 'VP' and node.elem == 'VP':
        checkbe = node.parent.children[0].children
        ts = arg['common'].extra['rep'][1]
        if len(checkbe[0].children) == 0:
            wd = arg['tk'][int(checkbe[0].elem)]['l']
            if ts == 'VBN' and wd in ['be']:
                q['mod'] += 'be '
                q['word'] += 'be '
                ed = True
            # passive
            # print ts
            if ts == 'VBN' and wd in ['have'] or ts == 'VBG' and wd in ['be'] \
                    or ts == 'VB' and wd in ['will', 'would', 'to', 'do']:
                br = True
            # break later
    # verb example
    if node.elem == 'PP':
        return False
    # pp not count
    if node.elem in ['S', 'SBAR'] and ('ADJP' in childe or 'JJ' in childe):
        return False
    # make it clear (that)
    if comone in ['ADJP', 'JJ']:
        q['ch']['sj'] -= 1
    if node.elem == 'NP':
        if getq(comone) in ['NN', 'NP']:
            q['ch']['sn'] -= 1
            ad = 'N V'
        # complicate NP
        if getq(comone) in ['VB', 'VP']:
            vm = True
        # keep the tense
    if node.elem == 'ADJP' and comone in ['ADJP', 'JJ'] and node.parent.elem == 'VP':
        checkbe = node.parent.children[0].children
        if len(checkbe[0].children) == 0:
            wd = arg['tk'][int(checkbe[0].elem)]['l']
            if wd in ['be']:
                q['mod'] += 'be '
                q['word'] += 'be '
    # be clear that
    if node.elem == 'VP' and getq(comone) in ('NN', 'NP'):
        ad = 'V N'
    # cut down trees
    for child in node.children:
        if child.extra['tag'] == arg['tag']:
            if ed or vm:
                sub = arg['anst']
            else:
                sub = arg['ansl']
            # q['mod'] += sub + '(%s) ' % arg['common'].elem
            q['mod'] += sub
            q['word'] += sub
        # the common node
        elif getq(comone) in ['NN', 'NP'] and child.elem == 'VP':
            checkbe = node.parent.children[0].children
            if len(checkbe[0].children) == 0:
                wd = arg['tk'][int(checkbe[0].elem)]['l']
                q['ch']['v'] &= wd not in ['be']
        elif comone in ['ADVP', 'RB', 'RBR'] and \
                (getq(child.elem) not in ['VB', 'VP', 'JJ'] and child.elem not in ['ADJP']):
            pass
        elif child.elem == 'PP':
            for child2 in child.children:
                modeget(child2, arg, q, 'VBG')
                if q['ch']['g'] > 0:
                    break
        # PP extend
        elif child.elem in ['S'] and len(child.children) == 1 and child.children[0].elem == "VP":
            for child2 in child.children[0].children:
                modeget(child2, arg, q, 'VBG')
                if q['ch']['g'] > 0:
                    break
        # S extend
        elif comone in ['NN', 'NP'] and child.elem in ['S', 'SBAR']:
            pass
        # N S forbid
        # elif comone in ['ADJP', 'JJ'] and child.elem in ['S', 'SBAR'] and q['ch']['w'] == 0:
        #    pass
        # J forbid
        elif child.elem in ['ADVP', 'RB', 'RBR']:
            if comone not in ['ADVP', 'RB', 'RBR']:
                advp = True
        # ignore S after N
        else:
            modeget(child, arg, q, ad)

    if q['ch']['v'] and q['ch']['w'] > 0:
        addResult(arg, q)

    if not ed and not vm and advp and \
            (comone in ['VP', 'ADJP'] or getq(comone) in ['VB', 'JJ']):
        q = {'mod': "", 'word': "", 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
        for child in node.children:
            if child.extra['tag'] == arg['tag']:
                sub = arg['ansl']
                # q['mod'] += sub + '(%s) ' % arg['common'].elem
                q['mod'] += sub
                q['word'] += sub
            elif child.elem in ['ADVP', 'RB', 'RBR']:
                modeget(child, arg, q)
            else:
                pass
        if q['ch']['v'] and q['ch']['w'] > 0:
            addResult(arg, q)

    return 0 if ed or vm or br else 100


def find_common(arg):
    node = arg['nodes'][arg['keypos'][0]].parent
    lca = [node, node.depth]
    for i, k in enumerate(arg['keypos']):
        if i == 0:
            node = arg['nodes'][k]
            while node:
                node.extra['tag'] = arg['tag']
                node = node.parent
        else:
            node = arg['nodes'][k]
            while node.extra['tag'] != arg['tag']:
                node.extra['tag'] = arg['tag']
                node = node.parent
            if node.depth < lca[1]:
                lca = [node, node.depth]
    return lca[0]


def comnex_find(arg):
    # print arg['common'].extra
    if not arg['common'].extra['rep'][0]:
        return
    # if len(arg['keypos']) > 1:
    #    addResult(arg, arg['ansl'])
    node = arg['common'].parent
    brk = 10
    while node.elem != '@':
        if node.extra['rep'][0] not in arg['keylm']:
            brk = min(brk, 1)
        brk = min(brk - 1, comnex_add(node, arg))
        if brk == 0:
            return
        node = node.parent


def check_find(key, tokens, arg):
    get_root_tree(arg)

    iters = []
    for k in key:
        iterlist = []
        for i, t in enumerate(arg['tk']):
            if tokens[k]['lemma'] == t['l']:
                iterlist.append(i)
        iters.append(iterlist)

    for tag, qkey in enumerate(product(*iters)):
        arg['keypos'] = qkey
        arg['keytk'] = [arg['tk'][k] for k in qkey]
        arg['keylm'] = [k['l'] for k in arg['keytk']]
        arg['tag'] = tag
        arg['common'] = find_common(arg)
        arg['ansl'] = arg['anst'] = ''
        get_common_ans(arg['common'], arg)
        comnex_find(arg)


def result_part(retJson):
    if len(retJson['desc']['sen']) > 20:
        # retJson['desc']['sen'] = retJson['desc']['sen'][:20] + retJson['desc']['sen'][-1:]
        retJson['desc']['sen'] = retJson['desc']['sen'][:20]
        senlist = [sen['id'] for sen in retJson['desc']['sen']]
        retJson['result'] = [result for result in retJson['result'] if result['sen'] in senlist]


def get_comnex_db(tokens, key, args):
    retJson = {'result': [], 'desc': {'sen': []}}
    senmap = {}

    keys = [tokens[k]['lemma'] for k in key]
    keys.sort(key=lambda word: -len(word))
    rs = cl.find({'tokens.l': {'$all': keys}})

    for sen in rs:
        tree0 = sen['tree0']
        tk = sen['tokens']
        tree = transfer_Node_i(tree0)
        halfSent = [w['t'] for w in tk]
        arg = dict({
            'tk': tk,
            'tree': tree[0],
            'nodes': tree[1],
            'senmap': senmap,
            'senlist': retJson['desc']['sen'],
            'strlist': retJson['result'],
            'sent': halfSent,
        }, **args)
        check_find(key, tokens, arg)

    retJson['desc']['sen'].sort(key=lambda word: -word['count'] if word['title'] != '_others_' else 0)
    result_part(retJson)
    return retJson


def get_comnex_inter(sentence, key, ctype):
    rquest = parse(sentence)
    tokens = rquest['sentences'][0]['tokens']

    return get_comnex_db(tokens, key, {'title': sentence + ' ', 'type': ctype})
