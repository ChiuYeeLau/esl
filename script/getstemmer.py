import json
import commands
from itertools import imap
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def state_update(state):
    if state[0] == 1:
        state[0] = 0
        state[1] += 1


def process_list(ulist, st=False):
    if len(ulist) > 50 or st and ulist:
        rs = commands.getoutput('java -cp stanford-corenlp.jar edu.stanford.nlp.process.Stemmer %s' % ' '.join(ulist))[:-1]
        rslist = rs.split(' ')
        if len(rslist) != len(ulist):
            print rslist, ulist
            print 'fatal'
            exit()
        for t, s in imap(None, ulist, rslist):
            stemmerDict[t] = s
        del ulist[:]


def process_splist(splist, st=False):
    if len(splist) > 50 or st and splist:
        stlist = []
        for sp in splist:
            if "'" not in sp:
                stlist.append("'" + sp + "'")
            else:
                stlist.append('"' + sp + '"')
        rs = commands.getoutput('java -cp stanford-corenlp.jar edu.stanford.nlp.process.Stemmer %s' % ' '.join(stlist))[:-1]
        rslist = rs.split(' ')
        if len(rslist) != len(splist):
            print rslist, splist
            print 'fatal'
            exit()
        for t, s in imap(None, splist, rslist):
            stemmerDict[t] = s
        del splist[:]

if __name__ == '__main__':
    addr = '127.0.0.1'
    db = MongoClient(addr).test
    db.authenticate('test', 'test')
    posts = db.syntax2

    f = open('stemmer.json', 'w')
    stemmerDict = {}

    cnt = 0
    ulist, splist = [], []
    for sen in posts.find():
        tk = sen['tokens']
        for ti in tk:
            if ti['l'] not in stemmerDict:
                if ti['l'].isalpha():
                    ulist.append(ti['l'])
                # else:
                #    splist.append(ti['l'])

        process_list(ulist)
        process_splist(splist)

        cnt += 1
        if cnt % 1000 == 0:
            print cnt

    process_list(ulist, True)
    process_splist(splist, True)
    f.write(json.dumps(stemmerDict))
    db.logout()
