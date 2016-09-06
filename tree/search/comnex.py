#!/usr/bin/env python
# encoding: utf-8

import json
import time
from itertools import product
from search.parse import transfer_Node_i, parse
from search.clean_sentence import cleaned_sentence
from search.util import getq
from django.conf import settings

cl = settings.DB.syntax2
f = open('../script/newconjugate.json')
conjugateDict = json.load(f)
disp = {'SBAR': 'S', 'ADVP': 'ADV', 'ADJP': 'ADJ', 'JJ': 'ADJ', 'RB': 'ADV',
        'NN': 'N', 'NP': 'N', 'VP': 'V', 'VB': 'V'}
niltk = {'l': '', 't': '', 'p': '', 'q': ''}
TIMING = [.0] * 7
CTIME = [.0] * 6


def dfs_root_tree(tree, arg):
    tree.extra['tag'] = -1
    for child in tree.children:
        dfs_root_tree(child, arg)
    if len(tree.children) == 0:
        tree.extra['rep'] = dict(arg['tk'][int(tree.elem)])
    elif len(tree.children[0].children) == 0:
        tree.extra['rep'] = dict(tree.children[0].extra['rep'])
    else:
        tree.extra['rep'] = dict(niltk)
        tex = tree.extra
        te = tree.elem
        tk = arg['tk']
        stat = [0] * 5
        for child in tree.children:
            cexr = dict(child.extra['rep'])
            if te == 'NP':
                if getq(child.elem) in ['NN', 'NP']:
                    tex['rep'] = cexr
                elif child.elem == 'PP':
                    c = child.children[0]
                    if c.elem == 'IN':
                        tkcc = tk[int(c.children[0].elem)]['l']
                        if tkcc == 'of':
                            tex['rep'] = dict(niltk)
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
                    if stat[0] == 2 and cexr['p'] == 'VBN' or \
                            stat[0] == 3 and cexr['p'] == 'VBN' or \
                            stat[0] == 5 and cexr['p'] == 'VBP':
                        tex['rep'] = cexr
                    elif stat[0] == 4 and cexr['p'] == 'VBP':
                        tex['rep'] = cexr
                    elif stat[0] == 3 and cexr['p'] == 'VBG':
                        tex['rep'] = cexr
                    elif stat[0] != 0:
                        tex['rep'] = dict(niltk)
                    else:
                        tex['rep'] = cexr

            elif te == 'ADJP':
                if child.elem in ['ADJP', 'JJ']:
                    tex['rep'] = cexr
            elif te == 'ADVP':
                if child.elem in ['ADVP', 'RB', 'RBR']:
                    tex['rep'] = cexr
            elif te == 'PP':
                if getq(child.elem) in ['VP', 'VB', 'NP', 'NN']:
                    tex['rep'] = cexr
            elif te == 'PRT':
                tex['rep']['l'] += cexr['l'] + ' '
            elif len(tree.children) == 1:
                tex['rep'] = cexr

        if tree.children[-1].elem == 'POS':
            tree.elem = 'PRP$'
            tex['rep'] = dict(niltk)


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
    amod = [qm if i in q['pos'] else '<a pos=%d href="#">' % i + qm + '</a>'
            for i, qm in enumerate(q['mod'])]
    title = ' '.join(q['mod'])
    if arg['type'] == 0:
        (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title,
                                   {'display': ' '.join(amod), 'pos': q['pos'], 'other': '_other_' in q['mod']})
        if flag:
            markSent = cleaned_sentence(arg['sent'], arg['keypos'])
            arg['strlist'].append({'sentence': markSent, 'sen': retId})
    elif arg['type'] == 1:
        if title == arg['title']:
            title = ' '.join(q['word'])
            (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title,
                                       {'display': title, 'pos': [], 'other': '_other_' in q['word']})
            if flag:
                markSent = cleaned_sentence(arg['sent'], arg['keypos'])
                arg['strlist'].append({'sentence': markSent, 'sen': retId})


