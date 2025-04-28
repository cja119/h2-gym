"""

"""
from __future__ import annotations
from h2_gym.graph.spatial import SpaceGraph
from h2_gym.graph.temporal import StochasticGenerator
from h2_gym.graph.temporal import Isochronous
from pathlib import Path
from .utils import (
    add_constants,
    add_equations,
    add_constraints,
    add_inlets,
    add_controls,
    module_loader
)

class HydrogenSupply:
    """
    Hydrogen export class
    """

    def __init__(self,json_file) -> None:
        """
        Initializes the hydrogen export class
        """
        self.file = json_file
        self.space_graph = SpaceGraph()
        self.generator = StochasticGenerator()
        self.graph = Isochronous(self.space_graph,self.generator)
        
        self.get_data()

        return None

    def get_data(self) -> None:
        """
        Gets the data from the json file
        """
        current_path = Path(__file__).parent.parent.parent/"data/supply"

        data, module = module_loader(current_path, self.file)
        
        # The constraints map to themselves
        self_edges = list(zip(data['partial_order'],data['partial_order']))

        with self.space_graph.builder() as gb:
            gb['nodes'] = data['partial_order']
            gb['edges'] = data['edges'] + self_edges
            gb['directed'] = True


        for node in self.space_graph:
            add_constants(node, data)
            add_equations(node, data, module)
            add_constraints(node, data, module)
            add_inlets(node, data)
            add_controls(node, data)

        for _, value in data['uncertainties'].items():
            self.generator.bind_dataset(
                path = current_path,
                filenames = value['files']
                )
            self.generator.bind_variable(
                self.space_graph[value['target_node']],
                value['var_name']
                )

        return None