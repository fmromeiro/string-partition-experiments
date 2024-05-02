import abc

import gurobipy as gp

from .watcher import Watcher

EPS = 1e-4

class BaseILP(abc.ABC):
    def __init__(self, l1, l2, compare, reverse, signaled, intergenic, i1=None, i2=None, limit=3600):
        self.l1 = l1
        self.l2 = l2
        self.compare = compare
        self.reverse = reverse
        self.signaled = signaled
        self.intergenic = intergenic and i1 and i2
        if self.intergenic:
            self.i1 = i1
            self.i2 = i2
        else:
            self.i1 = [0] * (len(l1) - 1)
            self.i2 = [0] * (len(l2) - 1)
        self.limit = limit
        self.sol = []

    @abc.abstractmethod
    def _add_variables(self):
       pass

    @abc.abstractmethod
    def _add_constraints(self):
        pass
    
    @abc.abstractmethod
    def _add_objective(self):
        pass

    def formulate(self):
        self.model = gp.Model('(Reverse) Common Minimum String Partition Program')
        self.model.Params.TimeLimit = self.limit
        self.model.Params.Threads = 1

        self._add_variables()        
        self._add_constraints()
        self._add_objective()

    @abc.abstractmethod
    def _parse_solution(self):
        pass

    def optimize(self):
        self.watcher = Watcher(float('inf'), lambda x, y: x < y)
        try:
            self.model.optimize(self.watcher.callback)
            self._parse_solution()
        except gp.GurobiError as e:
            print('Error code ' + str(e.errno) + ': ' + str(e))
        except AttributeError:
            print('Encountered an attribute error')

    def log_solution(self):
        for (t,k) in self.sol:
            print(f'Block {t} at {k}')

    def log_stats(self):
        print('### ESTATISTICAS')
        print(f'runtime: {self.model.Runtime}')
        print(f'first_sol: {self.watcher.first_sol}')
        print(f'first_time: {self.watcher.first_time}')
        print(f'last_sol: {self.watcher.last_sol}')
        print(f'last_time: {self.watcher.last_time}')
        print(f'gap: {self.model.MIPGap}')
        print(f'best_bd: {self.model.ObjBoundC}')

    def _log_stats_dummy(self, stats):
        print('### ESTATISTICAS')
        for stat in ('runtime','first_sol','first_time','last_sol','last_time',
                     'gap','best_bd'):
            print(f'{stat}: {stats.get(stat, 0)}')

    def run(self):
        self.formulate()
        self.optimize()
        self.log_solution()
        self.log_stats()