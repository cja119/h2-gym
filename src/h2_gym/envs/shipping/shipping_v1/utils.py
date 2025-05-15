"""
Utility functions for the shipping environment.
"""

from typing import Optional
from pathlib import Path
import pandas as pd
from pycountry import countries
from h2_plan.data import DefaultParams
from pyomo.environ import Param, Set
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


def import_data(
    data_folder: str, planning_model: str, vector: str, random_param: bool = False
) -> Optional[pd.DataFrame]:
    """
    This function is used to import the data from the config file.
    """

    sets = {}
    params = {}

    config_file = (
        Path(__file__).parent.parent.parent.parent
        / "data/shipping"
        / data_folder
        / "config.yml"
    )
    planning_model = (
        Path(__file__).parent.parent.parent.parent / "tmp/planning" / planning_model
    )

    default_parameters = (
        DefaultParams("default").filter_params(vector).formulation_parameters
    )

    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_file} does not exist.")

    if not planning_model.exists():
        raise FileNotFoundError(f"Planning model {planning_model} does not exist.")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    for key, item in config["Time"]:
        if key != "total_duration":
            sets[key] = Set(
                initialize=[
                    val * item
                    for val in range(config["Time"]["total_duration"] // item)
                ]
            )

    for key, value in config["default_data"].items():
        param = default_parameters.copy()
        for _key in value:
            param = param[_key]

        params[key] = Param(initialize=param, mutable=False)

    pass
