"""
This module contains the shipping environment which performs a bilevel
"""

from __future__ import annotations
from h2_gym.data.shipping.ngdemand import NGDemand
from h2_gym.graph.temporal import StochasticGenerator, Isochronous
from h2_gym.graph.node import Node
from h2_gym.graph.spatial import SpaceGraph
from h2_gym.algs.filter import KalmanFilter
from pathlib import Path
import yaml
from .utils import (
    get_ng_data
)


class ShippingEnv:

    def __init__(self,file: str) -> None:
        
        self._file = file
        self._generator = StochasticGenerator()
        self._space_graph = SpaceGraph()
        self._time_graph = Isochronous(self._space_graph,self._generator)
        
        pass

    def get_data(self, planning_model: str):
        """
        Loads the environment's data.
        """

        current_path = Path(__file__).parent
        planning_model_path = current_path.parent.parent/ "tmp/planning"/ planning_model
        data_path = current_path.parent.parent / "data/shipping"

        planning_results = yaml.safe_load(open(planning_model_path, 'r'))

        self._generator.bind_dataset(
            dataset=get_ng_data(
                data='natural_gas_demand.csv',
                path=data_path / 'csv',
                country=self._import_country,
                unit='TJ'
                ).data()['OBS_VALUE'].values * self.demand_sf / 730,
                varname = 'demand',
                time_duration=730
        )


        pass


    