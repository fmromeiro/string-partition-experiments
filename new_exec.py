import argparse
import os
from pathlib import Path
import re
import sys
from timeit import default_timer

from src.ilp import Block_ILP, Substring_ILP
from src.utils import blocks, inter

def run_tests_for_impl(impl, log_dir):
    impl = Block_ILP if 'cb' in impl else Substring_ILP
    reverse = False
    signaled = True
    mod = False
    intergenic = True
    
    files = (f for f in os.listdir('instances'))
            #  if re.match(rf'smcisp-1250-04-1000-06', f))
            #  if re.match(rf'test-', f))
    for filename in files:
        filename = Path(filename).stem

        with open(f'instances/{filename}.in') as f:
            lines = f.readlines()
            file_infos = filename.split('-')
            file_suffix = "-".join(file_infos[1:])
            balanced = file_infos[-1] == '1'

            i = 0
            while i < len(lines) // 4:
                s1 = list(map(int, lines[i*4].split()))
                i1 = list(map(int, lines[i*4 + 1].split()))[1:-1]
                s2 = list(map(int, lines[i*4 + 2].split()))
                i2 = list(map(int, lines[i*4 + 3].split()))[1:-1]

                comp = inter.signaled_compare
                i1_ = [0] * len(i1)
                i2_ = [0] * len(i2)
                filename = f'smcfisp-{i:02d}-{file_suffix}-N'
                with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                    t = default_timer()
                    impl(s1,s2,comp,reverse,signaled,balanced,mod,intergenic,
                         i1_,i2_).run()
                    print(f'total_time: {default_timer()-t}')

                filename = f'smcfisp-{i:02d}-{file_suffix}-0'
                with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                    t = default_timer()
                    impl(s1,s2,comp,reverse,signaled,balanced,mod,intergenic,
                         i1,i2).run()
                    print(f'total_time: {default_timer()-t}')

                comp = inter.signaled_flex_compare
                for interval in (0.25, 0.5):
                    i2l = [round((1 - interval) * x) for x in i2]
                    i2u = [round((1 + interval) * x) for x in i2]
                    i2_ = list(zip(i2l, i2u))
                    int_str = str(interval).replace('.', '')
                    filename = f'smcfisp-{i:02d}-{file_suffix}-{int_str}'
                    with open(f'{log_dir}/{filename}.log', 'w') as sys.stdout:
                        t = default_timer()
                        impl(s1,s2,comp,reverse,signaled,balanced,mod,
                             intergenic,i1,i2_).run()
                        print(f'total_time: {default_timer()-t}')

                i += 1

def main():
    for impl in ('cb', 'cs'):
        log_dir = os.path.join('logs', impl)
        os.makedirs(log_dir, exist_ok=True)
        run_tests_for_impl(impl, log_dir)

if __name__ == '__main__':
    main()

