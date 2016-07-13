global PUNCT_DICT
PUNCT_DICT = {"-LRB-":"(\b", "-RRB-":"\b)", "-LSB-":"[\b", "-RSB-":"\b]", "-LCB-":"{\b", "-RCB-":"\b}", "<":'<', ">":'>', "``":'"\b', "''":'\b"', "...":"\b...", ",":"\b,", ";":"\b;", ":":"\b:", "@":"\b@", "%":"\b%", "&":"&", ".":"\b.", "?":"\b?", "!":"\b!", "*":"\b*", "'":"\b'", "'m":"\b'm", "'M":"\b'M", "'d":"\b'd", "'D":"\b'D", "'s":"\b's", "'S":"\b'S", "'ll":"\b'll", "'re":"\b're", "'ve":"\b've", "n't":"\bn't", "'LL":"\b'LL", "'RE":"\b'RE", "'VE":"\b'VE", "N'T":"\bN'T", "`":"'\b"}
def cleaned_sentence(tokens, highlights):
    tt = [PUNCT_DICT.get(t, t) for t in tokens]
    for i in highlights:
        tt[i] = '<span>%s</span>' % tt[i]
    r = ' '.join(tt)
    r = r.replace(' \b', '')
    r = r.replace('\b ', '')
    r = r.replace(' <span>\b', '<span>')
    r = r.replace('\b</span> ', '</span>')
    return r
