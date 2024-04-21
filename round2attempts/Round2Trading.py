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


        return buy_price, sell_price

    def update_position(self, product, order_type: str, quantity: int):
        if order_type == 'BUY':
            self.position[product] += quantity
        elif order_type == 'SELL':
            self.position[product] -= quantity
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
        for product in state.order_depths:
            print(f"Product: {product}")
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if(product == 'STARFRUIT' or product == 'AMETHYSTS'):
                if product == 'STARFRUIT':
                    acceptable_price = 4950
                else:
                    acceptable_price = 10000
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "BUY", best_ask_amount)
                        print(str(product), "BUY", str(quantity) + "x", best_ask)
                        orders.append(Order(product, best_ask, quantity))
                        self.update_position(product, "BUY", quantity)
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "SELL", best_bid_amount)
                        print(str(product), "SELL", str(-quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -quantity))
                        self.update_position(product, "SELL", quantity)

            if(product == 'ORCHIDS'):
                sunshineList.append(state.observations.conversionObservations['ORCHIDS'].sunlight)
                humidityList.append(state.observations.conversionObservations['ORCHIDS'].humidity)

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                current_position = self.position['ORCHIDS']

                # Calculate the predicted price using the model coefficients
                buy_price, sell_price = self.calculate_buy_sell_prices(state, sunshineList, humidityList)
                print(f'!!!!! ORCHID STUFF: buyThreshold: {buy_price} sellThreshold: {sell_price} ask: {best_ask} bid: {best_bid} !!!!!')
                if buy_price > best_ask:
                    # Buy if predicted price is significantly higher than best ask price
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_ask, best_ask_amount)
                    if allowable_quantity > 0:
                        print(str(product), "BUY", str(allowable_quantity) + "x", best_ask)
                        orders.append(Order(product, best_bid, allowable_quantity))
                        self.update_position(product, "BUY", allowable_quantity)
                if sell_price < best_bid and current_position > 0:
                    # Sell if predicted price is significantly lower than best bid price and we have a position to sell
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_bid, -best_bid_amount)
                    if allowable_quantity > 0:
                        print(str(product), "SELL", str(-allowable_quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -allowable_quantity))
                        self.update_position(product, "SELL", allowable_quantity)
                data = jsonpickle.encode({'sunshine': sunshineList, 'humidity': humidityList})
            result[product] = orders
            
        data = jsonpickle.encode({'sunshine': sunshineList, 'humidity': humidityList})
        return result, 0, data