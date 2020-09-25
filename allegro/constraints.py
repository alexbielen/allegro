"""
constraints.py

"""
from collections import Counter
from typing import Callable, List, Optional

from ortools.sat.python import cp_model


Filter = Callable[[List[int]], bool]
Formatter = Callable[[List[int]], None]
Variable = cp_model.IntVar
Constraint = cp_model.Constraint
BoundedLinearExpression = cp_model.BoundedLinearExpression


def unique_pitch_classes(solution: List[int]) -> bool:
    pitch_classes = Counter()
    equal_temperament_mod = 12
    for pitch_class in solution:
        pitch_classes[str(pitch_class % equal_temperament_mod)] += 1

    for _, count in pitch_classes.items():
        if count != 1:
            return False

    return True


class _DefaultCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solutions = []

    def on_solution_callback(self):
        solution = [self.Value(v) for v in self.__variables]
        self.solutions.append(solution)


class Problem:
    def __init__(self):
        self.model = cp_model.CpModel()
        self._variables = []
        self._variable_count = 0
        self._filters = []
        self._solver = cp_model.CpSolver()

    def add_constant(self, x: int):
        return self.model.NewConstant(x)

    def add_variable(
        self, lower_bound: int, upper_bound: int, name: str = None
    ) -> Variable:
        if not name:
            name = chr(self._variable_count)
        var = self.model.NewIntVar(lower_bound, upper_bound, name)
        self._variables.append(var)
        self._variable_count += 1
        return var

    def add_constraint(self, constraint: BoundedLinearExpression) -> Constraint:
        constraint = self.model.Add(constraint)
        return constraint

    def add_all_different_constraint(self, notes: List[int]):
        constraint = self.model.AddAllDifferent(notes)
        return constraint

    def add_filter(self, f: Filter):
        self._filters.append(f)

    def solve(self, show_variables=Optional[List[any]]):
        if show_variables:
            variables = show_variables
        else:
            variables = self._variables

        solutions = _DefaultCallback(variables)
        self._solver.SearchForAllSolutions(self.model, solutions)
        result = []
        print(solutions.solutions)
        for solution in solutions.solutions:
            passes_filters = all([f(solution) for f in self._filters])
            if passes_filters:
                result.append(solution)

        return result
