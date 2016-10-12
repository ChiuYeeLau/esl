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
            index, sentence, tokens = tuple(lines[0:3])
            tree = ending.join(lines[3:])
            tokens = tokens[tokens.find('[') + 1:tokens.rfind(']')].split('] [')
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
    c['v'] &= child['e'][0].isalpha()
    c['v'] &= child['e'] not in ['MD', 'CC']
    c['w'] += 1
    e = child['e']
    r = tks[child['x']['r']][1]
    if not r:
        r = '_other_'
    if e in ['CD', 'PDT', 'QP', 'PRN', 'DT', 'PRP$', 'POS']:
        c['w'] -= 1
    elif ad == 'V N' and e in ['PRT']:
        c['w'] -= 1
        q['word'].append(tks[child['x']['r']][1])
    elif ad == 'VBG' and e in ['VBG', 'VBN']:
        c['g'] |= 1
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
        tk = arg['tk'][int(arg['tree'][child['c'][0]]['e'])][1]
        e = getq(child['e'])
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
                q['word'].append(r)
            else:
                c['w'] -= 1
        elif ad == 'N V' and child['e'] in ['VBG', 'VBN']:
            c['sj'] -= 1
            e = 'JJ'
            if c['sj'] >= 0:
                q['mod'].append(disp.get(e, e))
                q['word'].append(tks[child['x']['r']][0])
        elif e in ['RB']:
            if tk == 'not' or c['sv'] <= 0:
                c['w'] -= 1
            else:
                c['sv'] -= 1
                q['mod'].append(disp.get(e, e))
                q['word'].append(r)
        elif e in ['VB']:
            if tk in ['be']:
                c['w'] -= 1
            elif tk in ['have']:
                c['w'] -= 1
            else:
                q['mod'].append(disp.get(e, e))
                q['word'].append(r)
        else:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r)
    else:
        if e == 'ADJP':
            c['sj'] -= 1
        if c['sj'] >= 0:
            q['mod'].append(disp.get(e, e))
            q['word'].append(r)
        else:
            c['w'] -= 1


def dfs_get(node, arg, q, ad, flag):
    comone = arg['common']['e']
    tree = arg['tree']
    tk = arg['tk']
    for i_child in node['c']:
        child = tree[i_child]
        if child['x'].get('tag', -1) == arg['tag']:
            if not arg['ansm']:
                if len(child['c']) > 0:
                    dfs_get(child, arg, q, ad, flag)
                else:
                    q['pos'].append(len(q['mod']))
                    q['mod'].append(tk[child['x']['r']][1])
                    q['word'].append(tk[child['x']['r']][1])
            else:
                sub = arg['ansm']
                # q['mod'] += sub + '(%s) ' % arg['common']['e']
                lmod = len(q['mod'])
                q['pos'] += [lmod + i for i in arg['ansp']]
                q['mod'] += sub
                if child['e'] == 'PP':
                    qmod = q['mod'][:]
                    qpos = q['pos'][:]
                    dfs_get(child, arg, q, '', flag)
                    q['mod'] = qmod[:]
                    q['pos'] = qpos[:]
                else:
                    q['word'] += sub
        # the common node
        elif getq(comone) in ['NN', 'NP'] and child['e'] == 'VP':
            q['ch']['v'] &= not checkbe(node, arg)
        elif comone in ['ADVP', 'RB', 'RBR'] and \
                (getq(child['e']) not in ['VB', 'VP', 'JJ'] and child['e'] not in ['ADJP']):
            pass
        elif child['e'] == 'PP':
            dfs_get(child, arg, q, 'VBG', flag)
        # PP extend
        elif child['e'] in ['S'] and len(child['c']) == 1 and tree[child['c'][0]]['e'] == "VP":
            dfs_get(tree[child['c'][0]], arg, q, 'VBG', flag)
        # S extend
        elif getq(comone) in ['NN', 'NP'] and child['e'] in ['S', 'SBAR']:
            pass
        # N S forbid
        # elif comone in ['ADJP', 'JJ'] and child['e'] in ['S', 'SBAR'] and q['ch']['w'] == 0:
        #    pass
        # J forbid
        elif child['e'] in ['ADVP', 'RB', 'RBR']:
            if comone not in ['ADVP', 'RB', 'RBR']:
                flag['advp'] = True
        # ignore S after N
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
        return wd in ['be']
    else:
        return False


