"""

"""
from __future__ import annotations
from glob import glob

class StochasticGenerator:
    """
    Implements the stochastic generator class
    """

    def __init__(self) -> None:
        """
        Initializes the stochastic generator class
        """
        self._time = 0
    
    def bind_variable(self, node, varname):
        """
        Binds a variable to the stochastic generator
        """
        if varname not in node['variables']:
            node['variables'].add(
                key=varname,
                value = self.dataset[self._time],
                range = (min(self.dataset), max(self.dataset))
                )
        else:
            node['variables'][varname] = self.dataset[self._time]
        
        self.target = node['variables'][varname] 

    def bind_dataset(self, path, filenames):
        """
        Binds a dataset to the stochastic generator
        """

        for file_name in filenames:
            csvs_files = glob(str(path) +'/' + file_name)

        self.dataset = []
        for filename in csvs_files:
            with open(filename) as f:
                next(f) 
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        _, value = parts
                        self.dataset.append(float(value))
                    elif len(parts) == 1:
                        value = float(parts[0])
                        self.dataset.append(float(value))
        self._maxtime = len(self.dataset)
        
    def update(self):
        """
        Updates the stochastic generator
        """
        self._time += 1
        self.target = self.dataset[self._time % self._maxtime]