def modeget(child, arg, q, ad=''):
    c = q['ch']
    c['v'] &= child.elem[0].isalpha()
    c['v'] &= child.elem not in ['MD', 'CC']
    c['w'] += 1
    e = child.elem
    pn = (len(q['mod']) == arg['nxt'])
    if len(q['mod']) == arg['nxt']:
        r = child.extra['rep']['l']
        if not r:
            r = '_other_'
    else:
        r = '_other_'
    if e in ['CD', 'PDT', 'QP', 'PRN', 'DT', 'PRP$', 'POS']:
        c['w'] -= 1
    elif ad == 'V N' and e in ['PRT']:
        c['w'] -= 1
        q['word'].append(child.extra['rep']['l'])
    elif ad == 'VBG' and e in ['VBG', 'VBN']:
        c['g'] |= 1
        q['mod'].append(e)
        q['word'].append(child.extra['rep']['t'] if pn else e)
    elif e in ['ADVP']:
        c['sv'] -= 1
        if c['sv'] >= 0:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r if pn else disp.get(e, e))
        else:
            c['w'] -= 1
    elif len(child.children) == 1 and len(child.children[0].children) == 0:
        tk = arg['tk'][int(child.children[0].elem)]['l']
        e = getq(child.elem)
        if e in ['IN', 'TO']:
            q['pos'].append(len(q['mod']))
            q['mod'].append(tk)
            q['word'].append(tk)
        elif e in ['NN', 'JJ']:
            if e == 'NN':
                c['sn'] -= 1
            if e == 'JJ':
                c['sj'] -= 1
                e = 'JJ'
            if c['sn'] >= 0 and c['sj'] >= 0:
                q['mod'].append(disp.get(e, e))
                q['word'].append(r if pn else disp.get(e, e))
            else:
                c['w'] -= 1
        elif ad == 'N V' and child.elem in ['VBG', 'VBN']:
            c['sj'] -= 1
            e = 'JJ'
            if c['sj'] >= 0:
                q['mod'].append(disp.get(e, e))
                q['word'].append(child.extra['rep']['t'] if pn else disp.get(e, e))
        elif e in ['RB']:
            if tk == 'not' or c['sv'] <= 0:
                c['w'] -= 1
            else:
                c['sv'] -= 1
                q['mod'].append(disp.get(e, e))
                q['word'].append(r if pn else disp.get(e, e))
        elif e in ['VB']:
            if tk in ['be']:
                c['w'] -= 1
            elif tk in ['have']:
                c['w'] -= 1
            else:
                q['mod'].append(disp.get(e, e))
                q['word'].append(r if pn else disp.get(e, e))
        else:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r if pn else disp.get(e, e))
    else:
        if e == 'ADJP':
            c['sj'] -= 1
        if c['sj'] >= 0:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r if pn else disp.get(e, e))
        else:
            c['w'] -= 1


def dfs_get(node, arg, q, ad, flag):
    comone = arg['common'].elem
    for child in node.children:
        if child.extra['tag'] == arg['tag']:
            if 'ansm' not in arg:
                if len(child.children) > 0:
                    dfs_get(child, arg, q, ad, flag)
                else:
                    q['pos'].append(len(q['mod']))
                    q['mod'].append(child.extra['rep']['l'])
                    q['word'].append(child.extra['rep']['l'])
            else:
                sub = arg['ansm']
                # q['mod'] += sub + '(%s) ' % arg['common'].elem
                lmod = len(q['mod'])
                q['pos'] += [lmod + i for i in arg['ansp']]
                q['mod'] += sub
                if child.elem == 'PP':
                    qmod = q['mod'][:]
                    qpos = q['pos'][:]
                    dfs_get(child, arg, q, '', flag)
                    q['mod'] = qmod[:]
                    q['pos'] = qpos[:]
                else:
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
            dfs_get(child, arg, q, 'VBG', flag)
        # PP extend
        elif child.elem in ['S'] and len(child.children) == 1 and child.children[0].elem == "VP":
            dfs_get(child.children[0], arg, q, 'VBG', flag)
        # S extend
        elif getq(comone) in ['NN', 'NP'] and child.elem in ['S', 'SBAR']:
            pass
        # N S forbid
        # elif comone in ['ADJP', 'JJ'] and child.elem in ['S', 'SBAR'] and q['ch']['w'] == 0:
        #    pass
        # J forbid
        elif child.elem in ['ADVP', 'RB', 'RBR']:
            if comone not in ['ADVP', 'RB', 'RBR']:
                flag['advp'] = True
        # ignore S after N
        else:
            modeget(child, arg, q, ad)
        if q['ch']['g'] > 0:
            break


