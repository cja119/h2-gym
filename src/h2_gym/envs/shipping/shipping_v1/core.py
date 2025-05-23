"""
This module contains the shipping environment which performs a bilevel model predictive
control optimisation for the shipping problem.
"""

from __future__ import annotations
from h2_gym.data.shipping.ngdemand import NGDemand
from h2_gym.algs import KalmanFilter
from h2_gym.algs.mpc import FastController
from pyomo.environ import Param, value
from meteor_py import GetData
from random import randint
from pathlib import Path
from numpy.random import normal
from numpy import mean
import yaml
from .utils import (
    import_fast_data,
    import_fast_functions,
    args_dict,
    temporal_align,
)


class ShippingEnvV1:

    def __init__(self) -> None:

        # self._outer_generator = StochasticGenerator()
        # self._inner_generator = StochasticGenerator()
        # self._space_graph = SpaceGraph()
        # self._time_graph = Isochronous(self._space_graph, self._outer_generator)
        self.idx = 0
        self._args = args_dict()
        self._fast = FastController()
        self._slow_data = {
            "params": {
                "storage_capacity": 10,
                "mean_ship_transit_time": 35,
                "std_ship_transit_time": 2,
            }
        }
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
            self._args["fast"]["data_folder"],
            self._args["fast"]["planning_model"],
            self._args["vector"],
            self._args["fast"]["random_param"],
        )

        self._fast_data.update(
            import_fast_functions(
                self._args["fast"]["data_folder"], self._fast_data["sets"]
            )
        )

        self._filter = KalmanFilter(
            self._args["demand_prediction"]["country"],
            self._args["demand_prediction"]["frequency"],
            self._args["demand_prediction"]["sector"],
        )

        self._filter.scale_dataset(self._args["demand_prediction"]["scale"])

        self._filter.fit_train()

        self._weather_data = GetData(
            [self._args["weather_data"]["weather_file"]]
        ).data()

        self._filter, self._weather_data = temporal_align(
            self._weather_data, self._filter, randomise=True
        )

        self._fast.build(self._fast_data)

        latent_states = {
            "current_ships": 1,
            "hydrogen_storage": 0.5
            * self._fast_data["params"]["hydrogen_storage_capacity"],
            "vector_storage": 0.5
            * self._fast_data["params"]["vector_storage_capacity"],
            "energy_conversion": (
                0.5
                * self._fast_data["params"]["conversion_trains_number"]
                * self._fast_data["params"]["variable_energy_penalty_conversion"]
                * self._fast_data["params"]["single_train_limit_conversion"]
            ),
            "cumulative_charge": 0,
            "ordered_ship": 0,
            "sent_ship": 0,
        }

        destination_storage = 0.5 * self._slow_data["params"]["storage_capacity"]
        ship_destination = []
        ship_origin = []
        expected_arrivals = []
        expected_destinations = []

        self._state = (
            latent_states,
            destination_storage,
            ship_destination,
            ship_origin,
            expected_arrivals,
            expected_destinations
        )

        pass

    def render(self, mode="human"):
        return self._fast.render()

    def reset(self) -> None:
        """
        This function is used to reset the environment.
        """
        with self as slf:
            pass
        pass

    def step(self, action, plot = False):
        """
        Extracts data from the model, solves the inner loop and hands over the results to the outer loop
        """

        observation = {}

        (latent_states, destination_storage, ship_destination, ship_origin, 
        expected_arrivals, expected_destinations) = (
            self._state
        )

        # Updating the Kalman filter
        new_demand = self._filter.update()
        demand_forecast = self._filter.predict(12)

        # Updating the demand forecast
        n_steps = demand_forecast.index[0].days_in_month
        projection = demand_forecast["predicted_mean"].values
        observation["demand_forecast"] = projection
        
        total_sent = 0

        #
        results = None

        # Iteratively solving the inner loop problem
        for i in range(n_steps +61):

            # Using a 1-week persistance forecast
            weather_forecast = (
                self._weather_data[self.idx : self.idx + 168]
                + (len(self._fast_data["sets"]["grid0"]) - 168)
                * [mean(self._weather_data)]
            )

            # Grabbing the relevant portion from the shipping schedule
            shipping_schedule = {
                key - self.idx: value
                for key, value in action.items()
                if key < len(self._fast_data["sets"]["grid0"]) + self.idx and key - self.idx > 0
            }
        
            # Simulating the randomness of the shipping schedule
            if 0 in ship_origin:
                n_arrived_ships = ship_origin.count(0)
                ship_origin.remove(0)
                origin_arrive = n_arrived_ships 
                expected_arrivals = expected_arrivals[n_arrived_ships:]
            else:
                origin_arrive = 0


            expected_arrivals_indexed = {i:0 for i in self._fast_data["sets"]["grid1"]}
            for arrival in  expected_arrivals:
                expected_arrivals_indexed[int(arrival)*24] += 1

            fast_args = {
                "ship_schedule": {
                    "name": "ship_schedule",
                    "loc": "exogenous",
                    "param": {
                        "set": self._fast_data["sets"]["grid1"],
                        "initialize": shipping_schedule,
                    },
                },
                "energy_wind": {
                    "name": "energy_wind",
                    "loc": "exogenous",
                    "param": {
                        "set": self._fast_data["sets"]["grid0"],
                        "initialize": weather_forecast,
                    },
                },
                "ship_arrived": {
                    "name": "ship_arrived",
                    "loc": "exogenous",
                    "param": {
                        "set": None,
                        "initialize": origin_arrive,
                    },
                },
                "expected_ships": {
                    "name": "expected_ships",
                    "loc": "exogenous",
                    "param": {
                        "set": self._fast_data["sets"]["grid1"],
                        "initialize": expected_arrivals_indexed,
                    },
                },
            }
            # Updating the fast model with the new parameters and solving it
            self._fast.update(fast_args, results)
            results, latent_states = self._fast.solve(not plot)
            self._fast.visualise_output(24)
            total_sent += latent_states["sent_ship"]
            print(
                f"\r[Inner-Loop] Shipping schedule for day {i}. {int(total_sent)} ships sent",
                end=" " * 20,
            )

            # Randomly simulating the arrival of the ships
            if latent_states["ordered_ship"] >= 0:
                ship_origin.extend(
                    [
                        int(
                            normal(
                                value(
                                    self._fast_data["params"]["mean_ship_arrival_time"]
                                ),
                                value(
                                    self._fast_data["params"]["std_ship_arrival_time"]
                                ),
                            )
                        )
                        for _ in range(int(latent_states["ordered_ship"]))
                    ]
                )
                expected_arrivals.extend([self._fast_data["params"]["mean_ship_arrival_time"]]*int(latent_states["ordered_ship"]))
                
            if latent_states["sent_ship"] >= 0:
                ship_destination.extend(
                    [
                        int(
                            normal(
                                value(
                                    self._slow_data["params"]["mean_ship_transit_time"]
                                ),
                                value(
                                    self._slow_data["params"]["std_ship_transit_time"]
                                ),
                            )
                        )
                        for _ in range(int(latent_states["sent_ship"]))
                    ]
                )
                expected_destinations.extend([self._slow_data["params"]["mean_ship_transit_time"]]*int(latent_states["sent_ship"]))

            # Simulating the destination storage
            if 0 in ship_destination:
                n_arrived_ships = ship_destination.count(0)
                ship_destination.remove(0)
                destination_storage -= new_demand
                destination_storage += n_arrived_ships * value(
                    self._fast_data["params"]["ship_capacity"]
                )
                

            # Updating the state of the environment
            ship_origin = [val - 1 for val in ship_origin]
            expected_arrivals = [val - 1 for val in expected_arrivals if val >= 1]
            ship_destination = [val - 1 for val in ship_destination]
            expected_destinations = [val - 1 for val in expected_destinations if val >= 0]
            self.idx += 24
            
            self._state = (
                latent_states,
                destination_storage,
                ship_destination,
                ship_origin,
            )
            observation["destination_storage"] = destination_storage
            observation["ship_destination"] = ship_destination

            if plot:
                yield self._fast.render()
            else:
                yield None

        return observation, 0, False, {}
