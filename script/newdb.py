from pymongo import MongoClient


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
            if len(tokens) < 3:  # filter out fragments
                continue
            tokens = [_parse_token(t) for t in tokens]
            sentences.append((tokens, sentence, tree, deps))
        except Exception:
            print 'wrong: ', file
    return sentences


def _parse_token(s):
    # Text=? CharacterOffsetBegin=? CharacterOffsetEnd=? PartOfSpeech=? Lemma=?
    ss = s.split()
    text = ss[0][ss[0].find('=') + 1:]
    lemma = ss[4][ss[4].find('=') + 1:]
    pos = ss[3][ss[3].find('=') + 1:]
    if len(pos) < 2:
        qpos = pos
    else:
        qpos = pos[:2]
    return {'t': text, 'p': pos, 'l': lemma, 'q': qpos}


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
    

def make_tree0(tr):
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
    
    return ntr


if __name__ == '__main__':
    fin = open("index.txt", "r")

    addr = '127.0.0.1'
    db = MongoClient(addr).test
    db.authenticate('test', 'test')
    posts = db.syntax2

    text = fin.read()
    index = text.split()
    info = []
    cnt = 0
    for file in index:
        fin1 = open(file, "r")
        text1 = fin1.read()
        print file
        sentences = parse_text_file(file, text1)
        cnt += 1
        for s in sentences:
            tr = make_tree(s[2])
            ntr = make_tree0(tr)
            info.append({'tokens': s[0], 'sentence': s[1], 'tree': tr, 'tree0': ntr, 'deps': s[3]})
            # print info[-1]

        if cnt % 20 == 0 and len(info) > 0:
            posts.insert_many(info)
            info = []
            print 'insert'
        fin1.close()
    
    if len(info) > 0:
        posts.insert_many(info)
        print 'insert'

    # db.logout()
