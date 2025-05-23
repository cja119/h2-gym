"""
This defines the inner loop of the model predictive control (MPC) algorithm.
"""

from __future__ import annotations
from pyomo.environ import (
    AbstractModel,
    SolverFactory,
    value,
    Set,
    Param,
    Var,
    Constraint,
    Objective,
    Reals,
    Any,
)
from .utils import add_equations, suppress_output, ext_visualise_output
from typing import Optional
from h2_plan.data import DefaultParams
from h2_gym.envs import Planning
import matplotlib
import matplotlib.pyplot as plt
import logging


matplotlib.use("TkAgg")


class FastController:
    """ """

    def __init__(self):
        self.model1 = AbstractModel()
        self.model2 = AbstractModel()
        self._update_keys = None
        self._fig, self._axs = plt.subplots(2, 3, figsize=(18, 10), sharex=True)
        self._run_count = 0
        pass

    def render(self):
        return self._fig

    def build(self, data: dict):
        """
        This function builds the MPC problem
        """
        for key, set_ in data["sets"].items():
            setattr(self.model1, key, Set(initialize=list(set_)))
            getattr(self.model1, key).construct()
            setattr(self.model2, key, Set(initialize=list(set_)))
            getattr(self.model2, key).construct()

        for key, param in data["params"].items():
            setattr(self.model1, key, Param(initialize=param, within=Any))
            getattr(self.model1, key).construct()
            setattr(self.model2, key, Param(initialize=param, within=Any))
            getattr(self.model2, key).construct()

        for key, var in data["vars"].items():
            setattr(self.model1, key, Var(*var["time_duration"], within=var["domain"]))
            getattr(self.model1, key).construct()
            setattr(self.model2, key, Var(*var["time_duration"], within=var["domain"]))
            getattr(self.model2, key).construct()

        for key, constraint in data["constraints"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Constraint(*constraint["time_duration"], rule=constraint["rule"]),
                )
                # getattr(self.model1, key).construct()
            if key in data["forms"]["secondary"]:
                setattr(
                    self.model2,
                    key,
                    Constraint(*constraint["time_duration"], rule=constraint["rule"]),
                )
                # getattr(self.model2, key).construct()

        for key, equation in data["equations"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Constraint(*equation["time_duration"], rule=equation["rule"]),
                )
                # getattr(self.model1, key).construct()
            if key in data["forms"]["secondary"]:
                setattr(
                    self.model2,
                    key,
                    Constraint(*equation["time_duration"], rule=equation["rule"]),
                )
                # getattr(self.model2, key).construct()

        for key, objective in data["objectives"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Objective(expr=objective["rule"], sense=objective["sense"]),
                )
                # getattr(self.model1, key).construct()
            if key in data["forms"]["secondary"]:
                setattr(
                    self.model2,
                    key,
                    Objective(expr=objective["rule"], sense=objective["sense"]),
                )
                # getattr(self.model2, key).construct()
        # Setting the fixed variable boolean to False as this will be the first solve
        setattr(self.model1, "fixed", Param(initialize=False, mutable=True))
        getattr(self.model1, "fixed").construct()
        setattr(self.model2, "fixed", Param(initialize=False, mutable=True))
        getattr(self.model2, "fixed").construct()

        pass

    def solve(self, supress):
        """
        This function solves the MPC problem
        """
        self.instance1 = self.model1.create_instance()
        self.instance2 = self.model2.create_instance()

        self.solver = SolverFactory("gurobi")
        self.solver.options["mipgap"] = 0.05
        self.solver.options["FeasibilityTol"] = 1e-6
        self.solver.options["OptimalityTol"] = 1e-8

        with suppress_output(supress):
            self.results = self.solver.solve(self.instance1, tee= supress)

        self.lexicographic = 1

        if self.results.solver.termination_condition != "optimal":
            print("[INFO] Infeasible problem, solving lexicographically")
            self.results = self.solver.solve(self.instance2, tee= supress)
            self.lexicographic = 2

        return self.output()

    def update(self, stochastic_values, start_values: Optional[dict] = None):
        """
        This function updates the MPC problem
        """
        

        if start_values is None:
            self.stochastic_update(data=stochastic_values)
            return None
        print(f"{start_values['n_ship_ordered',0] = }")
        print(f"{start_values['n_ship_sent',0] = }")
        print(f"{start_values['waiting_ships',0] = }")
        print(f"{start_values['cumulative_charge',0] = }")
        for var in self.model1.component_objects(Var, active=True):
            for index in var:
                key = (var.name, index)
                if key in start_values:
                    var[index].fix(start_values[key])

        for var in self.model1.component_objects(Var, active=True):
            for index in var:
                key = (var.name, index)
                if key in start_values:
                    var[index].fix(start_values[key])

        self.stochastic_update(data=stochastic_values)

        return None

    def output(self, time_step: int = 24):
        """
        This function outputs the MPC problem
        """
        solve = self.instance1 if self.lexicographic == 1 else self.instance2



        # Dictionary to store values at t=24
        end_states = {}
        stochastic_output = {}

        # Extract if any ships were sent  or ordered
        stochastic_output["ordered_ship"] = sum(
            value(getattr(solve, "n_ship_ordered")[t]) for t in range(0, time_step, 24)
        )
        stochastic_output["sent_ship"] = sum(
            value(getattr(solve, "n_ship_sent")[t]) for t in range(0, time_step, 24)
        )

        for var in solve.component_objects(Var):
            for index in var:
                if isinstance(index, tuple):
                    if index[-1] == time_step:  # assuming time is the last index
                        new_index = index[:-1] + (0,)  # change t=24 to t=0
                        end_states[(var.name, new_index)] = value(var[index])
                elif index == time_step:
                    end_states[(var.name, 0)] = value(var[index])

        getattr(self.model1, "fixed").set_value(True)
        getattr(self.model2, "fixed").set_value(True)

        return  end_states, stochastic_output

    def stochastic_update(self, data: Optional[dict] = None):
        """
        This function updates the MPC problem
        """

        for key, param in data.items():
            if param["param"]["set"] is not None:
                self.model1.del_component(key)
                self.model2.del_component(key)

                setattr(
                    self.model1,
                    key,
                    Param(
                        param["param"]["set"],
                        initialize=param["param"]["initialize"],
                        within=Reals,
                    ),
                )
                getattr(self.model1, key).construct()
                setattr(
                    self.model2,
                    key,
                    Param(
                        param["param"]["set"],
                        initialize=param["param"]["initialize"],
                        within=Reals,
                    ),
                )
                getattr(self.model2, key).construct()
            else:
                #if key == "ship_arrived":
                #    try:
                #        param["param"]["initialize"] += value(getattr(self.model1, key))
                #    except AttributeError:
                #        pass
                self.model1.del_component(key)
                self.model2.del_component(key)
                setattr(
                    self.model1,
                    key,
                    Param(initialize=param["param"]["initialize"], within=Reals),
                )
                getattr(self.model1, key).construct()
                setattr(
                    self.model2,
                    key,
                    Param(initialize=param["param"]["initialize"], within=Reals),
                )
                getattr(self.model2, key).construct()

            # These keys will be used to grab the output
            if param["loc"] == "endogenous":
                if self._update_keys is None:
                    self._update_keys = {key: param["name"]}
                elif key not in self._update_keys:
                    self._update_keys[key] = param["name"]
        pass

    def visualise_output(self, time_step: int = 24):
        """
        Extracts latent states and dynamically updates plots across runs.
        """
    
        solve = self.instance1 if self.lexicographic == 1 else self.instance2
        
        self._joined_data = ext_visualise_output(
            solve=solve,
            axs=self._axs,
            run_count=self._run_count,
            time_step=time_step,
            joined_data=self._joined_data if hasattr(self, "_joined_data") else None,
            fig=self._fig,
        )

        self._run_count += 1
        