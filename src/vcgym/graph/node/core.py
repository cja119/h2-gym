"""
Implements the node class
"""

from __future__ import annotations
from typing import Union

class Node:
    def __init__(self) -> None:
        """
        Initializes the node class
        """
        self._id = None
        self._inputs = []
        self._outputs = []
        self._params = {}
        self._metadata = {}
        self._funcs = []
        self._vars = {}
        self._name = None

    def __enter__(self) -> Node:
        """
        Enters the node context
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the node context
        """
        pass

    def __setitem__(self, key: str, value: Union[str, int]) -> None:
        """
        Sets the value of the node
        """

        if key == "inputs":
            self.set_input(value)
        elif key == "outputs":
            self.set_output(value)
        elif key == "name":
            self.set_name(value)
        else:
            raise KeyError(f"Key {key} not found in node")
    
    def __getitem__(self, key: str) -> Union[str, int]:
        """
        Gets the value of the node
        """
        if key == "variables":
            return self.add_vars
        elif key == "functions":
            return self.add_funcs
        else:
            raise KeyError(f"Key {key} not found in node")
        
    def add_vars(self, key: str, value: Union[str, int]) -> None:
        """
        Adds a variable to the node
        """
        self._vars[key] = value
    
    def add_funcs(self, f: function, target: tuple[str,str]) -> None:
        """
        Adds a function to the node
        """
        if target[0] not in self._graph.nodes:
            raise ValueError(f"Node {target[0]} not found in graph")
        
        if target[1] not in self._graph.nodes[target[0]]._vars:
            raise ValueError(f"Variable {target[1]} not found in node {target[0]}")

        self._funcs.append({
            'function': f,
            'target_node': target[0],
            'target_var': target[1]
            })
        return None
    
    def get_id(self) -> str:
        """
        Returns the id of the node
        """
        return self._id
    
    def set_id(self, id: str) -> None:
        """
        Sets the id of the node
        """
        self._id = id
    
    def set_input(self, input: list) -> None:
        """
        Sets the inputs of the node
        """
        self._inputs.append(input)
    
    def get_inputs(self) -> list:
        """
        Returns the inputs of the node
        """
        return self._inputs
    
    def set_output(self, outputs: list) -> None:
        """
        Sets the outputs of the node
        """
        self._outputs.append(outputs)

    def get_outputs(self) -> list:
        """
        Returns the outputs of the node
        """
        return self._outputs

    def set_name(self, name: Union[str,int]) -> None:
        """
        Sets the name of the node
        """
        self._name = name

    def get_name(self) -> Union[str,int]:
        """
        Returns the name of the node
        """
        return self._name