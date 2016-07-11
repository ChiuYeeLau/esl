import requests

# NLP_SERVER = '166.111.139.15:9000'
NLP_SERVER = 'localhost:9000'


class Node(object):
    def __init__(self, elem="", parent=None, depth=-1):
        self.elem = elem
        self.children = []
        self.parent = parent
        self.size = 1
        self.depth = depth


class Tree(object):
    def __init__(self):
        self.root = Node()


def tree_structure_to_json(root):
    if root.elem == "":
        return
    else:
        print '{'
        print "\"name\":\"" + root.elem + "\","
        print "\"size\":\"", root.size, "\""

        len_children = len(root.children)
        if len_children == 0:
            print "}"
        else:
            print ","
            print "\"children\":["
            count = 0
            for child in root.children:
                tree_structure_to_json(child)
                count += 1
                if count != len_children:
                    print ","
                else:
                    print "]}"


def transfer_Node_i(text):
    level = 0
    tree = Node("_ROOT_")
    root = tree
    word = ""
    leaflist = []
    for c in text:
        if level == 0:
            tree.children.append(Node("@"))
            root = tree.children[-1]
        if c == '(':
            level += 1
            if word:
                root.elem = word
                word = ""
            p = Node(word, root, level)
            root.children.append(p)
            root = p
        elif c == ')':
            level -= 1
            if word:
                root.elem = len(leaflist)
                leaflist.append(root)
                word = ""
            root = root.parent
        else:
            word += c
    return (tree.children[0], leaflist)


def transfer_Node(text):
    level = 0
    tree = Node("_ROOT_")
    root = tree
    word = ""
    for c in text:
        if level == 0:
            tree.children.append(Node("@"))
            root = tree.children[-1]
        if c == '(':
            level += 1
            if word:
                root.elem = word
                word = ""
            p = Node(word, root, level)
            root.children.append(p)
            root = p
        elif c == ')':
            level -= 1
            if word:
                root.elem = word
                word = ""
            root = root.parent
        else:
            word += c
    return tree.children[0]


def tree_transfer(text):
    '''
    tmp = ""
    stack = []
    stacko = []
    answer = ["id"]
    for c in text:
        if c in ("(", ")"):
            if tmp != "":
                if len(stack) != 0:
                    node = stack[-1]
                    if tmp not in node[1]:
                        node[1][tmp] = 0
                    else:
                        node[1][tmp] += 1
                    if tmp == node[0] and node[1][tmp] == node[2]:
                        node[1][tmp] += 1
                    node = [tmp, {tmp : -1}, node[1][tmp]]
                else:
                    node = [tmp, {tmp : -1}, 0]
                stack.append(node)
                if node[2] != 0:
                    stacko.append(tmp + str(node[2]))
                else:
                    stacko.append(tmp)
                answer.append("@".join(stacko))
                tmp = ""
        else:
            tmp += c
        if c == ")":
            stack.pop()
            stacko.pop()
    '''
    tmp = ""
    stack = []
    cnt = {}
    answer = ["id"]
    for c in text:
        if c in ("(", ")"):
            if tmp != "":
                if tmp == ',':
                    tmp = '_comma_'
                if c == ')':
                    stack.append(tmp)
                else:
                    if tmp not in cnt:
                        cnt[tmp] = 0
                    else:
                        cnt[tmp] += 1
                    stack.append(tmp + str(cnt[tmp]))
                answer.append("@".join(stack))
                tmp = ""
        else:
            tmp += c
        if c == ")":
            stack.pop()
    return ",\n".join(answer) + '\n'


def tree_format(s):
    state = 0
    q = []
    for c in s:
        if c == '(':
            state = 1
        elif c == ')':
            if state == 3:
                q.append(')')
            state = 0
        elif ord(c) <= 32:
            if state == 1:
                state = 2
        else:
            if state == 2:
                state = 3
                q.append('(')
        if ord(c) > 32:
            q.append(c)

    return ''.join(q)


def parse(s):
    r = requests.post('http://' + NLP_SERVER + '/?properties%3d%7b%22annotators%22%3a%22tokenize%2cssplit%2cpos%2clemma%2cparse%22%2c%22outputFormat%22%3a%22json%22%7d%0a', data=s)
    return r.json()
"""sentence_input = raw_input("enter the sentence:")
request = parse(sentence_input)
print request["sentences"][0]['parse']"""
