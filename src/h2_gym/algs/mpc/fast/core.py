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
)
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
            setattr(self.model1, key, Set(initialize=list(set_)))
            getattr(self.model1, key).construct()
            setattr(self.model2, key, Set(initialize=list(set_)))
            getattr(self.model2, key).construct()

        for key, param in data["params"].items():
            setattr(self.model1, key, Param(initialize=param, within=Reals))
            getattr(self.model1, key).construct()
            setattr(self.model2, key, Param(initialize=param, within=Reals))
            getattr(self.model2, key).construct()

        for key, var in data["vars"].items():
            setattr(self.model1, key, Var(*var["time_duration"], within=var["domain"]))
            setattr(self.model2, key, Var(*var["time_duration"], within=var["domain"]))

        for key, constraint in data["constraints"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Constraint(*constraint["time_duration"], rule=constraint["rule"]),
                )
            if key in data["forms"]["secondary"]:
                setattr(
                    self.model2,
                    key,
                    Constraint(*constraint["time_duration"], rule=constraint["rule"]),
                )

        for key, equation in data["equations"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Constraint(*equation["time_duration"], rule=equation["rule"]),
                )
            if key in data["forms"]["secondary"]:
                setattr(
                    self.model2,
                    key,
                    Constraint(*equation["time_duration"], rule=equation["rule"]),
                )

        for key, objective in data["objectives"].items():
            if key in data["forms"]["primary"]:
                setattr(
                    self.model1,
                    key,
                    Objective(expr=objective["expr"], sense=objective["sense"]),
                )
            if key in data["forms"]["secondary"]:
                setattr(self.model2, key, objective)

        self.instance1 = self.model1.create_instance()
        self.instance2 = self.model2.create_instance()

        pass

    def solve(self):
        """
        This function solves the MPC problem
        """
        self.solver = SolverFactory("gurobi")
        self.solver.options["mipgap"] = 0.05
        self.solver.options["FeasibilityTol"] = 1e-6
        self.solver.options["OptimalityTol"] = 1e-6

        self.results = self.solver.solve(self.instance1, tee=False)
        self.lexicographic = 1
        if self.results.solver.termination_condition == "infeasible":
            self.results = self.solver.solve(self.instance2, tee=False)
            self.lexicographic = 2

        return self.output()

    def update(self, data: dict):
        """
        This function updates the MPC problem
        """

        for key, param in data.items():
            setattr(
                self.instance1,
                key,
                Param(
                    *(
                        param["param"]["set"]
                        if param["param"]["set"] is not None
                        else None
                    ),
                    initialize=param["param"]["initialize"],
                    within=Reals,
                ),
            )
            setattr(
                self.instance2,
                key,
                Param(
                    *(
                        param["param"]["set"]
                        if param["param"]["set"] is not None
                        else None
                    ),
                    initialize=param["param"]["initialize"],
                    within=Reals,
                ),
            )

            # These keys will be used to grab the output
            if param["loc"] == "endogenous":
                if self._update_keys is None:
                    self._update_keys = {key: param["name"]}
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
            if key == "current_ships":
                latent_states["current_ships"] = value(getattr(solve, "ship_arrived"))
                -sum(value(getattr(solve, "n_ship_send")[t]) for t in range(time_step))
            else:
                latent_states[name] = value(getattr(solve, name)[time_step])

        latent_states["ordered_ship"] = sum(
            value(getattr(solve, "n_ship_ordered")[t]) for t in range(time_step)
        )

        latent_states["sent_ship"] = sum(
            value(getattr(solve, "n_ship_sent")[t]) for t in range(time_step)
        )

        return latent_states
