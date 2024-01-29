# Implmentation of the linear program for the CMSP described in
# BLUM, Christian; RAIDL, Günther R. Computational performance evaluation of two
# integer linear programming models for the minimum common string partition
# problem. Optimization Letters, v. 10, p. 189-205, 2016.

from typing import Callable, TypeAlias
import pyomo.environ as pyo
import numpy as np

Char: TypeAlias = int
String: TypeAlias = list[Char]
Block: TypeAlias = tuple[String,int,int]

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

    def __init__(self, g1: String, g2: String, compare: Callable[[String,String],bool]):
        self.g1 = g1
        self.g2 = g2
        self.compare = compare

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
                # enable this if only if doing RCMSP
                if (t := tuple(reversed(block))) in B:
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

    def flatten_strings(self, strs: dict[String,list[int]]) -> tuple[list[tuple[String,int]],dict[String,list[tuple[int,int]]]]:
        res = []
        B = {}
        for t, K in strs.items():
            B[t] = []
            for k in K:
                B[t].append((k,len(res)))
                res.append((t,k))
        return (res,B)

    @staticmethod
    def matrixG1(model: pyo.ConcreteModel, j:int) -> pyo.Expression:
        expr = sum(
            model.y1[i]
                for i, (t, k) in enumerate(model.l1)
                if k <= j - 1 < k + len(t))
        return expr == 1

    @staticmethod
    def matrixG2(model: pyo.ConcreteModel, j: int) -> pyo.Expression:
        expr = sum(
            model.y2[i]
                for i, (t, k) in enumerate(model.l2)
                if k <= j - 1 < k + len(t))
        return expr == 1


    def run(self):
        model = pyo.ConcreteModel()

        B1, B2 = self.find_blocks(self.g1, self.g2)
        
        model.l1, model.B1 = self.flatten_strings(B1)
        model.l2, model.B2 = self.flatten_strings(B2)
        model.n1 = pyo.RangeSet(0,len(model.l1)-1)
        model.n2 = pyo.RangeSet(0,len(model.l2)-1)

        model.y1 = pyo.Var(model.n1,domain=pyo.Binary)
        model.y2 = pyo.Var(model.n2,domain=pyo.Binary)

        model.setG1 = pyo.RangeSet(len(self.g1)) 
        model.setG2 = pyo.RangeSet(len(self.g2)) 

        model.mG1 = pyo.Constraint(model.setG1, rule=ILPModel.matrixG1)
        model.mG2 = pyo.Constraint(model.setG2, rule=ILPModel.matrixG2)

        model.eqs = pyo.ConstraintList()
        
        for t,K in model.B1.items():
            expr1 = sum(model.y1[i] for _,i in K)
            expr2 = sum(model.y2[i] for _,i in model.B2[t])
            model.eqs.add(expr1 == expr2)

        model.value = pyo.Objective(
            expr = sum(model.y1[i] for i in model.n1),
            sense = pyo.minimize)

        model.pprint()

        opt = pyo.SolverFactory('cplex')
        result_obj = opt.solve(model, tee=True)

        print("status", result_obj.solver.termination_condition)
        sol_dict = model.y1.extract_values()
        for b in sol_dict.keys():
            if sol_dict[b] == 1:
                print("Block", model.l1[b], b,sol_dict[b])

# g1 = sys.argv[1].split(",")
# g2 = sys.argv[2].split(",")

seq = [1,2,3,4]
base = seq * 50
np.random.seed(1729)
g1 = np.random.permutation(len(base))
g2 = np.random.permutation(len(base))

g1 = [base[x] for x in g1]
g2 = [base[x] for x in g2]

print(g1,sep=',')
print(g2,sep=',')

model = ILPModel(g1, g2, reverse_compare)
model.run()