import pandas as pd
import numpy as np
import jsonpickle
from typing import Dict, List, Tuple
import math
import statistics
from datamodel import OrderDepth, Observation, TradingState, Order

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.signal_window = 10
        self.sunshineList = []
        self.humidityList = []
        self.prev_sunshine = None 
        self.prev_humidity = None 

    def generate_signal(self, state: TradingState, sunlightList, humidityList) -> Tuple[float, float]:
        signal = 0  # Default no signal
        reset = False

        # Ensure at least signal_window + 1 data points are available for normalization
        if (len(sunlightList) > self.signal_window and len(humidityList) > self.signal_window):
            # Extract the last two data points for normalization
            last_sunshine = sunlightList[-1]
            last_humidity = humidityList[-1]

            
            min_sunlight = 1000
            max_sunlight = 4600
            min_humidity = 30
            max_humidity = 100

            
            sunshine_mean = statistics.mean(sunlightList)
            sunshine_std_dev = statistics.stdev(sunlightList)
            humidity_mean = statistics.mean(humidityList)
            humidity_std_dev = statistics.stdev(humidityList)
    
            
            if sunshine_std_dev != 0 and humidity_std_dev != 0:
                last_sunshine_norm = (last_sunshine - min_sunlight) / (max_sunlight - min_sunlight)
                last_humidity_norm = (last_humidity - min_humidity) / (max_humidity - min_humidity)
                prev_sunshine_norm = self.prev_sunshine
                prev_humidity_norm = self.prev_humidity
                spread = 0
                mean_spread = 0
                std_dev_spread = 0
                if (self.prev_humidity != None and self.prev_sunshine != None):
                    # Generate signals based on normalized data
                    if last_sunshine_norm > last_humidity_norm and prev_sunshine_norm <= prev_humidity_norm:
                        signal = 1  # Buy signal
                    elif last_humidity_norm > last_sunshine_norm and prev_humidity_norm <= prev_sunshine_norm:
                        signal = -1  # Sell signal

                    # Calculate spread based on normalized data
                    spread = abs(last_sunshine_norm - last_humidity_norm)
                    mean_spread = statistics.mean([abs(s - h) for s, h in zip(sunlightList, humidityList)])
                    std_dev_spread = statistics.stdev([abs(s - h) for s, h in zip(sunlightList, humidityList)])

                    # Check if spread exceeds mean + std deviation
                    if spread > mean_spread + std_dev_spread:
                        reset = True

                print(f'!!!! last_sunshine: {last_sunshine_norm} last_humidity: {last_humidity_norm} prev_sun: {prev_sunshine_norm} prev_hum: {prev_humidity_norm} Signal: {signal} Spread {spread} Mean Spread {mean_spread} Std Dev Spread {std_dev_spread} !!!!')
                self.prev_sunshine = last_sunshine_norm
                self.prev_humidity = last_humidity_norm
        return signal, reset

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
        for product in state.order_depths:
            print(f"Product: {product}")
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if(product == 'STARFRUIT' or product == 'AMETHYSTS'):
                acceptable_price = 10000
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "BUY", best_ask_amount)
                        print(str(product), "BUY", str(best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, best_ask_amount))
                        self.update_position(product, "BUY", best_ask_amount)
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "SELL", best_bid_amount)
                        print(str(product), "SELL", str(-best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        self.update_position(product, "SELL", best_bid_amount)

            if(product == 'ORCHIDS'):
                self.sunshineList.append(state.observations.conversionObservations['ORCHIDS'].sunlight)
                self.humidityList.append(state.observations.conversionObservations['ORCHIDS'].humidity)

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                current_position = self.position['ORCHIDS']
                signal, reset = self.generate_signal(state, self.sunshineList, self.humidityList)
                
                # Calculate the predicted price using the model coefficients
                if signal == 1:
                    # Buy if predicted price is significantly higher than best ask price
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_ask, best_ask_amount)
                    if allowable_quantity > 0:
                        print(str(product), "BUY", str(allowable_quantity) + "x", best_ask)
                        orders.append(Order(product, best_bid, allowable_quantity))
                        self.update_position(product, "BUY", best_ask_amount)
                if signal == -1 and current_position > 0:
                    # Sell if predicted price is significantly lower than best bid price and we have a position to sell
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_bid, -best_bid_amount)
                    if allowable_quantity > 0:
                        print(str(product), "SELL", str(-allowable_quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        self.update_position(product, "SELL", -best_bid_amount)
                if reset:
                    if(self.position['ORCHIDS'] > 0):
                        print(str(product), "SELL", str(-self.position['ORCHIDS']) + "x", best_bid)
                        orders.append(Order(product, best_bid, -self.position['ORCHIDS']))
                        self.update_position(product, "SELL", self.position['ORCHIDS'])
                    if(self.position['ORCHIDS'] < 0):
                        print(str(product), "BUY", str(-self.position['ORCHIDS']) + "x", best_ask)
                        orders.append(Order(product, best_ask, -self.position['ORCHIDS']))
                        self.update_position(product, "BUY", -self.position['ORCHIDS'])
                #data = jsonpickle.encode({'sunshine': self.sunshineList, 'humidity': self.humidityList})
            result[product] = orders
            
        data = jsonpickle.encode("hello")
        return result, 0, data