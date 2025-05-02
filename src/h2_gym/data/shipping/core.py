"""
This class will pull the natural gas data for different regions and 'clean'
it into a format that cna be used in the shipping model.
"""
from __future__ import annotations


class NGDemand:

    def __init__(self, data: str, country: str, unit:str = 'TJ',path:Optional[str] = None) -> None:
        """
        Initializes the natural gas demand class. 
        """
        self._data = self.get_data(data, path, country, unit)
        self._inputs = None
        self._outputs = None
        self._props = None

        return None
    

    
    @staticmethod
    
    
    def data(self) -> pd.DataFrame:
        """
        Returns the data of the natural gas demand class
        """
        return self._data
    
    

