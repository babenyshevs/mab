from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import statsmodels.stats.api as sms
from scipy.stats import norm
from statsmodels.stats.power import TTestIndPower

from src.data.utilites import bootstrap


class SampleSizeGrid:
    """
    A class to calculate and visualize sample size requirements for given variables using Plotly.

    Attributes:
        x_name (str): The name of the x-axis for the plot.
        y_name (str): The name of the y-axis for the plot.
        variables (list): A list of variables to analyze.
        data (Any): The dataset containing the variables.
        power (float): The desired power for the statistical test.
        alpha (float): The significance level for the statistical test.
    """

    def __init__(
        self,
        x_name: str = "minimum detectable effect size",
        y_name: str = "observations needed (precise)",
        variables: list = None,
        data: Any = None,
        power: float = 0.8,
        alpha: float = 0.05,
    ):
        self.x_name = x_name
        self.y_name = y_name
        self.variables = variables
        self.data = data
        self.power = power
        self.alpha = alpha

    def calculate_observation_requirements(self, variable: str) -> pd.DataFrame:
        """
        Calculate observation requirements based on bootstrap analysis for a single variable.

        Args:
            variable (str): The variable of interest.

        Returns:
            pd.DataFrame: A DataFrame containing the observation requirements for the specified variable.
        """
        A = bootstrap(data=self.data, variable=variable, bias=0, repeats=1000, sample=100)
        m = np.mean(A)
        effects = {self.x_name: [], self.y_name: []}

        for effect_size in np.arange(start=0.01, stop=0.15, step=0.01):
            proportional_effect = sms.proportion_effectsize(m + effect_size, m)
            power_analysis = TTestIndPower()
            required_n = power_analysis.solve_power(
                effect_size=proportional_effect, power=self.power, alpha=self.alpha, nobs1=None
            )
            required_n = int(required_n)
            effects[self.x_name].append(effect_size)
            effects[self.y_name].append(required_n)

        df = pd.DataFrame(effects)
        return df

    def plot_observation_requirements(self, return_fig=False) -> None:
        """
        Plot observation requirements for all variables using Plotly.
        """
        fig = go.Figure()

        for variable in self.variables:
            df = self.calculate_observation_requirements(variable)
            fig.add_trace(
                go.Scatter(
                    x=df[self.x_name], y=df[self.y_name], mode="lines+markers", name=variable
                )
            )

        fig.update_layout(
            title="Observations Needed vs. Minimum Detectable Effect Size",
            xaxis_title="Minimum Detectable Effect Size",
            yaxis_title="Observations Needed (Precise)",
            legend_title="Variables",
            # template="plotly_white",
        )
        if return_fig:
            return fig
        else:
            fig.show()

    def plot_distributions(self, return_fig=False) -> None:
        """
        Plot distributions obtained from calculate_observation_requirements for all variables using Plotly.
        Each variable is plotted separately, sharing the y-axis but having their own x-axis.
        """
        # Create a subplot figure with shared y-axis
        fig = sp.make_subplots(
            rows=1, cols=len(self.variables), shared_yaxes=True, subplot_titles=self.variables
        )

        for i, variable in enumerate(self.variables, start=1):
            sample = bootstrap(data=self.data, variable=variable, bias=0, repeats=1000, sample=500)
            mu, std = norm.fit(sample)
            hist_data = go.Histogram(
                x=sample,
                histnorm="probability density",
                name=f"{variable} (std={np.round(std, 4)}, mean={np.round(mu, 2)})",
            )
            fig.add_trace(hist_data, row=1, col=i)
            fig.update_xaxes(title_text="Mean", row=1, col=i)

        fig.update_layout(
            title="Distribution of boostraped metric",
            yaxis_title="Frequency",
            showlegend=True,
            # template="plotly_white",
        )
        if return_fig:
            return fig
        else:
            fig.show()


# Example usage:
# analyzer = SampleSizeGrid(variables=["acceptable", "fabricating_info"], data=labstudio_data)
# analyzer.plot_observation_requirements()
# analyzer.plot_distributions()
