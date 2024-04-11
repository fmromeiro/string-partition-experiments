from itertools import product

def compare(l1, l2, reverse):
    dir_comp = True
    rev_comp = reverse
    for i in range(len(l1)):
        dir_comp = dir_comp and l1[i] == l2[i]
        rev_comp = rev_comp and l1[i] == l2[-i-1]
        if not (dir_comp or rev_comp): return False
    return True

def signaled_compare(l1, l2, reverse):
    dir_comp = True
    rev_comp = True
    for i in range(len(l1)):
        dir_comp = dir_comp and l1[i] == l2[i]
        if i == len(l2) - i - 1:
            rev_comp = rev_comp and l1[i] == abs(l2[-i-1])
        else:
            rev_comp = rev_comp and l1[i] == -l2[-i-1]
        if not (dir_comp or rev_comp): return False
    return True

def find_sub(block, string, compare, reverse):
    l_pos = []
    start = 0
    while start <= len(string) - len(block):
        if compare(block, string[start: start + len(block)], reverse):
            l_pos.append(start)
        start += 1
    return l_pos

def find_substrings(l1, l2, compare, reverse = False, signaled = False):
    B = set()
    B1 = dict()
    B2 = dict()

    for i in range(len(l1)):
        for j in range(i, len(l1)):
            t = tuple(l1[i:j + 1])

            if t in B:
                B1[t].append(i)
                continue
            elif signaled and (t_ := tuple(-x for x in reversed(t))) in B:
                B1[t_].append(i)
                continue
            elif reverse and (t_ := tuple(reversed(t))) in B:
                B1[t_].append(i)
                continue

            pos = find_sub(t, l2, compare, reverse)
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