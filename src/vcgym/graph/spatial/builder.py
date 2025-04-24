"""
This module contains the Graph class, which is used to represent a graphical structure of the problem
"""

from __future__ import annotations
from ..node import Node
from typing import Union
import jax.numpy as jnp

class GraphBuilder:
    def __init__(self, graph):
        """
        Initializes the graph builder
        """
        self.graph = graph

    def __enter__(self) -> GraphBuilder:
        """
        Enters the graph context
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the graph context
        """
        self.build()
        return None
    
    def __setitem__(self, key: Union[str, int], value: Node) -> None:
        """
        Embeds a node in the graph
        """

        if key == 'nodes':
            for node in value:
                self.graph.add_node(node)
        elif key == 'edges':
            for edge in value:
                self.graph.add_edge(*edge)
        else:
            setattr(self.graph, '_'+key, value)
        
        return None        

    def build(self) -> None:
        """
        Builds the graph
        """
        return None
                
            
            



    