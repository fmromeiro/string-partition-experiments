from math import floor
import os

from generator import generate, swap, reverse

def main():
    ns = [200,300,400,500,600]
    chars = [4,20,0.5,0.25]
    seed = 1
    fr_ops = 1
    ops = [reverse]

    os.makedirs('instances', exist_ok=True)

    z = len(str(len(ns) * len(chars)))
    i = 0
    for n in ns:
        char_set = set(floor(c * n) if c < 1 else c for c in chars)
        for c in char_set:
            s1, s2 = generate(n,c,ops,fr_ops,seed)
            i += 1
            with open(f'instances/rmcsp_{str(i).zfill(z)}-{n}_{c}_{fr_ops}_{seed}.in','w') as f:
                print(f'{n} {c}', file=f)
                print(*s1, file=f)
                print(*s2, file=f)

if __name__ == '__main__':
    main()