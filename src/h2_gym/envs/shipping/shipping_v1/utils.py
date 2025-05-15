"""
Utility functions for the shipping environment.
"""

from typing import Optional
from pathlib import Path
import importlib.util
from h2_plan.data import DefaultParams
from pyomo.environ import Param, Set, Constraint, Objective, maximize, minimize
from numpy.random import rand
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

    default_parameters = DefaultParams("default")

    default_parameters.filter_params(vector)

    default_parameters = default_parameters.formulation_parameters

    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_file} does not exist.")

    if not planning_model.exists():
        raise FileNotFoundError(f"Planning model {planning_model} does not exist.")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

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

    return {"sets": sets, "params": params}


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
            'vector': None,
            'fast':{
                "data_folder": None,
                "planning_model": None,
                "random_param": False,
                "horizon": 28
            },
            'slow':{
            },
            'demand_prediction':{
                "country": "EU",
                "frequency": "monthly",
                "sector": "industry",
                "scale": 24.3,
            },
            'weather_data':{
                'weather_file': None
            }
        }
    return args