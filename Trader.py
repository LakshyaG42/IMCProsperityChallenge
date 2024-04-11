from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import pandas as pd

class Trader:

    def __init__(self):
        self.traderData = ""
        self.mean_window = 30  # Rolling window for calculating mean and std
        self.signal_threshold = 1.0  # Threshold for generating buy/sell signals
        self.positions = {}  # Store current positions
        self.rolling_mean = pd.Series()
        self.rolling_std = pd.Series()

    def calculate_signals(self, price_data: pd.Series) -> pd.Series:
        signals = pd.Series(index=price_data.index, data=0.0)

        # Calculate rolling mean and std
        self.rolling_mean = price_data.rolling(window=self.mean_window).mean()
        self.rolling_std = price_data.rolling(window=self.mean_window).std()

        # Generate buy/sell signals
        signals[price_data < (self.rolling_mean - self.signal_threshold * self.rolling_std)] = 1.0
        signals[price_data > (self.rolling_mean + self.signal_threshold * self.rolling_std)] = -1.0

        return signals

    def run(self, state):
        # Extract Aquatic Amethyst prices from state
        amethyst_prices = state.order_depths['AMETHYSTS'].mid_prices

        # Generate trading signals
        signals = self.calculate_signals(amethyst_prices)

        # Execute trading actions based on signals
        for timestamp, signal in signals.items():
            if signal == 1.0:  # Buy signal
                if 'AMETHYSTS' not in self.positions:
                    self.positions['AMETHYSTS'] = 100  # Initial position size
            elif signal == -1.0:  # Sell signal
                if 'AMETHYSTS' in self.positions:
                    del self.positions['AMETHYSTS']

        # Prepare output data
        result = {}
        for product, position in self.positions.items():
            if position > 0:
                result[product] = [{"symbol": product, "price": amethyst_prices[-1], "quantity": position}]

        # Update trader data for next iteration
        self.traderData = "SAMPLE"  # Update with actual trader data

        # Return trading actions
        conversions = 1  # Placeholder value, not used in this strategy
        return result, conversions, self.traderData