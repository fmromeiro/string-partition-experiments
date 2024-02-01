import argparse
from math import ceil, floor
import random
from typing import Callable, TypeAlias, Iterable

String: TypeAlias = Iterable[int]

def swap(s: String):
    n = len(s)
    l1 = random.randrange(n-3)
    n1 = random.randrange(1, floor((n - l1) / 2 + 1))
    l2 = random.randrange(l1 + n1,n - n1 + 1)
    s[l1:l1 + n1], s[l2:l2 + n1] = s[l2:l2 + n1], s[l1:l1 + n1]

def reverse(s: String):
    n = len(s)
    l = random.randrange(n-1)
    r = random.randrange(l+1, n+1)
    if l == 0:
        if r == 0: s[:] = s[::-1]
        else: s[:r] = s[r-1::-1]
    elif r == 0: s[l:] = s[:l-1:-1]
    else: s[l:r] = s[r-1:l-1:-1]

def generate(n: int, chars: int,  ops: list[Callable[[String], None]],
             fr_ops: float = 0.5, seed: int = 1) -> tuple[String, String]:
    if n < chars:
        raise Exception('String length must be higher than alphabet size')
    
    random.seed(seed)
    s1 = list(range(1, chars + 1))
    s1 += random.choices(s1, k = n - chars)
    random.shuffle(s1)
    
    s2 = s1.copy()
    for _ in range(ceil(fr_ops * n)):
        random.choice(ops)(s2)

    return s1,s2

def _parse_args():
    parser = argparse.ArgumentParser(description='(R)MCSP instance generator')
    parser.add_argument('n',type=int,help='string size')
    parser.add_argument('chars',type=int,help='number of distinct characters')
    parser.add_argument('ops',choices=['s','r','sr', 'rs'],
                        help='allowed operations, s = swap, r = reverse')
    parser.add_argument('seed',type=int,
                        help='random seed for string generation')
    parser.add_argument('--fr_ops',default=0.5,type=float,
                        help='number of operations made in fraction of string'
                        ' size')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    ops = []
    if 's' in args.ops: ops.append(swap)
    if 'r' in args.ops: ops.append(reverse)
    s1,s2 = generate(args.n, args.chars, ops, args.fr_ops, args.seed)
    print(args.n, args.chars)
    print(*s1)
    print(*s2)