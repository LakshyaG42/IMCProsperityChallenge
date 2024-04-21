import pandas as pd
import numpy as np
import jsonpickle
from typing import Dict, List, Tuple
import math
import statistics
from datamodel import OrderDepth, Observation, TradingState, Order
from collections import deque

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.signal_window = 3
        self.signal_buffer = deque(maxlen=self.signal_window)

    def calculate_buy_sell_prices(self, state: TradingState, sunlightList, humidityList) -> Tuple[float, float]:
        order_depth = state.order_depths['ORCHIDS']
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        current_price = (best_ask+best_bid)/2.0

        # Calculate moving averages for sunlight and humidity
        window_size = 7  # You can adjust the window size as needed
        
        if(len(sunlightList) > window_size and len(humidityList) > window_size):
            sunlight_ma = sum(sunlightList[-window_size:]) / window_size
            humidity_ma = sum(humidityList[-window_size:]) / window_size
        else:
            sunlight_ma = sum(sunlightList) / len(sunlightList)
            humidity_ma = sum(humidityList) / len(humidityList)

        # Calculate buy and sell prices based on moving averages
        buy_price = current_price * (1 + (sunlight_ma * 0.1) + (humidity_ma * 0.05))
        sell_price = current_price * (1 - (sunlight_ma * 0.1) - (humidity_ma * 0.05))

        signal = self.generate_signal(sunlight_ma, humidity_ma)
        self.signal_buffer.append(signal)

        if(signal != 1):
            buy_price = None
        if(signal != -1):
            sell_price = None
        

        return buy_price, sell_price

    def generate_signal(self, sunlight_ma: float, humidity_ma: float) -> int:
        # Generate buy (1), sell (-1), or hold (0) signal based on moving averages
        if len(self.signal_buffer) == self.signal_window:
            prev_sunlight_ma, prev_humidity_ma = self.signal_buffer[-1]
            if sunlight_ma > humidity_ma and prev_sunlight_ma <= prev_humidity_ma:
                return 1  # Buy signal
            elif humidity_ma > sunlight_ma and prev_humidity_ma <= prev_sunlight_ma:
                return -1  # Sell signal
        return 0  # Hold signal


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
    
    def run(self, state: TradingState):
                result = {}
                if(state.traderData):
                    decoded_data = jsonpickle.decode(state.traderData)
                    sunshineList = decoded_data['sunshine']
                    humidityList = decoded_data['humidity']
                else:
                    sunshineList = []
                    humidityList = []
                product = 'ORCHIDS'
                order_depth = state.order_depths[product]
                sunshineList.append(state.observations.conversionObservations['ORCHIDS'].sunlight)
                humidityList.append(state.observations.conversionObservations['ORCHIDS'].humidity)

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                current_position = self.position['ORCHIDS']

                # Calculate the predicted price using the model coefficients
                buy_price, sell_price = self.calculate_buy_sell_prices(state, sunshineList, humidityList)
                if(buy_price or sell_price):
                    if buy_price:
                        if buy_price > best_ask:
                            # Buy if predicted price is significantly higher than best ask price
                            allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_ask, best_ask_amount)
                            if allowable_quantity > 0:
                                print(str(product), "BUY", str(allowable_quantity) + "x", best_ask)
                                result[product].append(Order(product, best_bid, allowable_quantity))
                    if sell_price:
                        if sell_price < best_bid and current_position > 0:
                            # Sell if predicted price is significantly lower than best bid price and we have a position to sell
                            allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_bid, -best_bid_amount)
                            if allowable_quantity > 0:
                                print(str(product), "SELL", str(-allowable_quantity) + "x", best_bid)
                                result[product].append(Order(product, best_bid, -allowable_quantity))
                print(f'!!! PreviousSunshineHistory { sunshineList } !!! PreviousHumidityHistory { humidityList }' )
                data = jsonpickle.encode({'sunshine': sunshineList, 'humidity': humidityList})
                return result, 0, data