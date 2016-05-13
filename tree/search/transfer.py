def transfer():
    fin = open("tree_brackets_example", "r")
    text = fin.read()
    tmp = ""
    last_pop = ""
    queue = []
    answer = []
    answer += "id,\n"
    for c in text:
        if c == "(":
            if tmp != "":
                if last_pop == tmp:
                    tmp += "1"
                queue.append(tmp)
                answer += "@".join(queue) + ",\n"
                tmp = ""
        elif c == ")":
            if tmp != "":
                if last_pop == tmp:
                    tmp += "1"
                queue.append(tmp)
                tmp = ""
                answer += "@".join(queue) + ",\n"
                last_pop = queue.pop()
            else:
                last_pop = queue.pop()
        else:
            tmp += c
    print "".join(answer)
    return "".join(answer)

transfer()
