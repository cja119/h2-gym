"""
This module contains the Graph class, which is used to represent a graphical structure of the problem
"""
from __future__ import annotations
from ..node import Node
from .builder import GraphBuilder
from typing import Union
from collections import OrderedDict
import jax.numpy as jnp

class SpaceGraph:
    """
    
    """

    def __init__(self) -> None:
        """
        
        """
        self._adjacency_matrix = None
        self._acyclic = None
        self._connected = None
        self._nodes = OrderedDict()
        self._edges = []
        self._built = False
        self._acyclic = True
        self._adjacency_matrix = None

        return None

    def __getitem__(self, key: Union[int, str]) -> Node:
        """
        Returns the node with the given key.
        """
        if key not in self._nodes:
            raise ValueError(f"Node {key} not found in the graph")
        return self._nodes[key]

    def builder(self) -> GraphBuilder:
        """
        Returns a GraphBuilder object to build the graph.
        """
        return GraphBuilder(self)
    
    def add_node(self, node_id: Union[int,float,str]) -> None:
        """
        Adds a node to the graph.
        """
        self._nodes[node_id] = Node()
        return None
    
    def add_edge(self, node_id: Union[int,float,str],
                 output_id: Union[int,float,str]) -> None:
        """
        Adds an edge to the graph.
        """
        
        if node_id not in self._nodes:
            raise ValueError(f"Node {node_id} not found in the graph")
        if output_id not in self._nodes:
            raise ValueError(f"Node {output_id} not found in the graph")
        else:
            self._edges.append((node_id, output_id))
            self._nodes[node_id].set_output(output_id)
            self._nodes[output_id].set_input(node_id)
            if (
                list(self._nodes.keys()).index(node_id) > \
                    list(self._nodes.keys()).index(output_id)
            ):
                self._acyclic = False
        return None
    
