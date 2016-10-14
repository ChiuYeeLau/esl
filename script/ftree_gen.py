#!/usr/bin/env python
# encoding: utf-8

import json
import sys
from pprint import pprint
from pymongo import MongoClient

disp = {'SBAR': 'S', 'ADVP': 'ADV', 'ADJP': 'ADJ', 'JJ': 'ADJ', 'RB': 'ADV',
        'NN': 'N', 'NP': 'N', 'VP': 'V', 'VB': 'V'}
niltk = -1


def getq(s):
    return s[:2] if len(s) > 2 else s


def node_dict(elem="", parent=-1, depth=-1):
    return {
        'e': elem,
        'c': [],
        'p': parent,
        'd': depth,
        'x': {}
    }


def dfs_root_tree(tl, node, tk):
    tree = tl[node]
    for child in tree['c']:
        dfs_root_tree(tl, child, tk)
    if len(tree['c']) == 0:
        tree['x']['r'] = int(tree['e'])
    elif len(tl[tree['c'][0]]['c']) == 0:
        tree['x']['r'] = tl[tree['c'][0]]['x']['r']
    else:
        tree['x']['r'] = niltk
        tex = tree['x']
        te = tree['e']
        stat = [0] * 5
        for ci in tree['c']:
            child = tl[ci]
            cexr = child['x']['r']
            if te == 'NP':
                if getq(child['e']) in ['NN', 'NP']:
                    tex['r'] = cexr
                elif child['e'] == 'PP':
                    c = tl[child['c'][0]]
                    if c['e'] == 'IN':
                        tkcc = tk[int(tl[c['c'][0]]['e'])][1]
                        if tkcc == 'of':
                            tex['r'] = niltk
            elif te == 'VP':
                if child['e'] == 'TO':
                    stat[0] = 1
                elif getq(child['e']) == 'VB':
                    tex['r'] = cexr
                    tkc = tk[int(tl[child['c'][0]]['e'])][1]
                    if tkc == 'have':
                        stat[0] = 2
                    elif tkc == 'be':
                        stat[0] = 3
                    elif tkc == 'do':
                        stat[0] = 4
                elif child['e'] == 'MD':
                    tkc = tk[int(tl[child['c'][0]]['e'])][1]
                    if tkc in ['will', 'would']:
                        stat[0] = 5
                elif child['e'] == 'VP':
                    tex['r'] = cexr
            elif te == 'ADJP':
                if child['e'] in ['ADJP', 'JJ']:
                    tex['r'] = cexr
            elif te == 'ADVP':
                if child['e'] in ['ADVP', 'RB', 'RBR']:
                    tex['r'] = cexr
            elif te == 'PP':
                if getq(child['e']) in ['VP', 'VB', 'NP', 'NN']:
                    tex['r'] = cexr
            elif te == 'PRT':
                tex['r'] = cexr
            elif len(tree['c']) == 1:
                tex['r'] = cexr

        if tl[tree['c'][-1]]['e'] == 'POS':
            tree['e'] = 'PRP$'
            tex['r'] = niltk


def transfer_Tree(text):
    level = 0
    treelist = []
    leaflist = []
    treelist.append(node_dict("@", -1, 0))
    root = 0
    word = ""
    for c in text:
        if c == '(':
            level += 1
            if word:
                treelist[root]['e'] = word
                word = ""
            treelist.append(node_dict("", root, level))
            p = len(treelist) - 1
            treelist[root]['c'].append(p)
            root = p
        elif c == ')':
            level -= 1
            if word:
                treelist[root]['e'] = len(leaflist)
                leaflist.append(root)
                word = ""
            root = treelist[root]['p']
        else:
            word += c
    return (treelist, leaflist)


def parse_text_file(file, s):
    sentences = []
    ending = '\n'
    l = [p for p in s.split('\n' + 'Sentence #') if p]
    # print len(l)
    for p in l:
        try:
            lines, deps = tuple(p.split(ending * 2)[:2])
            # lines = tuple(p.split('\n\n')[0])
            lines = lines.split('\n')
            index, sentence = tuple(lines[0:2])
            i = 2
            tokens = []
            while lines[i][0] == '[':
                tokens.append(lines[i][1:-1])
                i += 1
            tree = ending.join(lines[i:])
            if len(tokens) <= 3 or len(tokens) > 50:  # filter out fragments
                continue
            tokens = [_parse_token(t) for t in tokens]
            sentences.append((sentence, tokens, tree))
        except Exception:
            print 'wrong: ', file
    return sentences


def _parse_token(s):
    # Text=? CharacterOffsetBegin=? CharacterOffsetEnd=? PartOfSpeech=? Lemma=?
    ss = s.split()
    text = ss[0][ss[0].find('=') + 1:]
    lemma = ss[4][ss[4].find('=') + 1:]
    return (text, lemma)


