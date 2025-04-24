"""
This module contains the Functions class, which is used to represent the functions of the node.
"""
from __future__ import annotations
from typing import Union, Optional, List
from types import FunctionType 
from .variables import Variables
import re

class Functions:

    def __init__(self, id: Union[str,float], outputs: dict) -> None:
        self._funcs = {}
        self._targs = {}
        self._collection = {}
        self._vals = None
        self._id = id
        self._outputs = outputs
        pass

    def add(self, value: FunctionType, key: Union[str, int, float],
            targ: Optional[Union[float, int, str]] = None) -> None:
        """
        Adds a function to the node.
        """
        if not isinstance(key, (str, int, float)):
            raise TypeError(f"Key {key} must be a string")
        if not callable(value):
            raise TypeError(f"Value {value} must be a float or an integer")
        
        self._funcs[key] = value
        if targ is not None:
            if not isinstance(targ, (float, int, str)):
                raise TypeError(f"Target {targ} must be a float or an integer")
            if targ not in self._outputs:
                raise ValueError(f"Target {targ} not found in outputs")
            self._targs[key] = targ
        else:
            self._targs[key] = self._id
    
    def __gettitem__(self, key: Union[str,float,int]) -> Union[FunctionType,dict]:
        """
        Gets the value of the function.
        """
        if key not in self._funcs and key not in self._collection:
            raise KeyError(f"Key {key} not found in functions or collections")
        
        if key in self._collection:
            return {k: self._funcs[k] for k in self._collection[key]}
        else:
            return self._funcs[key]

    def __setitem__(self, key: Union[str,float,int], value: FunctionType) -> None:
        """
        Sets the value of the function.
        """
        if key not in self._funcs:
            raise KeyError(f"Key {key} not found in functions")
        
        self._funcs[key] = value
        return None
    
    def __contains__(self, key: Union[str,float,int]) -> bool:
        """
        Checks if the function exists in the node.
        """
        return key in self._funcs
    
    def collection(self,key: str, value: List[Union[str,float,int]]) -> None:
        """
        Adds a collection of functions to the node.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key {key} must be a string")
        if not isinstance(value, list):
            raise TypeError(f"Value {value} must be a list")
        
        if key in self._collection:
            raise KeyError(f"Key {key} already exists in collection")
        if key in self._funcs:
            raise KeyError(f"Key {key} already exists in functions")
        
        for v in value:
            if v not in self._funcs:
                raise KeyError(f"Key {v} not found in functions. Add the functions first") 
        self._collection[key] = value
        return None

    def evaluate(self, vars) -> dict:
        """
        
        """
        if not isinstance(vars, dict):
            raise TypeError(f"Vars {vars} must be a dictionary")
        
        res = {targ: {} for targ in self._targs.values()}

        for k, v in self._funcs.items():
            if k not in self._targs:
                raise KeyError(f"Key {k} not found in targets")

            res[self._targs[k]][k] = v(vars)
        self._vals = res
        return res
    
    def linearise(self,targ):
        """
        This function linearises the functions of the node.
        """
        new_vars = {}
        for key, func in self._funcs.items():
            if (
                self._vals is not None and
                self._targs[key] in self._vals
                ):
                val = self._vals[self._targs[key]][key]
            else:
                val = None
            if self._targs[key] == self._id or self._targs[key] == targ:
                continue
            else:
                if self._targs[key] not in new_vars:
                    new_vars[self._targs[key]] = {}
                new_vars[self._targs[key]][key] = val
                self._targs[key] = targ
        return new_vars


    
