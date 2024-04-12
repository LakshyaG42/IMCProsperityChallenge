from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import statistics
import math
import numpy as np
import pandas as pd
import jsonpickle

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20}
        self.starfruit_cache = []
        self.amethyst_cache = []
        self.cache_size = {'STARFRUIT': 5, 'AMETHYSTS': 6}
        self.mean_reversion_window = 5

    def update_cache(self, state: TradingState):
        order_depth_starfruit = state.order_depths.get('STARFRUIT')
        order_depth_amethyst = state.order_depths.get('AMETHYSTS')

        if order_depth_starfruit:
            if len(self.starfruit_cache) >= self.cache_size['STARFRUIT']:
                self.starfruit_cache.pop(0)  # Remove the oldest entry if cache size is reached
            self.starfruit_cache.append(order_depth_starfruit)

        if order_depth_amethyst:
            if len(self.amethyst_cache) >= self.cache_size['AMETHYSTS']:
                self.amethyst_cache.pop(0)  # Remove the oldest entry if cache size is reached
            self.amethyst_cache.append(order_depth_amethyst)

        print("Amethyst cache: ", [max(order_depth.buy_orders.keys()) for order_depth in self.amethyst_cache if len(order_depth.buy_orders.keys()) != 0])

    def mean_reversion(self) -> float:
        if len(self.amethyst_cache) < self.mean_reversion_window:
            return 0.0  # Not enough data for mean reversion calculation

        amethyst_prices = []
        for order_depth in self.amethyst_cache[-self.mean_reversion_window:]:
            if order_depth and order_depth.buy_orders:
                best_bid_price = max(order_depth.buy_orders.keys())
                amethyst_prices.append(best_bid_price)

        if not amethyst_prices:
            return 0.0  # No valid prices found in the cache
        print("Amethyst prices: ", amethyst_prices)
        rolling_mean = pd.Series(amethyst_prices).mean()
        latest_price = amethyst_prices[-1]
        mean_reversion_signal = latest_price - rolling_mean
        return mean_reversion_signal

    def calculate_allowable_quantity(self, product: str, order_type: str, quantity: int) -> int:
        current_position = self.position[product]
        position_limit = self.position_limit[product]
        allowable_quantity = 0

        if order_type == 'BUY':
            allowable_quantity = min(abs(position_limit) - abs(current_position), quantity)
            if current_position + allowable_quantity > position_limit:
                allowable_quantity = position_limit - current_position
        elif order_type == 'SELL':
            allowable_quantity = min(abs(position_limit) + abs(current_position), quantity)
            if current_position - allowable_quantity < -position_limit:
                allowable_quantity = current_position + position_limit

        return allowable_quantity

    def update_position(self, product: str, quantity: int):
        self.position[product] += quantity


    # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
    def run(self, state: TradingState):
        self.update_cache(state)

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
            if(product in state.position.keys()):
                print("State Position: " + str(state.position[product]))

            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print("Current Position:" + str(self.position['AMETHYSTS']))
            
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            if product == "AMETHYSTS":
                mean_reversion_signal = self.mean_reversion()
                print(f"Signal: {mean_reversion_signal}")
                if mean_reversion_signal > 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    allowable_quantity = self.calculate_allowable_quantity(product, 'SELL', -best_bid_amount)
                    quantity = min(allowable_quantity, -best_bid_amount)
                    print("SELL", str(-best_bid_amount) + "x", best_bid)
                    if(best_bid > 10000):
                        orders.append(Order(product, best_bid, quantity))
                        self.update_position(product, quantity)
                elif mean_reversion_signal < 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    allowable_quantity = self.calculate_allowable_quantity(product, 'BUY', -best_ask_amount)
                    quantity = min(allowable_quantity, -best_ask_amount)
                    print("BUY", str(best_ask_amount) + "x", best_ask)
                    if(best_ask < 10000):
                        orders.append(Order(product, best_ask, quantity))
                        self.update_position(product, -quantity)
            result[product] = orders

        traderData = jsonpickle.encode(result)
        
        conversions = 1
        return result, conversions, traderData