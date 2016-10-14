#!/usr/bin/env python
# encoding: utf-8

# import json
import requests
from itertools import izip
from search.parse import parse
from search.clean_sentence import cleaned_sentence
from django.conf import settings

ADDR = settings.ADDR
ROWS = 1000


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


def addResult(arg, res, pos):
    qpos = [i for i, qm in enumerate(res) if not qm.isupper()]
    amod = [qm if i in qpos else '<a pos=%d href="#">' % i + qm + '</a>'
            for i, qm in enumerate(res)]
    title = ' '.join(res)
    (retId, flag) = addCluster(arg['senmap'], arg['senlist'], title,
                               {'display': ' '.join(amod), 'pos': qpos, 'other': '_other_' in res})
    if flag:
        pos = [i for i in pos if 0 <= i and i < len(arg['sent'])]
        markSent = cleaned_sentence(arg['sent'], pos)
        arg['strlist'].append({'sentence': markSent, 'sen': retId})


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
    t1key = args['title']
    keys.sort(key=lambda word: -len(word))
    sents = '+AND+'.join(keys)
    cnt = 0

    while True:
        rs = requests.get('http://%s:8983/solr/syntax/select?q=res2:%s&wt=json&start=%d&rows=%d' % (ADDR, sents, cnt, ROWS))
        cnt += ROWS
        rs = rs.json()['response']['docs']
        if len(rs) == 0:
            break

        for sen in rs:
            res1 = sen['res1']
            res2 = sen['res2']
            res3 = sen['res3']
            sent = sen['sent'].split()
            arg = dict({
                'senmap': senmap,
                'senlist': retJson['desc']['sen'],
                'strlist': retJson['result'],
                'sent': sent,
            }, **args)
            for res in izip(res1, res2, res3):
                nrs = [[], [], []]
                nrs[0] = res[0].split()
                nrs[1] = res[1].split()
                nrs[2] = [int(ps) for ps in res[2].split()]
                # if arg['type'] == 1 and t1key == res[0]:
                #     addResult(arg, nrs[1], nrs[2])
                if arg['type'] in [0, 1]:
                    adr, adr2 = [], []
                    adp = []
                    cc = 0
                    for i, rs in enumerate(izip(nrs[0], nrs[1], nrs[2])):
                        if rs[1] in keys:
                            adr.append(rs[1])
                            adr2.append(rs[1])
                            adp.append(rs[2])
                            cc += 1
                        else:
                            adr.append(rs[0])
                            if i == arg['nxt']:
                                adr2.append(rs[1])
                                adp.append(rs[2])
                            else:
                                adr2.append(rs[0])
                    if cc == len(keys):
                        if arg['type'] == 1 and ' '.join(adr) == t1key:
                            addResult(arg, adr2, adp)
                        elif arg['type'] == 0:
                            addResult(arg, adr, adp)

    retJson['desc']['sen'].sort(key=lambda word: -word['count'] if not word['other'] else 0)
    result_part(retJson)
    return retJson


def get_ftree2_inter(sentence, key, ctype, nxt=-1):
    rquest = parse(sentence)
    tokens = rquest['sentences'][0]['tokens']

    return get_comnex_db(tokens, key, {'title': sentence, 'type': ctype, 'nxt': nxt})
