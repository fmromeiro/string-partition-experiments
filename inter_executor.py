import argparse
import os
from pathlib import Path
import re
import sys
from timeit import default_timer

from src.ilp import Block_ILP, Substring_ILP
from src.utils import blocks, inter

def _parse_args():
    parser = argparse.ArgumentParser(
        description='Runs ILP on selected (R)MCSP instances')
    parser.add_argument('impl', choices=['cb','cs','cb-mod', 'cs-mod'],
                        help='cb uses the common block based implementation, '
                        'cs uses the common substring one')
    # parser.add_argument('-r', '--reverse', action='store_true')
    # parser.add_argument('-s', '--signaled', action='store_true')
    args = parser.parse_args()
    return args

def main():
    args = _parse_args()
    # s1 = list(map(int, input().split()))
    # i1 = list(map(int, input().split()))[1:-1]
    # s2 = list(map(int, input().split()))
    # i2 = list(map(int, input().split()))[1:-1]

    log_dir = os.path.join('logs', args.impl)
    os.makedirs(log_dir, exist_ok=True)

    files = (f for f in os.listdir('instances')
             if re.match(rf'smcisp-', f))
    for filename in files:
        filename = Path(filename).stem

        # filename = filename if args.reverse else filename[1:]

        mod = 'mod' in args.impl
        impl = Block_ILP if 'cb' in args.impl else Substring_ILP
        comp = inter.signaled_compare # if args.signaled else inter.compare
        with open(f'instances/{filename}.in') as f:
            lines = f.readlines()
            file_suffix = "-".join(filename.split("-")[1:])
            i = 0
            while i < len(lines) // 4:
                s1 = list(map(int, lines[i*4].split()))
                i1 = list(map(int, lines[i*4 + 1].split()))[1:-1]
                s2 = list(map(int, lines[i*4 + 2].split()))
                i2 = list(map(int, lines[i*4 + 3].split()))[1:-1]
                filename = f'smcisp-{i:02d}-{file_suffix}'
                with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                    t = default_timer()
                    impl(s1,s2,comp,False,True,True,mod,True, i1,i2).run()
                    print(f'total_time: {default_timer()-t}')
                i1 = [0] * len(i1)
                i2 = [0] * len(i2)
                filename = f'smcsp-{i:02d}-{file_suffix}'
                with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                    t = default_timer()
                    impl(s1,s2,comp,False,True,True,mod,True, i1,i2).run()
                    print(f'total_time: {default_timer()-t}')
                i += 1

if __name__ == '__main__':
    main()

