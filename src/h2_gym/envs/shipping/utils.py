"""
Utility functions for the shipping environment.
"""

from typing import Optional 
from pathlib import Path
import pandas as pd
from pycountry import countries

def get_ng_data(data, path, country, unit) -> str:
    """
    Returns the data of the natural gas demand class
    """
    if data[-4:] != '.csv':
        data = data + '.csv'

    # Handling the path
    path = Path(path) if path is not None else Path(__file__).parent / 'csv'
    dataset = pd.read_csv(path / data)

    # Updating the column names to the country names
    dataset.set_index("REF_AREA", inplace=True)
    dataset.index = dataset.index.map(
        lambda i: countries.get(alpha_2=i.upper()).name
    )

    # Finding LNG import data, filtering by unit and country
    dataset = dataset.loc[country][
        (dataset.loc[country]['FLOW_BREAKDOWN'] == 'IMPLNG') &
        (dataset.loc['United Kingdom']['UNIT_MEASURE'] == unit)
    ]
    return dataset