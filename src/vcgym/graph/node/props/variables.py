"""
This module contains the Variables class, which is used to represent the variables of the node.
"""
from __future__ import annotations
from typing import Union, Optional, List
import re

class Variables:

    def __init__(self, id: Union[str,float], outputs: dict) -> None:
        self._vars = {}
        self._targs = {}
        self._collection = {}
        self._id = id
        self._outputs = outputs
        pass

    def get_vars(self) -> dict:
        """
        Returns the variables of the node.
        """
        return self._vars

    def add(self, key: str, value: Union[float, int], targ: Optional[Union[float, int]] = None) -> None:
        """
        Adds a variable to the node.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key {key} must be a string")
        if not isinstance(value, (float, int)):
            raise TypeError(f"Value {value} must be a float or an integer")
        
        self._vars[key] = value
        if targ is not None:
            if not isinstance(targ, (float, int)):
                raise TypeError(f"Target {targ} must be a float or an integer")
            if (
                re.sub(r"[+-]","",targ) not in self._outputs 
                and re.sub(r"[+-]","",targ) != self._id
                ):
                raise ValueError(f"Target {targ} not found in outputs")
            self._targs[key] = targ
        else:
            self._targs[key] = self._id
    
    def __getitem__(self, key: Union[str,float,int]) -> Union[float,int,dict]:
        """
        Gets the value of the variable or colleciton of variables.
        """
        if key not in self._vars and key not in self._collection:
            raise KeyError(f"Key {key} not found in variables or collections")
        
        if key in self._collection:
            return {k:self._vars[k] for k in self._collection[key]}
        else:
            return self._vars[key]


    def __setitem__(self, key: str, value: Union[float, int]) -> None:
        """
        Sets the value of the variable.
        """
        if key not in self._vars:
            raise KeyError(f"Key {key} not found in variables")
        
        self._vars[key] = value
        return None

    
    def __contains__(self, key: str) -> bool:
        """
        Checks if the variable exists in the node.
        """
        return key in self._vars

    def collection(self, key: str, value: List[Union[str,float,int]]) -> None:
        """
        Adds a collection of variables to the node.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key {key} must be a string")
        if not isinstance(value, list):
            raise TypeError(f"Value {value} must be a list")
        
        if key in self._collection:
            raise KeyError(f"Key {key} already exists in collection")
        if key in self._vars:
            raise KeyError(f"Key {key} already exists in variables")
        
        for v in value:
            if v not in self._vars:
                raise KeyError(f"Key {v} not found in variables. Add the variables first") 
        self._collection[key] = value
        return None
