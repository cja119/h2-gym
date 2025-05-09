"""
This class will interact with the planning model (fond at github.com/cja119/stochasticmodel)
and solve the model to perform the planning operatinos for the hydrogen production region. 
"""
from __future__ import annotations
from typing import Optional 
from h2_plan.opt import  H2Planning
from h2_plan.data import DefaultParams
from pathlib import Path

class Planning:
    def __init__(self,data: Optional[str] = None) :
        """
        Initializes the planning model. 
        """

        self._model = None
        self._inputs = None
        self._outputs = None
        self._props = None

        if self._data is None:
            self._data = DefaultParams('default')
        else:
            self._data = DefaultParams(data)
            
        return None
    
    def get_data(self) -> str:
        """
        Returns the data of the planning model. 
        """
        return self._data
    
    def save_data(self, filename: str, file_path: Optional[str]) -> None:
        """
        Saves the loaded datafile for the planning model 
        """
        if file_path is None:
            file_path = self._data.path.parent / filename
        else:
            file_path = Path(file_path) / filename

        with open(file_path, "w") as f:
            f.write(self._data.to_json())
        return None
    
    def load_data(self, filename: str, file_path: Optional[str]) -> None:
        """
        Loads the data for the planning model. 
        """
        if file_path is None:
            file_path = self._data.path.parent / filename
        else:
            file_path = Path(file_path) / filename

        with open(file_path, "r") as f:
            self._data = DefaultParams.from_json(f.read())
        return None
    


    

    
    
    
    