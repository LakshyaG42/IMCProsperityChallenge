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

    def calculate_signals(self, price_data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(index=price_data.index, data=0.0)

        # Calculate rolling mean and std for each product
        self.rolling_mean = price_data.rolling(window=self.mean_window).mean()
        self.rolling_std = price_data.rolling(window=self.mean_window).std()

        # Generate buy/sell signals based on price deviations from mean
        signals[(price_data['AMETHYSTS'] < (self.rolling_mean['AMETHYSTS'] - self.signal_threshold * self.rolling_std['AMETHYSTS'])) &
                (price_data['STARFRUIT'] > (self.rolling_mean['STARFRUIT'] + self.signal_threshold * self.rolling_std['STARFRUIT']))] = 1.0

        signals[(price_data['AMETHYSTS'] > (self.rolling_mean['AMETHYSTS'] + self.signal_threshold * self.rolling_std['AMETHYSTS'])) &
                (price_data['STARFRUIT'] < (self.rolling_mean['STARFRUIT'] - self.signal_threshold * self.rolling_std['STARFRUIT']))] = -1.0

        return signals

    def run(self, state: TradingState):
        # Extract Aquatic Amethyst and Starfruit prices from state
        amethyst_prices = state.order_depths['AMETHYSTS'].mid_prices
        starfruit_prices = state.order_depths['STARFRUIT'].mid_prices
        price_data = pd.DataFrame({'AMETHYSTS': amethyst_prices, 'STARFRUIT': starfruit_prices})

        # Generate trading signals
        signals = self.calculate_signals(price_data)

        # Execute trading actions based on signals
        for timestamp, signal in signals.items():
            if signal == 1.0:  # Buy signal for Aquatic Amethysts, sell signal for Starfruit
                if 'AMETHYSTS' not in self.positions:
                    self.positions['AMETHYSTS'] = 100  # Initial position size
                if 'STARFRUIT' in self.positions:
                    del self.positions['STARFRUIT']
            elif signal == -1.0:  # Sell signal for Aquatic Amethysts, buy signal for Starfruit
                if 'STARFRUIT' not in self.positions:
                    self.positions['STARFRUIT'] = 100  # Initial position size
                if 'AMETHYSTS' in self.positions:
                    del self.positions['AMETHYSTS']

        # Prepare output data
        result = {}
        for product, position in self.positions.items():
            if position > 0:
                result[product] = [Order(product, price_data[product].iloc[-1], position)]

        # Update trader data for next iteration
        self.traderData = "SAMPLE"  # Update with actual trader data

        # Return trading actions
        conversions = 1  # Placeholder value, not used in this strategy
        return result, conversions, self.traderData