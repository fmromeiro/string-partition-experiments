# Implmentation of the linear program for the CMSP described in
# BLUM, Christian; RAIDL, Günther R. Computational performance evaluation of two
# integer linear programming models for the minimum common string partition
# problem. Optimization Letters, v. 10, p. 189-205, 2016.

from itertools import chain
from typing import Callable, TypeAlias

import gurobipy as gp
from gurobipy import GRB
import pyomo.environ as pyo
import numpy as np

Char: TypeAlias = int
String: TypeAlias = list[Char]
Block: TypeAlias = tuple[String,int,int]

EPS = 1e-4

def direct_compare(l1: String, l2: String) -> bool:
    for idx in range(len(l1)):
        if l1[idx] != l2[idx]:
            return False
    return True

def reverse_compare(l1: String, l2: String) -> bool:
    direct_eq = True
    reverse_eq = True
    for idx in range(len(l1)):
        direct_eq = direct_eq and l1[idx] == l2[idx]
        reverse_eq = reverse_eq and l1[idx] == l2[-idx-1]
        if not (direct_eq or reverse_eq): return False
    return direct_eq or reverse_eq

class ILPModel:

    def __init__(self, g1: String, g2: String,
                 compare: Callable[[String,String],bool], reverse:bool):
        self.g1 = g1
        self.g2 = g2
        self.compare = compare
        self.reverse = reverse

    def find_sub(self, block: String, genome: String) -> list[int]:
        l_pos = []
        start = 0
        while start <= (len(genome)-len(block)):
            
            if self.compare(block, genome[start:start + len(block)]):
                l_pos.append(start)
                start = start + len(block)
            else:
                start += 1
        return l_pos

    def find_blocks(self, g1: String, g2: String) -> tuple[dict[String,list[int]],dict[String,list[int]]]:
        B: set[String] = set()
        B1: dict[String, list[int]] = dict()
        B2: dict[String, list[int]] = dict()

        for i in range(len(g1)):
            for j in range(i, len(g1)):
                block = tuple(g1[i:(j+1)])

                if block in B:
                    B1[block].append(i)
                    continue
                if self.reverse and (t := tuple(reversed(block))) in B:
                    B1[t].append(i)
                    continue

                pos = self.find_sub(block, g2)
                if len(pos) > 0:
                    B.add(block)
                    B1[block] = [i]
                    B2[block] = pos
                else:
                    break
        return (B1,B2)

    def _add_vars(self, B, nB):
        y = dict()
        for t, ks in B.items():
            y[t] = dict()
            for k in ks:
                y[t][k] = self.model.addVar(0,1,nB % 2,GRB.BINARY,f'y{nB}_{t}_{k}')
        return y

    def _add_char_constrs(self,B,y,nB):
        for j in range(len(self.g1)):
            expr = sum(
                sum(y[t][k]
                    for k in ks
                    if k <= j < k + len(t))
                for t, ks in B.items())
            self.model.addConstr(expr == 1,f'unicidade de char {j} na str {nB}')

    def formulate(self):
        self.model = gp.Model('(Reverse) Common Minimum String Partition Program')
        self.model.Params.TimeLimit = 3600
        self.model.Params.Threads = 1
        self.model.ModelSense = GRB.MINIMIZE

        self.B1, self.B2 = self.find_blocks(self.g1, self.g2)

        self.y1 = self._add_vars(self.B1, 1)
        self.y2 = self._add_vars(self.B2, 2)
        
        self._add_char_constrs(self.B1,self.y1,1)
        self._add_char_constrs(self.B2,self.y2,2)
        
        for t in self.B1:
            self.model.addConstr(
                sum(self.y1[t].values()) == sum(self.y2[t].values()))

    def optimize(self):
        try:
            self.model.optimize()
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
        print(f'Quantidade de blocos: {self.model.ObjVal}')
        print(f'Tempo de execução: {self.model.Runtime}')

    def run(self):
        self.formulate()
        self.optimize()
        self.log_solution()
        self.log_stats()

if __name__ == '__main__':

    # g1 = sys.argv[1].split(",")
    # g2 = sys.argv[2].split(",")

    # seq = [1,2,3,4]
    # base = seq * 2
    # np.random.seed(1729)
    # g1 = np.random.permutation(len(base))
    # g2 = np.random.permutation(len(base))

    # g1 = [base[x] for x in g1]
    # g2 = [base[x] for x in g2]

    # print(g1,sep=',')
    # print(g2,sep=',')

    input()
    g1 = list(map(int, input().split()))
    g2 = list(map(int, input().split()))

    model = ILPModel(g1, g2, reverse_compare, True)
    model.run()