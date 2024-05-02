from itertools import product

def compare(l1, l2, i1, i2, reverse):
    # print(l1, l2, i1, i2)
    dir_comp = l1 == l2 and i1 == i2
    rev_comp = reverse and l1 == list(reversed(l2)) and i1 == list(reversed(i2))
    return dir_comp or rev_comp

def signaled_compare(l1, l2, i1, i2, _):
    dir_comp = l1 == l2 and i1 == i2
    rev_comp = l1 == [-x for x in reversed(l2)] and i1 == list(reversed(i2))
    return dir_comp or rev_comp

def find_sub(block, string, inter_block, inter_string, compare, reverse):
    l_pos = []
    start = 0
    while start <= len(string) - len(block):
        s = string[start: start + len(block)]
        i = inter_string[start: start + len(block) - 1]
        if compare(block, s, inter_block, i, reverse):
            l_pos.append(start)
        start += 1
    return l_pos

def find_substrings(l1, l2, i1, i2, compare, reverse = False, signaled = False):
    B = set()
    B1 = dict()
    B2 = dict()

    for i in range(len(l1)):
        for j in range(i, len(l1)):
            t = tuple(l1[i:j + 1])
            inter = i1[i:j]

            if t in B:
                inter2 = i1[B1[t][0]:B1[t][0] + len(inter)]
                if compare(list(t),list(t),inter,inter2,None):
                    B1[t].append(i)
                    continue
            elif signaled and (t_ := tuple(-x for x in reversed(t))) in B:
                inter2 = i1[B1[t_][0]:B1[t_][0] + len(inter)]
                if compare(list(t),list(t_),inter,inter2,None):
                    B1[t_].append(i)
                    continue
            elif reverse and (t_ := tuple(reversed(t))) in B:
                inter2 = i1[B1[t_][0]:B1[t_][0] + len(inter)]
                if compare(list(t),list(t_),inter,inter2,None):
                    B1[t_].append(i)
                    continue

            pos = find_sub(list(t), l2, inter, i2, compare, reverse)
            if pos:
                B.add(t)
                B1[t] = [i]
                B2[t] = pos
            else:
                break

    return (B1, B2)

def substrings_to_blocks(B1, B2):
    B = []
    for t in B1:
        B.extend(product((t,), B1[t], B2[t]))
    return B