def comnex_add(node, arg):
    q = {'mod': [], 'word': [], 'pos': [], 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
    comone = arg['common'].elem
    ad = ''
    ed = vm = br = False
    childe = [child.elem for child in node.children]
    if node.parent.elem == 'VP' and node.elem == 'VP':
        checkbe = node.parent.children[0].children
        ts = arg['common'].extra['rep']['p']
        if len(checkbe[0].children) == 0:
            wd = arg['tk'][int(checkbe[0].elem)]['l']
            if ts == 'VBN' and wd in ['be']:
                q['mod'].append('be')
                q['word'].append('be')
                ed = True
            # passive
            if ts == 'VBN' and wd in ['have'] or ts == 'VBG' and wd in ['be'] \
                    or ts == 'VB' and wd in ['will', 'would', 'to', 'do']:
                br = True
            # break later
    # verb example
    if node.elem in ['S', 'SBAR'] and ('ADJP' in childe or 'JJ' in childe):
        return 0
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
                q['mod'].append('be')
                q['word'].append('be')
    # be clear that
    if node.elem == 'PP':
        return 1 if getq(comone) in ['NN', 'NP'] else 0
    # search for key
    if node.elem == 'VP' and getq(comone) in ('NN', 'NP'):
        ad = 'V N'
    # cut down trees
    flag = {'edvm': ed or vm, 'advp': False}
    dfs_get(node, arg, q, ad, flag)
    if node == arg['common']:
        arg['ansm'] = q['mod']
        arg['answ'] = q['word']
        arg['ansp'] = q['pos']

    if (q['ch']['v'] and q['ch']['w'] > 0) or (node == arg['common'] and len(arg['keylm']) > 1):
        addResult(arg, q)

    if not ed and not vm and flag['advp'] and \
            (comone in ['VP', 'ADJP'] or getq(comone) in ['VB', 'JJ']):
        q = {'mod': [], 'word': [], 'pos': [], 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
        for child in node.children:
            if child.extra['tag'] == arg['tag']:
                sub = arg['ansm']
                # q['mod'] += sub + '(%s) ' % arg['common'].elem
                lmod = len(q['mod'])
                q['pos'] += [lmod + i for i in arg['ansp']]
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
    if not arg['common'].extra['rep']['l']:
        return
    node = arg['common']
    brk = 10
    while node.elem != '@':
        if node.extra['rep']['l'] not in arg['keylm']:
            brk = min(brk, 1)
        brk = min(brk - 1, comnex_add(node, arg))
        if brk == 0:
            return
        node = node.parent


def check_find(key, tokens, arg):
    iters = []
    for k in key:
        iterlist = []
        for i, t in enumerate(arg['tk']):
            if tokens[k]['lemma'] == t['l']:
                iterlist.append(i)
        iters.append(iterlist)

    get_root_tree(arg)
    TIMING[2] = time.time()
    CTIME[2] += TIMING[2] - TIMING[1]

    for tag, qkey in enumerate(product(*iters)):
        arg['keypos'] = qkey
        arg['keytk'] = [arg['tk'][k] for k in qkey]
        arg['keylm'] = [k['l'] for k in arg['keytk']]
        arg['tag'] = tag
        arg['common'] = find_common(arg)
        TIMING[3] = time.time()
        CTIME[3] += TIMING[3] - TIMING[2]
        comnex_find(arg)
        TIMING[2] = time.time()
        CTIME[4] += TIMING[2] - TIMING[3]


def result_part(retJson):
    if len(retJson['desc']['sen']) > 20:
        # retJson['desc']['sen'] = retJson['desc']['sen'][:20] + retJson['desc']['sen'][-1:]
        retJson['desc']['sen'] = retJson['desc']['sen'][:20]
        senlist = [sen['id'] for sen in retJson['desc']['sen']]
        retJson['result'] = [result for result in retJson['result'] if result['sen'] in senlist]


def get_comnex_db(tokens, key, args):
    global TIMING
    TIMING = [.0] * 7

    global CTIME
    CTIME = [.0] * 6
    TIMING[6] = time.time()
    retJson = {'result': [], 'desc': {'sen': []}}
    senmap = {}

    keys = [tokens[k]['lemma'] for k in key]
    keys.sort(key=lambda word: -len(word))
    rs = cl.find({'tokens.l': {'$all': keys}})
    TIMING[5] = time.time()
    CTIME[5] += TIMING[6] - TIMING[5]

    for sen in rs:
        tree0 = sen['tree0']
        tk = sen['tokens']
        TIMING[0] = time.time()
        CTIME[0] += TIMING[0] - TIMING[5]
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
        TIMING[1] = time.time()
        CTIME[1] += TIMING[1] - TIMING[0]
        check_find(key, tokens, arg)
        TIMING[5] = time.time()

    TIMING[6] = time.time()
    retJson['desc']['sen'].sort(key=lambda word: -word['count'] if not word['other'] else 0)
    result_part(retJson)
    CTIME[5] += time.time() - TIMING[5]
    print CTIME
    return retJson


def get_comnex_inter(sentence, key, ctype, nxt=-1):
    rquest = parse(sentence)
    tokens = rquest['sentences'][0]['tokens']

    return get_comnex_db(tokens, key, {'title': sentence, 'type': ctype, 'nxt': nxt})
