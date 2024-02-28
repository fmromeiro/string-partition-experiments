import gurobipy as gp
from gurobipy import GRB

class Watcher:
    def __init__(self, init_sol, comp):
        self.first_sol = self.last_sol = init_sol
        self.first_time = self.last_time = 0
        self.first_found = False
        self.comp = comp

    def callback(self, model: gp.Model, where: int) -> None:
        if where != GRB.Callback.MIPSOL: return

        if not self.first_found:
            self.first_sol = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            self.first_time = model.cbGet(GRB.Callback.RUNTIME)
            self.first_found = True
        
        if self.comp(
            model.cbGet(GRB.Callback.MIPSOL_OBJ), self.last_sol):
            self.last_sol = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            self.last_time = model.cbGet(GRB.Callback.RUNTIME)
