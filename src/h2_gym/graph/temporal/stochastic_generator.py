""" """

from __future__ import annotations
from glob import glob
from typing import Optional
from h2_gym.graph.node import Node


class StochasticGenerator:
    """
    Implements the stochastic generator class
    """

    def __init__(self, time_grid=1) -> None:
        """
        Initializes the stochastic generator class
        """
        self._time = 0
        self._targets = {}
        self._varnames = []
        self._node_id = {}
        self._maxtimes = {}
        self._datasets = {}
        self._time_dur = {}
        self._target = {}

    def bind_variable(
        self, node: Node, varname: str, time_duration: Optional[int] = None
    ):
        """
        Binds a variable to the stochastic generator
        """
        if varname in self._varnames:
            raise ValueError(
                f"Variable {varname} already exists in the stochastic generator"
            )

        if varname not in node["variables"]:
            node["variables"].add(
                key=varname,
                value=self._datasets[varname][self._time],
                range=(min(self.dataset), max(self.dataset)),
            )
        else:
            node["variables"][varname] = self._datasets[varname][self._time]

        self._varnames.append(varname)
        self._target[varname] = node["variables"][varname]
        self._node_id[varname] = node.get_id()
        self._time_dur[varname] = time_duration

    def bind_dataset(
        self,
        varname,
        path: Optional[str] = None,
        filenames: Optional[str] = None,
        dataset: Optional[str] = None,
        time_duration: Optional[int] = None,
    ):
        """
        Binds a dataset to the stochastic generator
        """

        for file_name in filenames:
            csvs_files = glob(str(path) + "/" + file_name)

        if dataset is None:
            self._datasets[varname] = []
            for filename in csvs_files:

                with open(filename) as f:
                    next(f)

                    for line in f:
                        parts = line.strip().split()

                        if len(parts) == 2:
                            _, value = parts
                            self._datasets[varname].extend(
                                [float(value)] * time_duration
                            )
                        elif len(parts) == 1:
                            value = float(parts[0])
                            self._datasets[varname].extend(
                                [float(value)] * time_duration
                            )

            self._maxtimes[varname] = len(self._datasets[varname])
        else:
            self._datasets[varname] = dataset
            self._maxtimes[varname] = len(self._datasets[varname])

    def update(self):
        """
        Updates the stochastic generator
        """
        self._time += 1
        for varname in self._varnames:
            self._target[varname] = self._datasets[varname][
                self._time % self._maxtimes[varname]
            ]

        result = {
            self._node_id[varname]: {varname: self._target[varname]}
            for varname in self._varnames
        }

        return result
