"""
This module contains the Variables class, which is used to represent the variables of the node.
"""
from __future__ import annotations
from typing import Union, Optional, List 
import re

class Variables:

    def __init__(self, id: Union[str,float], outputs: dict) -> None:
        self._vars = {}
        self._collection = {}
        self._rngs = {}
        self._id = id
        self._outputs = outputs
        pass

    def get_vars(self) -> dict:
        """
        Returns the variables of the node.
        """
        return self._vars

    def add(self, key: str, value: Union[float, int],
            range: Optional[list[Union[float,int]]] = None) -> None:
        """
        Adds a variable to the node.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key {key} must be a string")
        if not isinstance(value, (float, int, type(None))):
            raise TypeError(f"Value {value} must be a float or an integer")
        
        self._vars[key] = value
        self._rngs[key] = range

    
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
        if key[-3:] == '_pt':
            self.add(key, value)
            if 'pt' not in self._collection:
                self._collection['pt'] = []
            self._collection['pt'] = [key]  

        if key not in self._vars:
            raise KeyError(f"Key {key} not found in variables")
        
        self._vars[key] = value
        return None

    
    def __contains__(self, key: str) -> bool:
        """
        Checks if the variable exists in the node.
        """
        return key in self._vars
    
    def get_rng(self, key: str) -> Optional[list[Union[float,int]]]:
        """
        Returns the range of the variable.
        """
        if key not in self._rngs:
            return None
        
        return self._rngs[key]

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
    
    def get_collection(self, name:str) -> dict:
        """
        Returns the collection of functions.
        """
        if name not in self._collection:
            raise KeyError(f"Key {name} not found in collection")
        return {idx: self._vars[idx] for idx in self._collection[name]}