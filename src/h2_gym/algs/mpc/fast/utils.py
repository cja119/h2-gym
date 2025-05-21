"""
Utils file for the inner loop of the model predictive control (MPC) algorithm.
"""

import yaml
from pathlib import Path
import sys, os
import contextlib

def add_equations(model, environment_name: str) -> None:
    """
    Adds the equations to the model.
    """

    current_path = Path(__file__).parent
    data_path = (
        current_path.parent.parent / "data/shipping/" + environment_name + "/fast_loop"
    )

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = devnull, devnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_out, old_err
