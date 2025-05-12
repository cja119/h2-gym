"""
Helper to interact with the sampler 
"""
from __future__ import annotations
from abc import ABC
from typing import Any, Dict, List, Optional, Tuple

import sys
import os

sys.path.append(os.path.abspath('./mu_F/src'))

# Now import from src


class nested_sampler(ABC):
    """
    This interacts with mu-F to build and solve the nested sampling problem. 
    This will also pull pre-solved solutions form the module if they exist.
    """
    
    def __init__(self, graph):
        """
        Initialize the nested sampler with a graph.
        """
        self.graph = graph
        