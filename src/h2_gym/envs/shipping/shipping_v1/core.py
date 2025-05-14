"""
This module contains the shipping environment which performs a bilevel model predictive
control optimisation for the shipping problem.
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
    optimisation_handover,
    environment_handover
)


class ShippingEnvV1:

    def __init__(self,file: str) -> None:
        
        self._file = file
        self._outer_generator = StochasticGenerator()
        self._inner_generator = StochasticGenerator()
        self._space_graph = SpaceGraph()
        self._time_graph = Isochronous(self._space_graph,self._outer_generator)
        
        pass

    
    def step(self):
        """
        Extracts data from the model, solves the inner loop and hands over the results to the outer loop.
        """
        environment_handover(self._model)

        self._inner_loop.update(self._model)
        self._inner_loop.solve()
        self._inner_loop.get_results()
        
        optimisation_handover(self._model)

        
        pass

    

        


    