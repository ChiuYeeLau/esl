import re
import sys
from pymongo import MongoClient
from pprint import pprint

def state_update(state):
    if state[0] == 1:
        state[0] = 0
        state[1] += 1

if __name__ == '__main__':
    addr = '127.0.0.1'
    db = MongoClient(addr).test
    db.authenticate('test','test')
    posts = db.syntax
    bulk = posts.initialize_unordered_bulk_op()

    cnt = 0
    for sen in posts.find():
        tk = sen['tokens']
        for ti in tk:
            st = ti['p']
            if len(st) < 2:
                ti['q'] = st
            else:
                ti['q'] = st[:2]

        bulk.find({'_id': sen['_id']}).update({'$set':{'tokens': tk}})
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
