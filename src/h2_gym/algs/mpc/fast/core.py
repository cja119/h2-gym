"""
This defines the inner loop of the model predictive control (MPC) algorithm.
"""

from __future__ import annotations
from pyomo.environ import ConcreteModel, Var, Constraint
from .utils import add_equations
from h2_plan.data import DefaultParams
from h2_gym.envs import Planning


class FastController:
    """ """

    def __init__(self, model):

        pass

    def build(self):
        """
        This function builds the MPC problem
        """
        pass

    def solve(self):
        """
        This function solves the MPC problem
        """
        pass

    def input(self):
        """ """
        pass

    def output(self):
        """ 
        """
        pass
