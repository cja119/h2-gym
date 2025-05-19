"""
This defines the inner loop of the model predictive control (MPC) algorithm.
"""

from __future__ import annotations
from pyomo.environ import AbstractModel, SolverFactory, value
from .utils import add_equations
from h2_plan.data import DefaultParams
from h2_gym.envs import Planning


class FastController:
    """ """

    def __init__(self):
        self.model1 = AbstractModel()
        self.model2 = AbstractModel()
        self._update_keys = None
        pass

    def build(self, data: dict):
        """
        This function builds the MPC problem
        """
        for key, set_ in data["sets"].items():
            setattr(self.model1, key, set_)
            getattr(self.model1, key).construct()
            setattr(self.model2, key, set_)
            getattr(self.model2, key).construct()

        for key, param in data["params"].items():
            setattr(self, key, param)
            setattr(self.model1, key, set_)
            getattr(self.model1, key).construct()
            setattr(self.model2, key, set_)
            getattr(self.model2, key).construct()
        
        for key, var in data["vars"].items():
            setattr(self.model1, key, var)
            setattr(self.model2, key, var)

        for key, constraint in data["constraints"].items():
            if key in data['formulations']['primary']:
                setattr(self.model1, key, constraint)
            if key in data['formulations']['secondary']:
                setattr(self.model2, key, constraint)

        
        for key, equation in data["equations"].items():
            if key in data['formulations']['primary']:
                setattr(self.model1, key, equation)
            if key in data['formulations']['secondary']:
                setattr(self.model2, key, equation)
            
        for key, objective in data["objectives"].items():
            if key in data['formulations']['primary']:
                setattr(self.model1, key, objective)
            if key in data['formulations']['secondary']:
                setattr(self.model2, key, objective)
        
        self.instance1 = self.model.create_instance()
        self.instance2 = self.model.create_instance()

        pass

    def solve(self):
        """
        This function solves the MPC problem
        """
        self.solver = SolverFactory('gurobi')
        self.solver.options["mipgap"] = 0.05
        self.solver.options['FeasibilityTol'] = 1e-6
        self.solver.options['OptimalityTol'] = 1e-6

        self.results = self.solver.solve(self.instance1, tee = False)
        self.lexicographic = 1
        if self.results.solver.termination_condition == "infeasible":
            self.results = self.solver.solve(self.instance2, tee = False)
            self.lexicographic = 2

        return self.output()

    def update(self, data: dict):
        """
        This function updates the MPC problem
        """

        for key, param in data["params"].items():
            setattr(self.instance1, key, param['param'])
            setattr(self.instance2, key, param['param'])
            
            # These keys will be used to grab the output
            if param['loc'] == 'endogenous':
                if self._update_keys is None:
                    self._update_keys = {key: param['name']}
                elif key not in self._update_keys:
                    self._update_keys.append(key[3:])
        pass

    def output(self, time_step: int = 24):
        """ 
        Grabs the necessary latent stated of the model for future solves
        """

        latent_states = {}

        if self.lexicographic == 1:
            solve = self.instance1
        else:
            solve = self.instance2

        for key, name in self._update_keys:
            if key == 'current_ships':
                latent_states['current_ships'] = value(getattr(solve, 'ship_arrived')) 
                - sum(
                    value(getattr(solve, 'n_ship_send')[t]) for t in range(time_step)
                    ) 
            else:
                latent_states[name] = value(getattr(solve, name)[time_step])

        latent_states['ordered_ship'] = sum(
            value(getattr(solve, 'n_ship_ordered')[t]) for t in range(time_step)
        )

        latent_states['sent_ship'] = sum(
            value(getattr(solve, 'n_ship_sent')[t]) for t in range(time_step)
        )

        return latent_states
