"""
This defines the inner loop of the model predictive control (MPC) algorithm.
"""
from __future__ import annotations
from pyomo.environ import ConcreteModel, Var, Constraint
from .utils import (add_equations)
from h2_plan.data import DefaultParams
from h2_gym.envs import Planning

class FastLoop:
    """
    
    """
    def __init__(self, name, weather_file, n_inner: int = 1):
        self._plan = Planning(name, weather_file)
        self._model = ConcreteModel()
        self._model
        pass

    def update(self, data):
        """
        Updates the inner loop with the new data.
        """
        pass
    
    def plan(self):
        """
        Plans the inner loop.
        """
        return

    def solve(self):
        """
        Solves the inner loop.
        """
        pass

    def get_results(self):
        """
        Returns the results of the inner loop.
        """
        pass