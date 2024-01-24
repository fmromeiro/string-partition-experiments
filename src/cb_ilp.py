# Implmentation of the linear program for the (R)CMSP described in
# BLUM, Christian; LOZANO, José A.; DAVIDSON, Pinacho. Mathematical programming
# strategies for solving the minimum common string partition problem. European
# Journal of Operational Research, v. 242, n. 3, p. 769-777, 2015.

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

    def find_blocks(self, g1: String, g2: String) -> list[Block]:
        B = []

        for i in range(len(g1)):
            for j in range(i, len(g1)):
                block = g1[i:(j+1)]
                pos = self.find_sub(block, g2)
                if len(pos) > 0:
                    B = B + [(block, i, x) for x in pos]
                else:
                    break
        return B

    @staticmethod
    def matrixG1(model: pyo.ConcreteModel, j:int) -> pyo.Expression:
        return sum(model.M1[b-1,j-1] * model.x[b] for b in model.setB) == 1

    @staticmethod
    def matrixG2(model: pyo.ConcreteModel, j: int) -> pyo.Expression:
        return sum(model.M2[b-1,j-1] * model.x[b] for b in model.setB) == 1

    def run(self):
        model = pyo.ConcreteModel()

        B = self.find_blocks(self.g1, self.g2)

        model.M1 = np.zeros((len(B), len(self.g1)), dtype = int)
        model.M2 = np.zeros((len(B), len(self.g2)), dtype = int)

        for idx in range(len(B)):
            b, k1, k2 = B[idx]
            model.M1[idx, k1:k1+len(b)] = 1
            model.M2[idx, k2:k2+len(b)] = 1

        model.setG1 = pyo.RangeSet(len(self.g1)) 
        model.setG2 = pyo.RangeSet(len(self.g2)) 
        model.setB = pyo.RangeSet(len(B))
        model.x = pyo.Var(model.setB, domain=pyo.Binary)

        model.mG1 = pyo.Constraint(model.setG1, rule=ILPModel.matrixG1)
        model.mG2 = pyo.Constraint(model.setG2, rule=ILPModel.matrixG2)

        model.value = pyo.Objective(
            expr = sum(model.x[b] for b in model.setB), sense = pyo.minimize)

        opt = pyo.SolverFactory('cplex')
        result_obj = opt.solve(model, tee=True)

        print("status", result_obj.solver.termination_condition)
        sol_dict = model.x.extract_values()
        for b in sol_dict.keys():
            if sol_dict[b] == 1:
                print("Block", B[b-1])

# g1 = sys.argv[1].split(",")
# g2 = sys.argv[2].split(",")

seq = [1,2,3,4]
base = seq * 10
np.random.seed(1729)
g1 = np.random.permutation(len(base))
g2 = np.random.permutation(len(base))

g1 = [base[x] for x in g1]
g2 = [base[x] for x in g2]

print(g1,sep=',')
print(g2,sep=',')

model = ILPModel(g1, g2, reverse_compare)
model.run()