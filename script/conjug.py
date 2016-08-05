import json

def get_conjugate(word):
    word = word.lower()
    confile = open("newconjugate.json")
    condict = json.loads(confile.read())
    if condict.has_key(word):
        return condict.get(word)
    else:
        return None
