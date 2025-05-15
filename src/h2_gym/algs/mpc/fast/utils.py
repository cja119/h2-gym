"""
Utils file for the inner loop of the model predictive control (MPC) algorithm.
"""

import yml
from Pathlib import Path


def add_equations(model, environment_name: str) -> None:
    """
    Adds the equations to the model.
    """

    current_path = Path(__file__).parent
    data_path = (
        current_path.parent.parent / "data/shipping/" + environment_name + "/fast_loop"
    )
