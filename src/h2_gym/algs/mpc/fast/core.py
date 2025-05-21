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
from .utils import add_equations, suppress_output
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
        self._run_count = 1
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

    def solve(self):
        """
        This function solves the MPC problem
        """
        self.instance1 = self.model1.create_instance()
        self.instance2 = self.model2.create_instance()

        self.solver = SolverFactory("gurobi")
        self.solver.options["mipgap"] = 0.05
        self.solver.options["FeasibilityTol"] = 1e-4
        self.solver.options["OptimalityTol"] = 1e-6

        with suppress_output():
            self.results = self.solver.solve(self.instance1, tee=False)

        self.lexicographic = 1

        if self.results.solver.termination_condition != "optimal":
            print("[INFO] Infeasible problem, solving lexicographically")
            self.results = self.solver.solve(self.instance2, tee=False)
            self.lexicographic = 2

        return self.output()

    def update(self, stochastic_values, start_values: Optional[dict] = None):
        """
        This function updates the MPC problem
        """
        self.stochastic_update(data=stochastic_values)

        if start_values is None:
            return None

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
            value(getattr(solve, "n_ship_ordered")[t]) for t in range(time_step)
        )
        stochastic_output["sent_ship"] = sum(
            value(getattr(solve, "n_ship_sent")[t]) for t in range(time_step)
        )

        for var in solve.component_objects(Var, active=True):
            for index in var:
                if isinstance(index, tuple):
                    if index[-1] == time_step:  # assuming time is the last index
                        new_index = index[:-1] + (0,)  # change t=24 to t=0
                        end_states[(var.name, new_index)] = value(var[index])
                elif index == time_step:
                    end_states[(var.name, 0)] = value(var[index])
                return end_states, stochastic_output

        getattr(self.model1, "fixed").set_value(True)
        getattr(self.model2, "fixed").set_value(True)

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

        # Gather time-series data
        steps = range(
            self._run_count * time_step, (self._run_count + 1) * time_step + 1
        )
        n_ship_ordered = [value(getattr(solve, "waiting_ships")[t]) for t in steps]
        n_ship_sent = [value(getattr(solve, "n_ship_sent")[t]) for t in steps]
        vector_storage = [value(getattr(solve, "vector_storage")[t]) for t in steps]
        cumulative_charge = [
            value(getattr(solve, "cumulative_charge")[t]) for t in steps
        ]
        energy_turbine = [value(getattr(solve, "energy_wind")[t]) for t in steps]
        energy_conversion = [
            value(getattr(solve, "energy_conversion")[t]) for t in steps
        ]

        axs = self._axs
        label = f"Run {self._run_count}"

        # Plot all subplots, joining with previous runs
        if self._run_count == 1:
            # First run: initialize data storage for joined plots
            self._joined_data = {
                "steps": list(steps),
                "n_ship_ordered": list(n_ship_ordered),
                "n_ship_sent": list(n_ship_sent),
                "vector_storage": list(vector_storage),
                "cumulative_charge": list(cumulative_charge),
                "energy_turbine": list(energy_turbine),
                "energy_conversion": list(energy_conversion),
            }
        else:
            # Append new data to existing joined data
            self._joined_data["steps"].extend(steps)
            self._joined_data["n_ship_ordered"].extend(n_ship_ordered)
            self._joined_data["n_ship_sent"].extend(n_ship_sent)
            self._joined_data["vector_storage"].extend(vector_storage)
            self._joined_data["cumulative_charge"].extend(cumulative_charge)
            self._joined_data["energy_turbine"].extend(energy_turbine)
            self._joined_data["energy_conversion"].extend(energy_conversion)

        # Plot joined data
        axs[0, 0].plot(
            self._joined_data["steps"],
            self._joined_data["n_ship_ordered"],
            label=label,
            color="blue",
        )
        axs[0, 0].set(title="Waiting Ships", xlabel="Time Step", ylabel="Count")
        axs[0, 0].grid(True)

        # Add horizontal lines every 24 hours (vertical lines at x=24,48,... up to max x)
        max_x = max(self._joined_data["steps"])
        for ax_row in axs:
            for ax in ax_row:
                for x in range(24, max_x + 1, 24):
                    ax.axvline(
                        x=x, linestyle="--", color="red", linewidth=0.8, alpha=0.5
                    )

        axs[0, 1].plot(
            self._joined_data["steps"],
            self._joined_data["n_ship_sent"],
            label=label,
            color="orange",
        )
        axs[0, 1].set(title="Number Ships Sent", xlabel="Time Step", ylabel="Count")
        axs[0, 1].grid(True)

        axs[0, 2].plot(
            self._joined_data["steps"],
            self._joined_data["vector_storage"],
            label=label,
            color="green",
        )
        axs[0, 2].set(title="Stored Vector", xlabel="Time Step", ylabel="Units")
        axs[0, 2].grid(True)

        axs[1, 0].plot(
            self._joined_data["steps"],
            self._joined_data["cumulative_charge"],
            label=label,
            color="purple",
        )
        axs[1, 0].set(title="Ship Fill", xlabel="Time Step", ylabel="Energy")
        axs[1, 0].grid(True)

        axs[1, 1].plot(
            self._joined_data["steps"],
            self._joined_data["energy_turbine"],
            label=label,
            color="navy",
        )
        axs[1, 1].set(title="Energy Turbine", xlabel="Time Step", ylabel="Energy")
        axs[1, 1].grid(True)

        axs[1, 2].plot(
            self._joined_data["steps"],
            self._joined_data["energy_conversion"],
            label=label,
            color="brown",
        )
        axs[1, 2].set(
            title="Energy Vector Conversion", xlabel="Time Step", ylabel="Energy"
        )
        axs[1, 2].grid(True)

        plt.tight_layout()

        self._fig.canvas.draw()  # Redraw canvas if needed
        self._run_count += 1

        return None
