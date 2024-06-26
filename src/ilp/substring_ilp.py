import gurobipy as gp
from gurobipy import GRB

from .base_ilp import BaseILP, EPS
from ..utils.inter import (compare, find_substrings2, get_abundant_chars,
                           get_exclusive_blocks)


class Substring_ILP(BaseILP):
    def __init__(self, l1, l2, compare, reverse, signaled, balanced, mod,
                 intergenic=False, i1=None, i2=None, limit=3600):
        super().__init__(l1,l2,compare,reverse,signaled,intergenic,i1,i2,limit)
        self.balanced = balanced
        self.mod = self.balanced and mod

        self.B1, self.B2 = find_substrings2(self.l1, self.l2,self.i1, self.i2, self.compare,
                                        self.reverse, self.signaled)
        excl1, excl2 = get_abundant_chars(self.l1, self.l2)
        self.E1 = get_exclusive_blocks(self.l1, excl1)
        self.E2 = get_exclusive_blocks(self.l2, excl2)
        if self.mod:
            self.B1 = {t:ks for t,ks in self.B1.items() if len(t) > 1}
            self.B2 = {t:ks for t,ks in self.B2.items() if len(t) > 1}

    def _add_vars(self, B, nB):
        y = dict()
        for t, ks in B.items():
            y[t] = dict()
            for k in ks:
                y[t][k] = self.model.addVar(
                    0,1,1 if nB == 1 else 0,GRB.BINARY)#,f'y{nB}_{t}_{k}')
        return y
    
    def _add_exclusive_vars(self):
        if not self.balanced:
            self.x1 = []
            self.x2 = []
            for t, k in self.E1:
                self.x1.append(self.model.addVar(0,1,1,GRB.BINARY))#, f'x1_{t}_{k}'))
            for t, k in self.E2:
                self.x2.append(self.model.addVar(0,1,1,GRB.BINARY))#, f'x2_{t}_{k}'))

    def _add_char_constrs(self,B,y,nB):
        for j in range(len(self.l1)):
            expr = sum(
                sum(y[t][k]
                    for k in ks
                    if k <= j < k + len(t[0]))
                for t, ks in B.items())
            if not self.balanced:
                E, x = (self.E1, self.x1) if nB == 1 else (self.E2, self.x2)
                expr += sum(
                    x[i]
                    for i, (t, k) in enumerate(E)
                    if k <= j < k + len(t))
            self.model.addConstr(
                expr <= 1 if self.mod else expr == 1,
                f'unicidade de char {j} na str {nB}')

    def _add_variables(self):
        self.y1 = self._add_vars(self.B1, 1)
        self.y2 = self._add_vars(self.B2, 2)
        self._add_exclusive_vars()

    def _add_constraints(self):
        self._add_char_constrs(self.B1,self.y1,1)
        self._add_char_constrs(self.B2,self.y2,2)

        for t in self.B1:
            self.model.addConstr(
                sum(self.y1[t].values()) == sum(self.y2[t].values()))

    def _count_rare_markers(self):
        counts = [{},{}]
        for i, s in enumerate((self.l1, self.l2)):
            for char in s:
                c = abs(char)
                if c not in counts[i]: counts[i][c] = 0
                counts[i][c] += 1
        total = 0
        for char in counts[0]:
            total += min(counts[0][char], counts[1].get(char, 0))
        return total

    def _add_objective(self):
        if not self.mod: return

        expr = gp.LinExpr()
        if self.balanced:
            expr += len(self.l1)
        else:
            expr += self._count_rare_markers()

        for t, ks in self.y1.items():
            for _, yk in ks.items():
                expr += (1 - len(t)) * yk
        self.model.setObjective(expr, GRB.MINIMIZE)

    def _parse_solution(self):
        self.sol = []
        for t, ks in self.B1.items():
            for k in ks:
                if self.y1[t][k].X > 1 - EPS:
                    self.sol.append((t,k))

    def run(self):
        if not self.B1:
            s = self._count_rare_markers()
            print('Only single character blocks found, solution is composed of '
                  f'{s} such blocks')
            self._log_stats_dummy({'first_sol': s, 'last_sol': s, 'best_bd': s})
        else:
            super().run()

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