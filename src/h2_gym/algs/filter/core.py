"""
This module enables demand projection for the nodes.
"""
from __future__ import annotations
from typing import Optional
from pathlib import Path
from pandas import read_csv, DataFrame, to_datetime
class KalmanFilter:
    """
    This class implements a Kalman filter for demand projection.
    """

    def __init__(self, data: str, country: str, unit: str = 'TJ', path: Optional[str] = None) -> None:
        """
        Initializes the Kalman filter class.
        """
        self._data = self.get_data(data, path, country, unit)
        self._inputs = None
        self._outputs = None
        self._props = None

        return None
    
    def predict():
        """
        Predicts the demand using the Kalman filter.
        """
        pass

    def update():
        """
        Updates the Kalman filter with new data.
        """
        pass

    def get_data(self, data: str, path: Optional[str], country: Optional[str], period: Optional[str] = None,
                 demand_type: Optional[str] = None) -> DataFrame:

        if path is None:
            path = Path(__file__).parent.parent.parent / f"""
            data/shipping/demand/src/data/analyzed/{period}_demand_clean.csv
            """
        
        data = read_csv(path)
        loc_mask = data['country'] == country
        if loc_mask.sum() == 0:
            print(f"[NOTE] Country {country} not found in the data, defaulting to EU for demand shape.")
            country = 'EU'
        
        mask = (data['type'] == demand_type) & loc_mask
        if mask.sum() == 0:
            print(f"[NOTE] Demand type {demand_type} not found in the data, defaulting to industrial for demand shape.")
            demand_type = 'industrial'
            dem_mask = data['type'] == demand_type
            if mask.sum() == 0:
                print(f"[NOTE] Demand type {demand_type} not found in the data, defaulting to total for demand shape.")
                demand_type = 'total'
                mask = data['type'] == demand_type
                if mask.sum() == 0:
                    raise ValueError(f"Demand type {demand_type} not found in the data.")

        data = data.loc[mask]

        dates = to_datetime(
            ['01/' + str(month) + '/' + str(year) for month, year in zip(data['month'].values, data['year'].values)],
            dayfirst=True
            ) 
        
        train_mask = [i.date <  dates[0].date for i in dates]
        test_mask = [i.date >= dates[0].date for i in dates]
        
        train_data = dates[train_mask].values()
        test_data = dates[test_mask].values()


        
