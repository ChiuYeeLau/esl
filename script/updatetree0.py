import re
import sys
from pymongo import MongoClient
from pprint import pprint

def state_update(state):
    if state[0] == 1:
        state[0] = 0
        state[1] += 1

if __name__ == '__main__':
    # fout = open("all.txt", "w")
    '''
    addr = sys.argv(1) if len(sys.argv) > 1 else '166.111.139.42'
    client = MongoClient(addr)
    db = client.test
    db.authenticate('test','test')
    posts = db.syntax
    '''
    addr = '127.0.0.1'
    db = MongoClient(addr).test
    db.authenticate('test','test')
    posts = db.syntax
    bulk = posts.initialize_unordered_bulk_op()

    cnt = 0
    for sen in posts.find():
        tk = sen['tokens']
        tr = sen['tree']
        i = 0

        ntr = ''
        tmp = ''
        state = [0, 0]
        for c in tr:
            if c == ')':
                if state[0] == 1:
                    ntr += str(state[1])
                    state[0] = 0
                    state[1] += 1
                ntr += ')'
                tmp = ''
            elif c == '(':
                ntr += tmp + '('
                state[0] = 1
                tmp = ''
            else:
                tmp += c

        bulk.find({'_id': sen['_id']}).update({'$set':{'tree0': ntr}})
        cnt += 1
        if cnt % 5000 == 0:
            print cnt
        if cnt % 100000 == 0:
            result = bulk.execute()
            pprint(result)
            bulk = posts.initialize_unordered_bulk_op()

    result = bulk.execute()
    pprint(result)

    db.logout()
