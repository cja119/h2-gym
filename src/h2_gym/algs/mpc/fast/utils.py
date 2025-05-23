"""
Utils file for the inner loop of the model predictive control (MPC) algorithm.
"""

import yaml
from pathlib import Path
from pyomo.environ import value
import sys, os
import contextlib
import numpy as np

def add_equations(model, environment_name: str) -> None:
    """
    Adds the equations to the model.
    """

    current_path = Path(__file__).parent
    data_path = (
        current_path.parent.parent / "data/shipping/" + environment_name + "/fast_loop"
    )

@contextlib.contextmanager
def suppress_output(supress: bool = True):
    if supress:
        with open(os.devnull, "w") as devnull:
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = devnull, devnull
            try:
                yield
            finally:
                sys.stdout, sys.stderr = old_out, old_err
    else:
        yield
        pass

def ext_visualise_output(
        solve,
        axs,
        run_count,
        time_step=24,
        joined_data=None,
        fig=None,
    ):
        """
        Extracts latent states and dynamically updates plots across runs.
        Args:
            solve: Pyomo model instance to extract variables from.
            axs: Matplotlib axes array for plotting.
            run_count: Current run count (int).
            time_step: Number of time steps per run (default 24).
            joined_data: Dict to accumulate data across runs (default None).
            fig: Matplotlib figure (optional, for canvas redraw).
            lexicographic: Which instance is being solved (default 1).
        Returns:
            joined_data: Updated joined_data dictionary.
        """

        # Gather time-series data
        steps = range(run_count * time_step, (run_count + 1) * time_step + 1)
        shifted = range(0, time_step + 1)
        daily_shifted = range(0, time_step + 1, 24)
        daily_steps = range(run_count * time_step, (run_count + 1) * time_step + 1, 24)
        cumulative_profit = [value(getattr(solve, "cumulative_profit")[t]) for t in shifted]
        n_ordered = [value(getattr(solve, "n_ship_ordered")[t]) for t in daily_shifted]
        vector_storage = [value(getattr(solve, "vector_storage")[t]) for t in shifted]
        cumulative_charge = [value(getattr(solve, "cumulative_charge")[t]) for t in shifted]
        energy_turbine = [value(getattr(solve, "energy_wind")[t]) for t in shifted]
        energy_conversion = [value(getattr(solve, "n_active_trains_conversion")[t]) for t in shifted]
        n_ship_sent = [value(getattr(solve, "n_ship_sent")[t]) for t in daily_shifted]
        hydrogen_storage = [
            value(getattr(solve, "hydrogen_storage")[t]) for t in shifted
        ]

        label = f"Run {run_count}"

        # Plot all subplots, joining with previous runs
        if joined_data is None or run_count == 1:
            joined_data = {
                "steps": list(steps),
                "daily_steps": list(daily_steps),
                "cumulative_profit": list(cumulative_profit),
                "n_ordered": list(n_ordered),
                "vector_storage": list(vector_storage),
                "cumulative_charge": list(cumulative_charge),
                "energy_turbine": list(energy_turbine),
                "energy_conversion": list(energy_conversion),
                "n_ship_sent": list(n_ship_sent),
                "hydrogen_storage": list(hydrogen_storage),
            }
        else:
            joined_data["steps"].extend(steps)
            joined_data["daily_steps"].extend(daily_steps)
            joined_data["cumulative_profit"].extend(cumulative_profit)
            joined_data["vector_storage"].extend(vector_storage)
            joined_data["n_ordered"].extend(n_ordered)
            joined_data["cumulative_charge"].extend(cumulative_charge)
            joined_data["energy_turbine"].extend(energy_turbine)
            joined_data["energy_conversion"].extend(energy_conversion)
            joined_data["n_ship_sent"].extend(n_ship_sent)
            joined_data["hydrogen_storage"].extend(hydrogen_storage)

        # Plot joined data
        axs[0, 0].plot(
            joined_data["steps"],
            [x / 1_000_000 for x in joined_data["cumulative_profit"]],
            label=label,
            color="black",
        )
        axs[0, 0].set(title="Cumulative Profit", xlabel="Time Step", ylabel="[M$]")
        axs[0, 0].grid(True)

        axs[0, 1].plot(
            joined_data["daily_steps"],
            joined_data["n_ordered"],
            label='N-Ordered' if run_count == 1 else None,
            color="black",
        )
        axs[0, 1].plot(
            joined_data["daily_steps"],
            joined_data["n_ship_sent"],
            label='N-Sent' if run_count == 1 else None,
            color="grey",
            linestyle="--",
        )

        axs[0, 1].set(title="Number Ships Ordered", xlabel="Time Step", ylabel="Count")
        axs[0, 1].grid(True)
        axs[0, 1].legend(loc="upper left", fontsize=8)

        axs[0, 2].plot(
            joined_data["steps"],
            joined_data["vector_storage"],
            label=label,
            color="black",
        )
        axs[0, 2].set(title="Stored Vector", xlabel="Time Step", ylabel="[kt]")
        axs[0, 2].grid(True)
        axs[1, 0].plot(
            joined_data["steps"],
            [x / 1000 for x in joined_data["cumulative_charge"]],
            label=label,
            color="black",
        )
        axs[1, 0].set(title="Ship Fill", xlabel="Time Step", ylabel="Mass (H2-eq) [kt]")
        axs[1, 0].grid(True)

        axs[1, 1].plot(
            joined_data["steps"],
            joined_data["energy_turbine"],
            label=label,
            color="black",
        )
        axs[1, 1].set(title="Single Turbine Energy", xlabel="Time Step", ylabel="Energy [GJ/h]")
        axs[1, 1].grid(True)
        # Limit the number of x-ticks for readability
        max_ticks = 10
        daily_steps = joined_data["daily_steps"]
        if len(daily_steps) > max_ticks:
            xticks = list(np.linspace(daily_steps[0], daily_steps[-1], max_ticks, dtype=int))
        else:
            xticks = daily_steps

        axs[1, 1].set_xticks(xticks)
        axs[1, 1].set_xticklabels([str(x) for x in xticks])

        axs[1, 2].plot(
            joined_data["steps"],
            joined_data["energy_conversion"],
            label=label,
            color="black",
        )
        axs[1, 2].set(
            title="Number Active Conversion Trains", xlabel="Time Step", ylabel="N Trains"
        )
        axs[1, 2].grid(True)
        if fig is not None:
            fig.tight_layout()
            fig.canvas.draw()  # Redraw canvas if needed

        return joined_data