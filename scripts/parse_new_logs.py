import csv
from itertools import product
import os

RESULTS_DIR = os.path.join('results')
LOGS_DIR = os.path.join('logs2')

def get_to_info(lines):
    for i, line in enumerate(lines):
        if line.startswith('###'): return i + 1

def parse_log(path):
    with open(path, 'r') as log:
        lines = log.readlines()
        i = get_to_info(lines)
        lines = lines[i:]

        info = {line.split(':')[0]: line.split(':')[1].strip() for line in lines}
        return info

def parse_impl(impl, problem, n_chars):
    logs = []
    n_chars_str = f'-{n_chars}-'
    dir = os.path.join(LOGS_DIR, impl)
    for log in sorted(os.listdir(dir)):
        if problem not in log or n_chars_str not in log: continue
        path = os.path.join(dir, log)
        logs.append(parse_log(path))
    return logs

def write_problem_logs(problem, logs):
    impls = ('cb', 'cs', 'cb-mod', 'cs-mod')
    cols = ('runtime', 'first_sol', 'first_time', 'last_sol', 'last_time',
            'gap', 'best_bd', 'total_time')
    columns = ('index', 'n_chars','test')
    columns += tuple('-'.join(x) for x in product(impls, cols))
    path = os.path.join(RESULTS_DIR, f'{problem}.csv')
    with open(path, 'w', newline='') as res:
        writer = csv.writer(res)
        writer.writerow(columns)

        i = 0
        for n_chars in logs:
            for test_idx in range(10):
                row = (i, n_chars, test_idx)
                for impl in impls:
                    test = logs[n_chars][impl][test_idx]
                    row += tuple(test[col] for col in cols)
                writer.writerow(row)
                i += 1


def main():
    problems = ('smcsp', 'smcisp')
    impls = ('cb', 'cs', 'cb-mod', 'cs-mod')
    ns_chars = (4,20,36)

    logs = {}
    for problem in problems:
        logs[problem] = {}
        for n_chars in ns_chars:
            logs[problem][n_chars] = {}
            for impl in impls:
                logs[problem][n_chars][impl] = parse_impl(impl, problem, n_chars)

    for prob in problems:
        write_problem_logs(prob, logs[prob])

if __name__ == '__main__':
    main()