"""
This module contains the Graph class, which is used to represent a graphical structure of the problem
"""
from __future__ import annotations
from ..node import Node
from .builder import GraphBuilder
from typing import Union
from collections import OrderedDict

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
        self._props = ["edges", "nodes"]
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
        self._nodes[node_id] = Node(node_id)
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

    def evaluate(self) -> None:
        """
        Evaluates the graph.
        """
        graph_outs = {}

        for id,node in self._nodes.items():
            outs = node.evaluate()
            pops = []
            if outs is not None:
                for key in outs:
                    if key[-1] =='+':
                        graph_outs[key[:-1]] = outs[key]
                        pops.append(key)
                    else:
                        pass
                
                for key in pops:
                    outs.pop(key)
                
                for edge,out in outs.items():
                    self._nodes[edge].set_input(out)
        return graph_outs 
        
                
        #return None
