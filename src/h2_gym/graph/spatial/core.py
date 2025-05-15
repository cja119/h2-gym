"""
This module contains the Graph class, which is used to represent a graphical structure of the problem
"""

from __future__ import annotations
from ..node import Node
from .builder import GraphBuilder
from typing import Union, Optional
from collections import OrderedDict
from .utils import get_rang
from re import sub as re_sub


class SpaceGraph:
    """ """

    def __init__(self) -> None:
        """ """
        self._adjacency_matrix = None
        self._acyclic = None
        self._connected = None
        self._nodes = OrderedDict()
        self._props = ["edges", "nodes"]
        self._edges = []
        self._built = False
        self._acyclic = True
        self._adjacency_matrix = None
        self._state = 0

        return None

    def __getitem__(self, key: Union[int, str]) -> Node:
        """
        Returns the node with the given key.
        """
        if key not in self._nodes:
            raise ValueError(f"Node {key} not found in the graph")
        return self._nodes[key]

    def __iter__(self):
        return self

    def __next__(self):
        state = self._state
        if self._state >= len(self._nodes):
            self._state = 0
            raise StopIteration  #  Termination condition
        self._state += 1
        keys = list(self._nodes.keys())
        return self[keys[state]]

    def builder(self) -> GraphBuilder:
        """
        Returns a GraphBuilder object to build the graph.
        """
        return GraphBuilder(self)

    def add_node(self, node_id: Union[int, float, str]) -> None:
        """
        Adds a node to the graph.
        """
        self._nodes[node_id] = Node(node_id)
        return None

    def add_edge(
        self, node_id: Union[int, float, str], output_id: Union[int, float, str]
    ) -> None:
        """
        Adds an edge to the graph.
        """

        if node_id not in self._nodes:
            raise ValueError(f"Node {node_id} not found in the graph")
        if re_sub(r"[+]", "", output_id) not in self._nodes:
            raise ValueError(f"Node {output_id} not found in the graph")
        else:
            self._edges.append((node_id, output_id))
            self._nodes[node_id].set_output(output_id)
            self._nodes[re_sub(r"[+]", "", output_id)].set_input(node_id)
            if output_id[-1] != "+":
                if list(self._nodes.keys()).index(node_id) > list(
                    self._nodes.keys()
                ).index(output_id):
                    self._acyclic = False
        return None

    def evaluate(self, graph_inputs: Optional[dict] = None) -> None:
        """
        Evaluates the graph. If no input is given we take the values stored in the nodes
        as the default initialisation.
        """
        if graph_inputs is not None:
            for edge, input in graph_inputs.items():
                if edge not in self._nodes:
                    raise ValueError(f"Node {edge} not found in the graph")
                self._nodes[edge].set_input(input)

        graph_outs = {}
        for id, node in self._nodes.items():
            outs = node.evaluate()
            pops = []
            if outs is not None:
                for key in outs:
                    if key[-1] == "+":
                        graph_outs[key[:-1]] = outs[key]
                        pops.append(key)
                    else:
                        pass

                for key in pops:
                    outs.pop(key)

                for edge, out in outs.items():
                    self._nodes[edge].set_var(out)
        return graph_outs

    def linearise(self, _outs: Optional[dict] = None) -> None:
        """
        Linearises the graph. This is done by removing the edges that are not needed
        to evaluate the graph.
        """
        if _outs is not None:
            _vars, _rngs = _outs
        else:
            _vars, _rngs = {}, {}
        if not self._acyclic:
            raise ValueError("Graph is not acyclic")

        _keys = list(self._nodes.keys())

        # Perform one pass through the graph to linearise it internally
        for origin, target in zip(_keys, _keys[1:] + [_keys[0] + "+"]):
            _vars = self._nodes[origin].linearise(target, _vars, _rngs)
            _rngs = get_rang(self._nodes, _vars)

        # Determine the new output set
        outs = self.evaluate()
        return outs, get_rang(self._nodes, outs)
