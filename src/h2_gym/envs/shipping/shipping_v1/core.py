"""
This module contains the shipping environment which performs a bilevel model predictive
control optimisation for the shipping problem.
"""

from __future__ import annotations
from h2_gym.data.shipping.ngdemand import NGDemand
from h2_gym.algs import KalmanFilter, MPC
from pyomo.environ import Param
from meteor_py import GetData
from pathlib import Path
import yaml
from .utils import optimisation_handover, environment_handover, import_fast_data, import_fast_functions, args_dict


class ShippingEnvV1:

    def __init__(self) -> None:
        
        #self._outer_generator = StochasticGenerator()
        #self._inner_generator = StochasticGenerator()
        #self._space_graph = SpaceGraph()
        #self._time_graph = Isochronous(self._space_graph, self._outer_generator)
        self.idx = 0
        self._args = args_dict()
        pass

    def __enter__(self) -> None:
        """
        This function is used to enter the environment.
        """
        return self._args

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        This function is used to exit the environment.

        """
        self._fast_data = import_fast_data(
            self._args['fast']["data_folder"],
            self._args['fast']["planning_model"],
            self._args["vector"],
            self._args['fast']["random_param"],
        )

        self._fast_data.update(
            import_fast_functions(
                self._args['fast']["data_folder"],
                self._fast_data["sets"]
            )
        ) 

        self._filter = KalmanFilter(
            self._args['demand_prediction']['country'],
            self._args['demand_prediction']['frequency'],
            self._args['demand_prediction']['sector']
        )

        self._filter.scale_dataset(
            self._args['demand_prediction']['scale']
        )

        self._filter.fit_train()

        self._weather_data = GetData(self._args['weather_data']['weather_file'])

        pass

    def step(self):
        """
        Extracts data from the model, solves the inner loop and hands over the results to the outer loop
        """

        # Updating the Kalman filter
        self._filter.update()
        demand_forecast = self._filter.predict(12)
        
        # Updating the demand forecast
        n_steps = demand_forecast.index[0].days_in_month
        projection = self._filter.predict(12)['predicted_mean'].values

        # Building the parameter dictionary for the slow model
        slow_args = {}

        # Solving the slow control problem
        self._slow.update(slow_args)
        shipping_schedule_year = self._slow.solve()

        # Iteratively solving the inner loop problem
        for i in range(n_steps):
            
            # Using a 1-week persistance forecast 
            weather_forecast = (
                self._weather_data[self.idx:self.idx + 7] * self._args['fast']['horizon']
            )

            # Grabbing the relevant portion from the shipping schedule
            shipping_schedule = (
                shipping_schedule_year[i:i+n_steps]
            )

            # Building the parameter dictionary for the fast model
            fast_args = {
                'demand_forecast': Param(set = self._fast_data['sets']['grid1'], initialize=[]),
                'weather_forecast': Param(set = self._fast_data['sets']['grid0'], initialize=weather_forecast),
            }

            # Updating the fast model with the new parameters and solving it
            self._fast.update(fast_args)
            res = self._fast.solve()
            
            print(f"\r[Inner-Loop] Shipping schedule for day {i}", end=' '*20)

            ### NEED TO CHECK THAT THE SHIP SHEDULE WAS MET, ELSE THE MISSED TARGET MUST ROLL OVER
            self.idx += 1
            

        

        self._simulate_destination_storage(shipping_schedule )

        pass
