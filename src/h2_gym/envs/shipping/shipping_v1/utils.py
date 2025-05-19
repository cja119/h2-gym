"""
Utility functions for the shipping environment.
"""

from typing import Optional
from pathlib import Path
import importlib.util
from h2_plan.data import DefaultParams
from pyomo.environ import (
    Param,
    Set,
    Constraint,
    Objective,
    maximize,
    minimize,
    Var,
    NonNegativeIntegers,
    NonNegativeReals,
)
from numpy.random import rand
from random import randint
from glob import glob
import yaml


def optimisation_handover(model):
    """
    This function is used to handover the results of the optimisation to the environment.
    """
    pass


def environment_handover(model):
    """
    This function is used to handover the results of the environment to the optimisation.
    """
    pass


def import_fast_data(
    data_folder: str, planning_model: str, vector: str, random_param: bool = False
) -> dict:
    """
    This function is used to import the data from the config file.
    """

    sets = {}
    params = {}
    vars = {}
    forms = {}

    config_file = (
        Path(__file__).parent.parent.parent.parent
        / "data/shipping"
        / data_folder
        / "fast_loop"
        / "config.yml"
    )
    planning_model = (
        Path(__file__).parent.parent.parent.parent / "tmp/planning" / planning_model
    )
    variable_file = (
        Path(__file__).parent.parent.parent.parent
        / "data/shipping"
        / data_folder
        / "fast_loop"
        / "variables.yml"
    )

    default_parameters = DefaultParams("default")

    default_parameters.filter_params(vector)

    default_parameters = default_parameters.formulation_parameters

    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_file} does not exist.")

    if not planning_model.exists():
        raise FileNotFoundError(f"Planning model {planning_model} does not exist.")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    with open(variable_file, "r") as f:
        variables = yaml.safe_load(f)

    for key, item in config["Time"].items():
        if key != "total_duration":
            sets[key] = Set(
                initialize=[
                    val * item
                    for val in range(config["Time"]["total_duration"] // item)
                ]
            )

    for key, value in config["param_source"]["default_data"].items():
        param = default_parameters.copy()
        for _key in value:
            param = param[_key]

        if isinstance(param, list):
            if random_param is True:
                param = (param[2] - param[0]) * rand() + param[0]
                params[key] = Param(initialize=param, mutable=False)
            else:
                params[key] = Param(initialize=param[1], mutable=False)
        else:
            params[key] = Param(initialize=param, mutable=False)

    for item in config["param_source"]["planning_model"]:
        with open(planning_model, "r") as f:
            data = yaml.safe_load(f)

        for key, value in data.items():
            params[key] = Param(initialize=param, mutable=False)

    for _, value in variables["variables"].items():
        vars[value["name"]] = Var(
            *[sets[_key] for _key in value["time_duration"]],
            within=(
                NonNegativeReals
                if value["time_duration"] == "positive_real"
                else NonNegativeIntegers
            ),
        )
    
    for key, param in variables["parameters"].items():
        params[key] = Param(initialize=param, mutable=False)
        
    for key, value in variables["formulations"].items():
        forms[key] = value 

    return {"sets": sets, "params": params, "vars": vars, "forms": forms}


def import_fast_functions(data_folder: str, sets: dict) -> dict:
    """
    This function is used to import data from the functions file
    """
    funcs = {
        "equations": {},
        "constraints": {},
        "objectives": {},
    }

    equations_path = (
        Path(__file__).parent.parent.parent.parent
        / "data/shipping"
        / data_folder
        / "fast_loop"
        / "equations.py"
    )

    functions_path = (
        Path(__file__).parent.parent.parent.parent
        / "data/shipping"
        / data_folder
        / "fast_loop"
        / "functions.yml"
    )

    if not equations_path.exists():
        raise FileNotFoundError(f"Equations file {equations_path} does not exist.")

    if not functions_path.exists():
        raise FileNotFoundError(f"Functions file {functions_path} does not exist.")

    with open(functions_path, "r") as f:
        functions = yaml.safe_load(f)

    mod_name = equations_path.stem
    spec = importlib.util.spec_from_file_location(mod_name, equations_path)
    _funcs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_funcs)

    for key, value in functions["equations"].items():
        if value["name"] in dir(_funcs):
            func = getattr(_funcs, value["name"])
            funcs["equations"][key] = Constraint(
                *[sets[_key] for _key in value["domain"]], rule=func
            )
        else:
            raise ValueError(f"Function {key} not found in equations file.")

    for key, value in functions["constraints"].items():
        if value["name"] in dir(_funcs):
            func = getattr(_funcs, value["name"])
            funcs["constraints"][key] = Constraint(
                *[sets[_key] for _key in value["domain"]], rule=func
            )
        else:
            raise ValueError(f"Function {key} not found in constraints file.")

    for key, value in functions["objectives"].items():
        if value["name"] in dir(_funcs):
            func = getattr(_funcs, value["name"])
            funcs["objectives"][key] = Objective(
                rule=func, sense=maximize if value["sense"] == "max" else minimize
            )
        else:
            raise ValueError(f"Function {key} not found in objectives file.")
    return funcs


def args_dict():
    args = {
        "vector": None,
        "fast": {
            "data_folder": None,
            "planning_model": None,
            "random_param": False,
            "horizon": 28,
        },
        "slow": {},
        "demand_prediction": {
            "country": "EU",
            "frequency": "monthly",
            "sector": "industry",
            "scale": 24.3,
        },
        "weather_data": {"weather_file": None},
        "shipping": {
            "mean_transit_time": 840,
            "std_transit_time": 48,
            "mean_ship_arrival_time": 168,
            "std_ship_arrival_time": 34,
        },
    }
    return args


def temporal_align(weather, kalman_filter, randomise: Optional[bool] = False):
    """
    This function temporally aligns the weather data with the demand data.
    and optionaly starts at a random opint in the dataseries.
    """
    if randomise:
        random_start = randint(0, len(weather) - 1)
    else:
        random_start = 0

    weather_data = weather[random_start:] + weather[:random_start]
    month = (random_start % 8760) // 730
    filter_month = kalman_filter._predict(1).index[0].month

    diff = month - filter_month if month > filter_month else month - filter_month + 12

    for _ in range(diff):
        kalman_filter._update()

    return kalman_filter, weather_data
