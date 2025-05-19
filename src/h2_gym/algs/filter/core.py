"""
This module enables demand projection for the nodes.
"""

from __future__ import annotations
from typing import Optional
from pathlib import Path
from pandas import read_csv, DataFrame, to_datetime, DateOffset, concat
from statsmodels.tsa.statespace.structural import UnobservedComponents
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from matplotlib import pyplot as plt
from numpy import random, empty, ndarray
from .utils import muted_color, muted_palette
from cycler import cycler
import warnings


class KalmanFilter:
    """
    This class implements a Kalman filter for demand projection.
    """

    def __init__(
        self,
        country: str,
        period: Optional[str],
        demand_type: Optional[str],
        path: Optional[str] = None,
    ) -> None:
        """
        Initializes the Kalman filter class.
        """
        self._data = self.get_data(path, country, period, demand_type)
        self._inputs = None
        self._outputs = None
        self._props = None
        self._synth = False

        return None

    def get_data(
        self,
        path: Optional[str],
        country: Optional[str],
        period: Optional[str] = None,
        demand_type: Optional[str] = None,
    ) -> None:

        if path is None:
            path = (
                Path(__file__).parent.parent.parent
                / f"data/shipping/ngdemand/demand/src/data/analyzed/{period}_demand_clean.csv"
            )

        data = read_csv(path)
        loc_mask = data["country"] == country
        if loc_mask.sum() == 0:
            print(
                f"[NOTE] Country {country} not found in the data, defaulting to EU for demand shape."
            )
            country = "EU"

        mask = (data["type"] == demand_type) & loc_mask
        if mask.sum() == 0:

            print(
                f"""[NOTE] Demand type {demand_type} not found in the data, defaulting to industry for demand shape.
       demand must be one of {data.loc[loc_mask]['type'].unique()}"""
            )

        data = data.loc[mask]

        dates = to_datetime(
            [
                "01/" + str(month) + "/" + str(year)
                for month, year in zip(data["month"].values, data["year"].values)
            ],
            dayfirst=True,
        )

        data = data.set_index(dates)
        data = data.drop(columns=["month", "year", "country", "type"])

        first_date = data.index.min()
        one_year_later = first_date + DateOffset(years=1)

        train_mask = data.index < one_year_later
        test_mask = data.index >= one_year_later

        train_data = data[train_mask]
        test_data = data[test_mask]

        self._train_data = train_data["demand"]
        self._test_data = test_data["demand"]
        self._seen_data = 0
        return data["demand"]

    def scale_dataset(self, demand) -> None:
        """
        Scales the dataset to an annual demand that is given.
        """
        annual_demand = sum(self._train_data)
        scale_factor = demand / annual_demand
        self._train_data = self._train_data * scale_factor
        self._test_data = self._test_data * scale_factor
        self._data = self._data * scale_factor

    def fit_train(self) -> None:
        """
        Fits the Kalman filter to the training data.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Fit the model
            self._model = UnobservedComponents(
                self._train_data,
                level="local level",
                seasonal=12,
            )

            self._results = self._model.fit(disp=False)

            if not self._synth:
                self._init_results = self._results

            # Get the fitted and smoothed values from results directly
            self._fitted_values = self._results.fittedvalues
            self._smoothed_values = self._results.smoothed_state

            # Get the filtered state and covariance
            self.last_state_mean = self._results.filtered_state[:, -1]
            self.last_state_cov = self._results.filtered_state_cov[:, :, -1]

            # Access filter results if needed
            self._filter_results = self._results.filter_results

    def gen_multi_synth(self, n_sim: int, dur: int) -> ndarray:
        """
        Generates multiple synthetic data points using the Kalman filter.
        """

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = UnobservedComponents(
                self._data,
                level="local level",
                seasonal=12,
            )

            results = model.fit(disp=False)

            sims = empty(shape=(n_sim, dur))

            for i in range(n_sim):
                sampled_state = random.multivariate_normal(
                    results.filtered_state[:, -1], results.filtered_state_cov[:, :, -1]
                )
                sim = results.simulate(nsimulations=dur, initial_state=sampled_state)
                sims[i] = sim

        return sims

    def plot_synth(self, sims):
        """
        Plots the synthetic data points generated by the Kalman filter.
        """
        plt.style.use("bmh")
        plt.rcParams["figure.dpi"] = 500
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "cm"
        plt.rcParams["axes.prop_cycle"] = cycler(color=muted_palette)
        plt.figure(figsize=(15, 4.5))
        plt.plot(
            self._data.index, self._data, label="Train Data", color=muted_color("blue")
        )

        indx = [
            self._data.index[-1] + DateOffset(months=i) for i in range(len(sims[0]) + 1)
        ]

        for i in range(sims.shape[0]):
            plt.plot(indx, [self._data.iloc[-1]] + list(sims[i][:]), alpha=0.5)

        plt.title("Synthetic Data Generation using Kalman Filter")
        plt.xlabel("Date")
        plt.ylim(bottom=0)
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        return plt

    def predict(self, n_pred: int) -> DataFrame:
        """
        Predicts the demand for the next n_pred periods.
        """
        # Get the forecast
        forecast = self._results.get_forecast(steps=n_pred)

        # Get the predicted values
        pred_values = forecast.predicted_mean

        # Get the confidence intervals
        conf_int = forecast.conf_int(alpha=0.05)

        # Create a DataFrame with the predicted values and confidence intervals
        pred_df = DataFrame(
            {
                "predicted_mean": pred_values,
                "lower_ci": conf_int.iloc[:, 0],
                "upper_ci": conf_int.iloc[:, 1],
            },
            index=pred_values.index,
        )

        return pred_df

    def update(self) -> float:
        """
        Updates the Kalman filter with the next data point.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._train_data = concat([self._train_data, self._test_data.iloc[[0]]])
            self._test_data = self._test_data[1:]
            self.fit_train()
            self.check_test()
            self._seen_data += 1
            self._synth = True

        return self._train_data.iloc[-1]

    def check_test(self) -> None:
        """
        Checks if the test data is less than 12 months.
        """

        if len(self._test_data) < 12:
            print(f"[NOTE] Less than 12 month data left. Generating synthetic data")
            n_sim = 1
            sims = empty(shape=(n_sim, 36))

            for i in range(n_sim):
                sampled_state = random.multivariate_normal(
                    self.last_state_mean, 0.5 * self.last_state_cov
                )
                sim = self._init_results.simulate(
                    nsimulations=36, initial_state=sampled_state
                )
                sims[i] = sim

            # Take the mean of the simulations
            sim = sims.mean(axis=0)

            indx = [
                self._train_data.index[-1] + DateOffset(months=1) + DateOffset(months=i)
                for i in range(36)
            ]
            self._test_data = DataFrame(sim, index=indx, columns=["demand"])["demand"]

    def plot(self):
        """
        Plots the projections from the Kalman filter for the next year
        """
        forecast = self.predict(12)
        forecast_mean = forecast["predicted_mean"]
        forecast_ci = DataFrame(
            {"lower_ci": forecast["lower_ci"], "upper_ci": forecast["upper_ci"]}
        )

        plt.style.use("bmh")
        plt.rcParams["figure.dpi"] = 500
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "cm"
        plt.figure(figsize=(15, 4.5))
        plt.plot(
            self._train_data.index,
            self._train_data,
            label="Train Data",
            color=muted_color("blue"),
        )
        plt.plot(
            self._test_data.index[:12],
            self._test_data[:12],
            label="Test Data",
            color=muted_color("green"),
        )

        if not self._train_data.empty:
            plt.plot(
                [self._train_data.index[-1], self._test_data.index[0]],
                [self._train_data.iloc[-1], self._test_data.iloc[0]],
                color=muted_color("green"),
                linestyle="--",
            )

        plt.plot(
            forecast_mean.index,
            forecast_mean,
            label="Forecast",
            color=muted_color("red"),
        )
        if not self._train_data.empty:
            plt.plot(
                [self._train_data.index[-1], forecast_mean.index[0]],
                [self._train_data.iloc[-1], forecast_mean.iloc[0]],
                color=muted_color("red"),
                linestyle="--",
            )

        plt.fill_between(
            [self._train_data.index[-1], *forecast_mean.index],
            [self._train_data.iloc[-1], *forecast_ci["lower_ci"]],
            [self._train_data.iloc[-1], *forecast_ci["upper_ci"]],
            color=muted_color("orange"),
            alpha=0.3,
            label="95% CI",
        )

        #
        plt.title("Kalman Filter Forecast (Local Linear Trend + Seasonality)")
        plt.xlabel("Date")
        plt.ylim(bottom=0)
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        return plt

    @staticmethod
    def seasonal_forecast(train, n_pred, season_length, alpha, beta, gamma):
        model = ExponentialSmoothing(
            train, trend="add", seasonal="add", seasonal_periods=season_length
        )
        model_fit = model.fit(
            smoothing_level=alpha,
            smoothing_trend=beta,
            smoothing_seasonal=gamma,
            optimized=False,
        )
        forecast = model_fit.forecast(n_pred)
        return forecast
