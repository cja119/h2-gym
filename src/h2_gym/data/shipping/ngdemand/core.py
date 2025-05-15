"""
This class will pull the natural gas data for different regions and 'clean'
it into a format that cna be used in the shipping model.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
from pathlib import Path


class NGDemand:

    def __init__(
        self,
        country,
        data: Optional[str],
        unit: str = "TJ",
        period: Optional[str] = None,
        path: Optional[str] = None,
    ) -> None:
        """
        Initializes the natural gas demand class. Default demand is taken for the EU.
        """
        self._data = self.get_data(data, path, country, unit, period)
        self._inputs = None
        self._outputs = None
        self._props = None

        return None

    @staticmethod
    def get_data(
        data: str, path: Optional[str], country: str, unit: str, period
    ) -> pd.DataFrame:
        """
        Pulls the natural gas demand data from the specified path and cleans it
        into a format that can be used in the shipping model.
        """
        if period is None:
            period = "monthly"
        elif period not in ["monthly", "daily"]:
            raise ValueError("Period must be either 'monthly' or 'daily'")

        if path is None:
            path = (
                Path(__file__).parent
                / f"demand/src/data/analyzed/{period}_demand_clean.csv"
            )

        data = pd.read_csv(path)

    def data(self) -> pd.DataFrame:
        """
        Returns the data of the natural gas demand class
        """
        return self._data
