import csv
from operator import itemgetter
import os
import re

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_DIR = os.path.join('results')
LOGS_DIR = os.path.join('logs')
LOG_PARSE_REGEX = re.compile(r'.?mcsp_(\d+)-(\d+)_(\d+)_(\d+)_(\d+).log')

def parse_logs(impl):
    logs = []
    dir = os.path.join(LOGS_DIR, impl)
    for log in sorted(os.listdir(dir)):
        m = LOG_PARSE_REGEX.match(log).groups()
        path = os.path.join(dir, log)
        with open(path, 'r') as log_file:
            lines = log_file.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.startswith('###'):
                lines = lines[i + 1:]
                found = True
                break
        if found:
            logs.append((*m, *map(lambda x: x.split(':')[1].strip(), lines)))
    return logs

def write_logs(impl, logs):
    with open(os.path.join(RESULTS_DIR, f'{impl}.csv'), 'w', newline='') as res:
        writer = csv.writer(res)
        writer.writerow(('index', 'length', 'n_chars', 'n_ops', 'seed',
                         'runtime', 'first_sol', 'first_time', 'last_sol',
                         'last_time', 'gap', 'best_bd'))
        writer.writerows(logs)

def _typecast_row(row):
    types = (
        (
            int,
            ('index','length','n_chars','n_ops','seed')
        ),
        (
            float,
            ('runtime','first_time','last_time','gap','best_bd','first_sol'
             ,'last_sol')
        ),
    )
    
    res = dict(row)
    for cast, cols in types:
        res.update({col: cast(row[col]) for col in cols})
    return res

def generate_graph(dfs, impls, column, tests, ns_chars):
    markers = {'cb': '^b', 'cb-mod': 'sg', 'cs': 'Pr', 'cs-mod': '*m'}
    for impl in impls:
        df = dfs[impl]
        df = df[(df['index'].isin(tests)) & (df['n_chars'].isin(ns_chars))]
        plt.plot(df['index'], df[column], markers[impl], alpha=0.5)
    plt.legend(impls)

def generate_graphs():
    markers = ('^b', 'sg', 'Pr', '*m')
    dfs = {}
    for name in os.listdir(RESULTS_DIR):
        path = os.path.join(RESULTS_DIR, name)
        impl = name.split('.')[0]
        dfs[impl] = pd.read_csv(path)
    
    os.makedirs('graphs', exist_ok=True)
    for n_chars in (4,20,36,52):
        for col in ('runtime', 'first_time', 'first_sol', 'gap', 'last_sol'):
            generate_graph(dfs,('cb', 'cb-mod', 'cs', 'cs-mod'), col, list(range(1,41)), (n_chars,))
            plt.savefig(f'graphs/rcmsp_{col}_lower_{n_chars}.png', dpi=150)
            plt.clf()
            generate_graph(dfs,('cb', 'cb-mod', 'cs', 'cs-mod'), col, list(range(41,81)), (n_chars,))
            plt.savefig(f'graphs/rcmsp_{col}_upper_{n_chars}.png',dpi=150)
            plt.clf()




def main():
    impls = ('cb', 'cb-mod', 'cs', 'cs-mod')
    for impl in impls:
        logs = parse_logs(impl)
        write_logs(impl,logs)

if __name__ == '__main__':
    os.makedirs(RESULTS_DIR, exist_ok=True)
    main()
    generate_graphs()