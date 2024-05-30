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

def _inter_flex_compare(i1, i2):
    for x1, x2 in zip(i1,i2):
        # print(x1,x2)
        if not(x2[0] <= x1 <= x2[1]): return False
    return True

def signaled_flex_compare(l1, l2, i1, i2, _):
    dir_comp = l1 == l2 and _inter_flex_compare(i1, i2)
    # print('e', list(reversed(i2)))
    rev_comp = l1 == [-x for x in reversed(l2)] and _inter_flex_compare(i1, list(reversed(i2)))
    return dir_comp or rev_comp


def find_sub(block, string, inter_block, inter_string, compare, reverse):
    l_pos = []
    start = 0
    while start <= len(string) - len(block):
        s = string[start: start + len(block)]
        i = inter_string[start: start + len(block) - 1]
        # print(i)
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
                inter2 = list(zip(inter2, inter2))
                if compare(list(t),list(t),inter,inter2,None):
                    B1[t].append(i)
                    continue
            elif signaled and (t_ := tuple(-x for x in reversed(t))) in B:
                inter2 = i1[B1[t_][0]:B1[t_][0] + len(inter)]
                inter2 = list(zip(inter2, inter2))
                if compare(list(t),list(t_),inter,inter2,None):
                    B1[t_].append(i)
                    continue
            elif reverse and (t_ := tuple(reversed(t))) in B:
                inter2 = i1[B1[t_][0]:B1[t_][0] + len(inter)]
                inter2 = list(zip(inter2, inter2))
                if compare(list(t),list(t_),inter,inter2,None):
                    B1[t_].append(i)
                    continue

            pos = find_sub(list(t), l2, inter, i2, compare, reverse)
            if pos:
                B.add(t)
                if t in B1:
                    B1[t].append(i)
                    B2[t].extend(pos)
                else:
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

def get_abundant_chars(l1,l2):
    counts = [{},{}]
    all_chars = set()
    for i, s in enumerate((l1, l2)):
        for char in s:
            c = abs(char)
            all_chars.add(c)
            if c not in counts[i]: counts[i][c] = 0
            counts[i][c] += 1

    abundant = (set(),set())
    for char in all_chars:
        c1 = counts[0].get(char, 0)
        c2 = counts[1].get(char, 0)
        if c1 > c2: abundant[0].add(char)
        elif c2 > c1: abundant[1].add(char)
    return abundant

def _find_abundant_run_from(string, start, abundant):
    for i in range(start, len(string)):
        if string[i] in abundant: break
    else: return (-1, None)

    for j in range(i+1, len(string)):
        if string[j] not in abundant: break
    else: j = len(string) + 1

    return (i, string[i:j])

def _get_all_exclusive_substrs(substring, idx):
    blocks = []
    for i in range(len(substring)):
        for j in range(i + 1, len(substring) + 1):
            blocks.append((i + idx, substring[i:j]))
    return blocks

def get_exclusive_blocks(string, abundant):
    i = 0
    blocks = []
    while i < len(string):
        idx, sub = _find_abundant_run_from(string, i, abundant)
        if sub == None: break
        blocks.extend(_get_all_exclusive_substrs(sub, idx))
        i += idx + len(sub)
    return blocks