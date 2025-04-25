"""

"""
from __future__ import annotations
from vcgym.graph.spatial import SpaceGraph
from vcgym.graph.temporal import StochasticGenerator
from pathlib import Path
import json
from importlib import util

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
        self.get_data()

        return None
    
    def get_data(self) -> None:
        """
        Gets the data from the json file
        """
        current_path = Path(__file__).parent.parent.parent.parent/"data/hydrogen"

        if self.file[:-5] != ".json":
            self.file += ".json"

        with open(current_path / self.file, 'r') as f:
            data = json.load(f)
        
        # Load the module from file
        functions = data['function_file']
        spec = util.spec_from_file_location('node_functions', current_path/functions)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # The constraints map to themselves
        self_edges = list(zip(data['partial_order'],data['partial_order']))

        with self.space_graph.builder() as gb:
            gb['nodes'] = data['partial_order']
            gb['edges'] = data['edges'] + self_edges
            gb['directed'] = True


        for node in self.space_graph:
            if 'constants' in data['nodes'][node.get_id()]:
                for constant,value in data['nodes'][node.get_id()]['constants'].items():
                    node['variables'].add(
                        constant,
                        value
                        )
            
                node['variables'].collection(
                    'constants',
                    list(data['nodes'][node.get_id()]['constants'].keys())
                    )

            if 'equations' in data['nodes'][node.get_id()]:
                for _,value in data['nodes'][node.get_id()]['equations'].items():
                    node['functions'].add(
                        getattr(module,value['name']),
                        value['name'],
                        value['target_node'],
                        value['var_name']
                        )
                    
                node['functions'].collection(
                    'equations',
                    [item['name'] for item in data['nodes'][node.get_id()]['equations'].values()]
                    )

            if 'constraints' in data['nodes'][node.get_id()]:
                for _, constraint in data['nodes'][node.get_id()]['constraints'].items():
                    node['functions'].add(
                        value = getattr(module,constraint['name']),
                        key = constraint['name'],
                        targ = constraint['target_node'],
                        varname = constraint['var_name']
                        )
                    
                    node['variables'].add(
                        key = constraint['var_name'],
                        value = 0,
                        range = None,
                        )
                    
                node['functions'].collection(
                    'constraints',
                    [item['name'] for item in data['nodes'][node.get_id()]['constraints'].values()]
                    )
                
                node['variables'].collection(
                    'constraints',
                    [item['var_name'] for item in data['nodes'][node.get_id()]['constraints'].values()]
                    )
            
            if 'inlets' in data['nodes'][node.get_id()]:
                for _, value in data['nodes'][node.get_id()]['inlets'].items():
                    node['variables'].add(
                        key = value['name'],
                        value = (value['rng'][0] + value['rng'][1]) / 2,
                        range = value['rng'],
                        )
                    
                node['variables'].collection(
                    'inlets',
                    [item['name'] for item in data['nodes'][node.get_id()]['inlets'].values()]
                    )
            
            if 'controls' in data['nodes'][node.get_id()]:
                for _, value in data['nodes'][node.get_id()]['controls'].items():
                    node['variables'].add(
                        key = value['name'],
                        value = (value['rng'][0] + value['rng'][1]) / 2,
                        range = value['rng'],
                        )

            if 'controls' in data['nodes'][node.get_id()]: 
                node['variables'].collection(
                    'controls',
                    [item['name'] for item in data['nodes'][node.get_id()]['controls'].values()]
                    )

        for _, value in data['uncertainties'].items():
            self.stochatic_generator =  StochasticGenerator()
            self.stochatic_generator.bind_dataset(
                path = current_path,
                filenames = value['files']
                )
            self.stochatic_generator.bind_variable(
                self.space_graph[value['target_node']],
                value['var_name']
                )

        return None