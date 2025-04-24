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
    