import requests
import json


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

def transfer_Node(text):
    level = 0
    tree_group = []
    i = 0
    word = ""
    for c in text:
        if level == 0:
            tree_group.append(Node("@"))
            root = tree_group[i]
            i += 1
        if c == '(':
            level += 1
            if word:
                root.elem = word
                word = ""
            root.children.append(Node(word, root, level))
            len_children = len(root.children)
            root = root.children[len_children - 1]
        elif c == ')':
            level -= 1
            if word:
                root.elem = word
                word = ""
            root = root.parent
        else:
            word += c
    return tree_group

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
    r = requests.post('http://166.111.139.15:9000/?properties%3d%7b%22annotators%22%3a%22tokenize%2cssplit%2cpos%2clemma%2cparse%22%2c%22outputFormat%22%3a%22json%22%7d%0a', data=s)
    return r.json()
"""sentence_input = raw_input("enter the sentence:")
request = parse(sentence_input)
print request["sentences"][0]['parse']"""
