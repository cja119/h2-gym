"""
This module contains the shipping environment which performs a bilevel
"""

from __future__ import annotations
from h2_gym.data.shipping import NGDemand
from h2_gym.graph.temporal import StochasticGenerator, Isochronous
from h2_gym.graph.node import Node
from h2_gym.graph.spatial import SpaceGraph


class ShippingEnv:

    def __init__(self, import_country, demand_sf: float = 0.025) -> None:
        
        self._generator = StochasticGenerator()
        self._space_graph = SpaceGraph()
        self._time_graph = Isochronous(self._space_graph,self._generator)
        self._generator.bind_dataset(
            dataset=self.get_data(
            import_country,
            demand_sf
            )
        )
        pass
    
    def get_data(self):
        pass

    @staticmethod
    def get_data(import_country, SF):
        """
        Gets the data from the json file
        """
        data = NGDemand('natural_gas_demand.csv', import_country, unit='TJ').data()
        return data['OBS_VALUE'].values * SF

    