def comnex_add(node, arg):
    q = {'mod': [], 'word': [], 'pos': [], 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
    comone = arg['common']['e']
    tree = arg['tree']
    ad = ''
    ed = vm = br = False
    childe = [tree[child]['e'] for child in node['c']]
    if tree[node['p']]['e'] == 'VP' and node['e'] == 'VP':
        cb = tree[tree[tree[node['p']]['c'][0]]['c'][0]]
        if len(cb['c']) == 0:
            wd = arg['tk'][int(cb['e'])][1]
            if wd in ['be']:
                q['pos'].append(len(q['mod']))
                q['mod'].append('be')
                q['word'].append('be')
                ed = True
            # passive
            # if ts == 'VBN' and wd in ['have'] or ts == 'VBG' and wd in ['be'] \
            #        or ts == 'VB' and wd in ['will', 'would', 'to', 'do']:
            if wd in ['have', 'be', 'will', 'would', 'to', 'do']:
                br = True
            # break later
    # verb example
    if node['e'] in ['S', 'SBAR'] and ('ADJP' in childe or 'JJ' in childe):
        return 0
    # make it clear (that)
    if comone in ['ADJP', 'JJ']:
        q['ch']['sj'] -= 1
    if node['e'] == 'NP':
        if getq(comone) in ['NN', 'NP']:
            q['ch']['sn'] -= 1
            ad = 'N V'
        # complicate NP
        if getq(comone) in ['VB', 'VP']:
            vm = True
        # keep the tense
    if node['e'] == 'ADJP' and comone in ['ADJP', 'JJ'] and tree[node['p']]['e'] == 'VP':
        if checkbe(node, arg):
            q['pos'].append(len(q['mod']))
            q['mod'].append('be')
            q['word'].append('be')
    # be clear that
    if node['e'] == 'PP':
        return 1 if getq(comone) in ['NN', 'NP'] else 0
    # search for key
    if node['e'] == 'VP' and getq(comone) in ('NN', 'NP'):
        ad = 'V N'
    # cut down trees
    flag = {'edvm': ed or vm, 'advp': False}
    dfs_get(node, arg, q, ad, flag)
    if node == arg['common']:
        arg['ansm'] = q['mod']
        arg['answ'] = q['word']
        arg['ansp'] = q['pos']

    if (q['ch']['v'] and q['ch']['w'] > 0) or (node == arg['common'] and len(arg['keylm']) > 1):
        arg['strlist1'].append(' '.join(q['mod']))
        arg['strlist2'].append(' '.join(q['word']))

    if not ed and not vm and flag['advp'] and \
            (comone in ['VP', 'ADJP'] or getq(comone) in ['VB', 'JJ']):
        q = {'mod': [], 'word': [], 'pos': [], 'ch': {'v': True, 'w': 0, 'g': 0, 'sn': 1, 'sj': 1, 'sv': 1}}
        for i_child in node['c']:
            child = tree[i_child]
            if child['x'].get('tag', -1) == arg['tag']:
                sub = arg['ansm']
                # q['mod'] += sub + '(%s) ' % arg['common']['e']
                lmod = len(q['mod'])
                q['pos'] += [lmod + i for i in arg['ansp']]
                q['mod'] += sub
                q['word'] += sub
            elif child['e'] in ['ADVP', 'RB', 'RBR']:
                modeget(child, arg, q)
            else:
                pass
        if q['ch']['v'] and q['ch']['w'] > 0:
            arg['strlist1'].append(' '.join(q['mod']))
            arg['strlist2'].append(' '.join(q['word']))

    return 0 if ed or vm or br else 100


def comnex_find(arg):
    # print arg['common']['e']
    if not arg['tk'][arg['common']['x']['r']][0]:
        return
    node = arg['common']
    brk = 10
    while node['e'] != '@':
        if arg['tk'][node['x']['r']][1] not in arg['keylm']:
            brk = min(brk, 1)
        brk = min(brk - 1, comnex_add(node, arg))
        if brk == 0:
            return
        node = arg['tree'][node['p']]


def check_find(arg):
    for tag in range(len(arg['tk']) - 1):
        qkey = [tag]
        arg['keypos'] = qkey
        arg['keytk'] = [arg['tk'][k] for k in qkey]
        arg['keylm'] = [k[1] for k in arg['keytk']]
        arg['ansm'] = ''
        arg['answ'] = ''
        arg['ansp'] = ''
        arg['tag'] = tag
        node = arg['nodes'][qkey[0]]
        arg['common'] = arg['tree'][node['p']]
        if getq(arg['common']['e']) not in ['NN', 'JJ', 'RB', 'VB']:
            continue
        if arg['keylm'][0] in ['be']:
            continue
        while node['p'] != -1:
            node['x']['tag'] = tag
            node = arg['tree'][node['p']]
        comnex_find(arg)


def mongo_start():
    fin = open("../parsed/index.txt", "r")

    text = fin.read()
    index = text.split()
    cnt = 0
    db = MongoClient("127.0.0.1", 27017).test
    db.authenticate("test", "test")
    cl = db.syntax3
    bulk = cl.initialize_unordered_bulk_op()

    for file in index:
        fin1 = open("../parsed/" + file, "r")
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

            retJson = {'r1': [], 'r2': []}
            arg = dict({
                'tk': tk,
                'tree': tree1,
                'nodes': leaf,
                'strlist1': retJson['r1'],
                'strlist2': retJson['r2'],
            })
            check_find(arg)
            bulk.insert({'sent': s[0], 'res1': retJson['r1'], 'res2': retJson['r2']})

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

            retJson = {'r1': [], 'r2': []}
            arg = dict({
                'tk': tk,
                'tree': tree1,
                'nodes': leaf,
                'strlist1': retJson['r1'],
                'strlist2': retJson['r2'],
            })
            check_find(arg)
            info.append({'sent': s[0], 'res1': retJson['r1'], 'res2': retJson['r2']})

        cnt += 1
        if cnt % 100 == 0:
            # break
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
