import argparse
import os
from pathlib import Path
import sys

from src import cb_ilp, cs_ilp

def _parse_args():
    parser = argparse.ArgumentParser(
        description='Runs ILP on selected (R)MCSP instances')
    parser.add_argument('impl', choices=['cb','cs'],
                        help='cb uses the common block based implementation, '
                        'cs uses the common substring one')
    parser.add_argument('fst', type=int, choices=range(1,33), metavar='fst',
                        help='first of the tests to be run [1-32]')
    parser.add_argument('lst', type=int, choices=range(1,33), metavar='lst',
                        help='last of the tests to be run [1-32]')
    parser.add_argument('-r', '--reverse', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = _parse_args()
    if args.lst < args.fst:
        raise Exception('fst and lst must indicate a valid test range')
    
    os.makedirs('logs', exist_ok=True)

    for i in range(args.fst,args.lst + 1):
        filename = next(f
                    for f in os.listdir('instances')
                    if f.startswith(f'rmcsp_{i}-'))
        filename = Path(filename).stem
        with open(f'instances/{filename}.in') as f:
            f.readline()
            s1 = list(map(int, f.readline().split()))
            s2 = list(map(int, f.readline().split()))

        filename = filename if args.reverse else filename[1:]

        if args.impl == 'cb':
            comp = (cb_ilp.reverse_compare
                    if args.reverse
                    else cb_ilp.direct_compare)
            with open(f'logs/cb_{filename}.log', 'w') as sys.stdout:
                cb_ilp.ILPModel(s1,s2,comp).run()
        else:
            comp = (cs_ilp.reverse_compare
                    if args.reverse
                    else cs_ilp.direct_compare)
            with open(f'logs/cs_{filename}.log', 'w') as sys.stdout:
                cs_ilp.ILPModel(s1,s2,comp,args.reverse).run()

if __name__ == '__main__':
    main()

