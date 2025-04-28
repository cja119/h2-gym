"""

"""
from __future__ import annotations
from ...spatial import SpaceGraph
from ...node import Node


class Isochronous():
    """
    This class implements a temporal graph, which is a graph with time-dependent edges. This
    graph is isochronous, meaning that the node morphology is time-inedependent. 
    """

    def __init__(self, node) -> None:
        """
        Initializes the temporal graph.
        """
        self._node = node
        self._props = node._props

        return None
    
    def back_pass(self, node: Node) -> None:
        """
        Back propagates the graph.
        """
        self._node = node
        return None
    
    def forward_pass(self, node: Node) -> None:
        """
        Forward propagates the graph.
        """
        outs = self._node.evaluate()

        return None
    
    def linearise(self) -> None:
        """
        Linearises the graph. This is done by removing the edges that are not needed
        to evaluate the graph. 
        """
        node_outs = None
        while node_outs is None or len(node_outs[0]) > 1:
            node_outs = self._node.linearise(node_outs)

        return None
    