def make_tree(s):
    state = 0
    q = ''
    for c in s:
        if c == '(':
            state = 1
        elif c == ')':
            if state == 3:
                q += ')'
            state = 0
        elif ord(c) <= 32:
            if state == 1:
                state = 2
        else:
            if state == 2:
                state = 3
                q += '('
        if ord(c) > 32:
            q += c

    return q


def make_whole_tree(s, tk):
    tree = transfer_Tree(make_tree(s))[0]
    dfs_root_tree(tree, 0, tk)
    return tree


def modeget(child, arg, q, ad=''):
    tks = arg['tk']
    c = q['ch']
    c['v'] &= child['e'] not in ['MD', 'CC']
    c['w'] += 1
    e = child['e']
    r = tks[child['x']['r']][1]
    rp = child['x']['r']
    if not r:
        r = '_other_'
    if not child['e'][0].isalpha():
        c['w'] -= 1
    elif e in ['CD', 'PDT', 'QP', 'PRN', 'DT', 'PRP$', 'POS']:
        c['w'] -= 1
    elif ad == 'V N' and e in ['PRT']:
        c['w'] -= 1
        q['pos'].append(child['x']['r'])
        q['word'].append(tks[child['x']['r']][1])
    elif ad == 'VBG' and e in ['VBG', 'VBN']:
        c['g'] |= 1
        q['pos'].append(child['x']['r'])
        q['mod'].append(e)
        q['word'].append(tks[child['x']['r']][0])
    elif e in ['ADVP']:
        c['sv'] -= 1
        if c['sv'] >= 0:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r)
        else:
            c['w'] -= 1
    elif len(child['c']) == 1 and len(arg['tree'][child['c'][0]]['c']) == 0:
        tkp = int(arg['tree'][child['c'][0]]['e'])
        tk = arg['tk'][tkp][1]
        e = getq(child['e'])
        if e in ['IN', 'TO']:
            q['pos'].append(tkp)
            q['mod'].append(tk)
            q['word'].append(tk)
        elif e in ['NN', 'JJ']:
            if e == 'NN':
                c['sn'] -= 1
            if e == 'JJ':
                c['sj'] -= 1
                e = 'JJ'
            if c['sn'] >= 0 and c['sj'] >= 0:
                q['pos'].append(rp)
                q['mod'].append(disp.get(e, e))
                q['word'].append(r)
            else:
                c['w'] -= 1
        elif ad == 'N V' and child['e'] in ['VBG', 'VBN']:
            c['sj'] -= 1
            e = 'JJ'
            if c['sj'] >= 0:
                q['pos'].append(child['x']['r'])
                q['mod'].append(disp.get(e, e))
                q['word'].append(tks[child['x']['r']][0])
        elif e in ['RB']:
            if tk == 'not' or c['sv'] <= 0:
                c['w'] -= 1
            else:
                c['sv'] -= 1
                q['pos'].append(rp)
                q['mod'].append(disp.get(e, e))
                q['word'].append(r)
        elif e in ['VB']:
            if tk in ['be']:
                c['w'] -= 1
            elif tk in ['have']:
                c['w'] -= 1
            else:
                q['pos'].append(rp)
                q['mod'].append(disp.get(e, e))
                q['word'].append(r)
        else:
            q['pos'].append(rp)
            q['mod'].append(disp.get(e, e))
            q['word'].append(r)
    else:
        if e == 'ADJP':
            c['sj'] -= 1
        if c['sj'] >= 0:
            q['pos'].append(rp)
            q['mod'].append(disp.get(e, e))
            q['word'].append(r)
        else:
            c['w'] -= 1


def dfs_get(node, arg, q, ad, flag):
    tree = arg['tree']
    for i_child in node['c']:
        child = tree[i_child]
        # the common node
        if child['e'] == 'PP':
            dfs_get(child, arg, q, 'VBG', flag)
        # PP extend
        elif child['e'] in ['S'] and len(child['c']) == 1 and tree[child['c'][0]]['e'] == "VP":
            dfs_get(tree[child['c'][0]], arg, q, 'VBG', flag)
        # S extend
        elif node['e'] == 'NP' and child['e'] in ['S', 'SBAR']:
            pass
        else:
            modeget(child, arg, q, ad)
        if q['ch']['g'] > 0:
            break


def checkbe(node, arg):
    tree = arg['tree']
    checkbe = tree[tree[tree[node['p']]['c'][0]]['c'][0]]
    # ts = tk[arg['common']['x']['r']]['p']
    if len(checkbe['c']) == 0:
        wd = arg['tk'][int(checkbe['e'])][1]
        # if ts == 'VBN' and wd in ['be']:
        return (wd in ['be'], int(checkbe['e']))
    else:
        return (False, -1)


