import argparse
import os
from pathlib import Path
import re
import sys

from src import blocks, blocks_ilp, substring_ilp

def _parse_args():
    parser = argparse.ArgumentParser(
        description='Runs ILP on selected (R)MCSP instances')
    parser.add_argument('impl', choices=['cb','cs','cb-mod', 'cs-mod'],
                        help='cb uses the common block based implementation, '
                        'cs uses the common substring one')
    parser.add_argument('fst', type=int, choices=range(1,145), metavar='fst',
                        help='first of the tests to be run [1-144]')
    parser.add_argument('lst', type=int, choices=range(1,145), metavar='lst',
                        help='last of the tests to be run [1-144]')
    parser.add_argument('-r', '--reverse', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = _parse_args()
    if args.lst < args.fst:
        raise Exception('fst and lst must indicate a valid test range')
    
    log_dir = os.path.join('logs', args.impl)
    os.makedirs(log_dir, exist_ok=True)

    for i in range(args.fst,args.lst + 1):
        filename = next(f
                    for f in os.listdir('instances')
                    if re.match(rf'rmcsp_0*{i}-', f))
        filename = Path(filename).stem
        with open(f'instances/{filename}.in') as f:
            f.readline()
            s1 = list(map(int, f.readline().split()))
            s2 = list(map(int, f.readline().split()))

        filename = filename if args.reverse else filename[1:]

        mod = 'mod' in args.impl
        if 'cb' in args.impl:
            with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                (blocks_ilp
                 .Block_ILP(s1,s2,blocks.compare,args.reverse,mod)
                 .run())
        else:
            with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                (substring_ilp
                 .Substring_ILP(s1,s2,blocks.compare,args.reverse,mod)
                 .run())

if __name__ == '__main__':
    main()

