import gurobipy as gp
from gurobipy import GRB

from .blocks import find_substrings, substrings_to_blocks, compare
from .watcher import Watcher

EPS =  1e-4

class Block_ILP:
    def __init__(self, l1, l2, compare, reverse, mod, limit=3600):
        self.l1 = l1
        self.l2 = l2
        self.compare = compare
        self.reverse = reverse
        self.mod = mod
        self.limit = limit

    def _add_vars(self):
        self.x = []
        for t, k1, k2 in self.B:
            self.x.append(
                self.model.addVar(0, 1, 1, GRB.BINARY, f'x_{t}_{k1}_{k2}'))

    def _add_char_constrs(self,nB):
        b = nB - 1
        for j in range(len(self.l1)):
            expr = sum(
                self.x[i]
                for i, (t,*k) in enumerate(self.B)
                if k[b] <= j < k[b] + len(t))
            self.model.addConstr(expr <= 1 if self.mod else expr == 1,
                                 f'unicidade de char {j} na str {nB}')

    def _add_objective(self):
        if not self.mod: return

        expr = gp.LinExpr()
        expr += len(self.l1)
        for (t,_,_), x in zip(self.B,self.x):
            expr += (1 - len(t)) * x
        self.model.setObjective(expr, GRB.MINIMIZE)

    def formulate(self):
        B1, B2 = find_substrings(self.l1, self.l2, self.compare, self.reverse)
        self.B = substrings_to_blocks(B1, B2)
        if self.mod:
            self.B = [b for b in self.B if len(b[0]) > 1]

        self.model = gp.Model('(R)CMSP with Common Blocks')
        self.model.params.TimeLimit = self.limit
        self.model.params.Threads = 1

        self._add_vars()

        self._add_char_constrs(1)
        self._add_char_constrs(2)

        self._add_objective()

    def optimize(self):
        self.watcher = Watcher(float('inf'), lambda x, y: x < y)
        try:
            self.model.optimize(self.watcher.callback)
            self.sol = []
            for i, v in enumerate(self.B):
                if self.x[i].X > 1 - EPS:
                    self.sol.append(v)
        except gp.GurobiError as e:
            print('Error code ' + str(e.errno) + ': ' + str(e))
        except AttributeError:
            print('Encountered an attribute error')

    def log_solution(self):
        for (t,k1,_) in self.sol:
            print(f'Block {t} at {k1}')

    def log_stats(self):
        print('### ESTATISTICAS')
        # print(f'Quantidade de blocos: {self.model.ObjVal}')
        print(f'runtime: {self.model.Runtime}')
        print(f'first_sol: {self.watcher.first_sol}')
        print(f'first_time: {self.watcher.first_time}')
        print(f'last_sol: {self.watcher.last_sol}')
        print(f'last_time: {self.watcher.last_time}')
        print(f'gap: {self.model.MIPGap}')
        print(f'best_bd: {self.model.ObjBoundC}')

    def run(self):
        self.formulate()
        self.optimize()
        self.log_solution()
        self.log_stats()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='(R)CMSP using Common Blocks')
    parser.add_argument('-r', '--reverse',action='store_true',
                        help='allow block reversal')
    parser.add_argument('-m', '--mod',action='store_true',
                        help='only use blocks larger than 2 chars')
    parser.add_argument('-l', '--limit', type=int, default=3600,
                         help='ILP time limit (in seconds)')
    args = parser.parse_args()

    input()
    l1 = list(map(int, input().split()))
    l2 = list(map(int, input().split()))

    ilp = Block_ILP(l1, l2, compare, args.reverse, args.mod, args.limit)
    ilp.formulate()
    ilp.optimize()
    ilp.log_solution()
    ilp.log_stats()