def comnex_add(node, arg):
    q = {'mod': [], 'word': [], 'pos': [], 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
    tree = arg['tree']
    ad = ''
    ed = vm = br = False
    childe = [tree[child]['e'] for child in node['c']]
    if tree[node['p']]['e'] == 'VP' and node['e'] == 'VP':
        cb = tree[tree[tree[node['p']]['c'][0]]['c'][0]]
        if len(cb['c']) == 0:
            pos = int(cb['e'])
            wd = arg['tk'][pos][1]
            if wd in ['be']:
                q['pos'].append(pos)
                q['mod'].append('be')
                q['word'].append('be')
                ed = True
            if wd in ['have', 'be', 'will', 'would', 'to', 'do']:
                br = True
            # break later
    # verb example
    qn = node['e']
    q['node'] = qn

    if qn in ['S', 'SBAR'] and ('ADJP' in childe or 'JJ' in childe):
        return 0
    # make it clear (that)

    if qn == 'ADJP' and tree[node['p']]['e'] == 'VP':
        ber = checkbe(node, arg)
        if ber[0]:
            q['pos'].append(ber[1])
            q['mod'].append('be')
            q['word'].append('be')
    # be clear that
    if qn == 'PP':
        return 0
    # search for key
    flag = {'edvm': ed or vm, 'advp': False}
    dfs_get(node, arg, q, ad, flag)
    if q['ch']['v'] and q['ch']['w'] > 1:
        arg['strlist1'].append(' '.join(q['mod']))
        arg['strlist2'].append(' '.join(q['word']))
        arg['strlist3'].append(' '.join(str(ps) for ps in q['pos']))

    return 0 if ed or vm or br else 100


def dfs_find(node, arg):
    tree = arg['tree']
    for child in node['c']:
        dfs_find(tree[child], arg)
    if len(node['c']) == 0 or len(node['c']) == 1 and len(tree[node['c'][0]]['c']) == 0:
        pass
    else:
        comnex_add(node, arg)


def check_find(arg):
    dfs_find(arg['tree'][0], arg)


def mongo_start():
    fin = open(sys.argv[2], "r")

    text = fin.read()
    index = text.split()
    cnt = 0
    db = MongoClient("127.0.0.1", 27017).test
    db.authenticate("test", "test")
    cl = db.syntax3
    bulk = cl.initialize_unordered_bulk_op()

    for file in index:
        fin1 = open(file, "r")
        text1 = fin1.read()
        print file
        sentences = parse_text_file(file, text1)

        for s in sentences:
            tree1 = make_whole_tree(s[2], s[1])
            tk = s[1]
            tk.append(('', ''))
            leaf = []
            for i, node in enumerate(tree1):
                if len(node['c']) == 0:
                    leaf.append(node)

            retJson = {'r1': [], 'r2': [], 'r3': []}
            arg = dict({
                'tk': tk,
                'tree': tree1,
                'nodes': leaf,
                'strlist1': retJson['r1'],
                'strlist2': retJson['r2'],
                'strlist3': retJson['r3'],
            })
            check_find(arg)
            bulk.insert({'sent': s[0], 'res1': retJson['r1'], 'res2': retJson['r2'], 'res3': retJson['r3']})

        cnt += 1
        if cnt % 100 == 0:
            # break
            result = bulk.execute()
            pprint(result)
            bulk = cl.initialize_unordered_bulk_op()

    result = bulk.execute()
    pprint(result)

    db.logout()


def solr_start():
    fin = open(sys.argv[2], "r")

    text = fin.read()
    index = text.split()
    cnt = 0
    cnt2 = 0
    info = []

    for file in index:
        fin1 = open(file, "r")
        text1 = fin1.read()
        print file
        sentences = parse_text_file(file, text1)

        for s in sentences:
            tree1 = make_whole_tree(s[2], s[1])
            tk = s[1]
            tk.append(('', ''))
            leaf = []
            for i, node in enumerate(tree1):
                if len(node['c']) == 0:
                    leaf.append(node)

            retJson = {'r1': [], 'r2': [], 'r3': []}
            arg = dict({
                'tk': tk,
                'tree': tree1,
                'nodes': leaf,
                'strlist1': retJson['r1'],
                'strlist2': retJson['r2'],
                'strlist3': retJson['r3'],
            })
            check_find(arg)
            info.append({'sent': s[0], 'res1': retJson['r1'], 'res2': retJson['r2'], 'res3': retJson['r3']})

        cnt += 1

        if cnt % 100 == 0:
            cnt2 += 1
            fout = open("totalsolr/solr%s.json" % cnt2, "w")
            fout.write(json.dumps(info))
            fout.close()
            info = []

    cnt2 += 1
    fout = open("totalsolr/solr%s.json" % cnt2, "w")
    fout.write(json.dumps(info))
    fout.close()


if len(sys.argv) != 3:
    print 'Usage: python ftree_gen.py <solr/mongo> <index_file>'
    exit()
if sys.argv[1] == "solr":
    solr_start()
elif sys.argv[1] == "mongo":
    mongo_start()
