import gurobipy as gp
from gurobipy import GRB

from .blocks import compare, find_substrings
from .watcher import Watcher

EPS = 1e-4

class Substring_ILP:
    def __init__(self, l1, l2, compare, reverse, mod, limit=3600):
        self.l1 = l1
        self.l2 = l2
        self.compare = compare
        self.reverse = reverse
        self.mod = mod
        self.limit = limit

    def _add_vars(self, B, nB):
        y = dict()
        for t, ks in B.items():
            y[t] = dict()
            for k in ks:
                y[t][k] = self.model.addVar(
                    0,1,1 if nB == 1 else 0,GRB.BINARY,f'y{nB}_{t}_{k}')
        return y

    def _add_char_constrs(self,B,y,nB):
        for j in range(len(self.l1)):
            expr = sum(
                sum(y[t][k]
                    for k in ks
                    if k <= j < k + len(t))
                for t, ks in B.items())
            self.model.addConstr(expr <= 1 if self.mod else expr == 1,
                                 f'unicidade de char {j} na str {nB}')

    def _add_objective(self):
        if not self.mod: return

        expr = gp.LinExpr()
        expr += len(self.l1)
        for t, ks in self.y1.items():
            for _, yk in ks.items():
                expr += (1 - len(t)) * yk
        self.model.setObjective(expr, GRB.MINIMIZE)

    def formulate(self):
        self.model = gp.Model('(Reverse) Common Minimum String Partition Program')
        self.model.Params.TimeLimit = self.limit
        self.model.Params.Threads = 1

        self.B1, self.B2 = find_substrings(self.l1, self.l2, self.compare,
                                           self.reverse)
        if self.mod:
            self.B1 = {t:ks for t,ks in self.B1.items() if len(t) > 1}
            self.B2 = {t:ks for t,ks in self.B2.items() if len(t) > 1}

        self.y1 = self._add_vars(self.B1, 1)
        self.y2 = self._add_vars(self.B2, 2)
        
        self._add_char_constrs(self.B1,self.y1,1)
        self._add_char_constrs(self.B2,self.y2,2)
        
        for t in self.B1:
            self.model.addConstr(
                sum(self.y1[t].values()) == sum(self.y2[t].values()))

        self._add_objective()

    def optimize(self):
        self.watcher = Watcher(float('inf'), lambda x, y: x < y)
        try:
            self.model.optimize(self.watcher.callback)
            self. sol = []
            for t, ks in self.B1.items():
                for k in ks:
                    if self.y1[t][k].X > 1 - EPS:
                        self.sol.append((t,k))
        except gp.GurobiError as e:
            print('Error code ' + str(e.errno) + ': ' + str(e))
        except AttributeError:
            print('Encountered an attribute error')

    def log_solution(self):
        for (t,k) in self.sol:
            print(f'Block {t} at {k}')

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

    ilp = Substring_ILP(l1, l2, compare, args.reverse, args.mod, args.limit)
    ilp.formulate()
    ilp.optimize()
    ilp.log_solution()
    ilp.log_stats()