import pandas as pd
import numpy as np
import jsonpickle
from typing import Dict, List
import math
import statistics
from datamodel import OrderDepth, Observation, TradingState, Order

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.model_coefficients = {'TRANSPORT_FEES': 1.2, 'EXPORT_TARIFF': -0.5, 'IMPORT_TARIFF': 0.8,
                                   'SUNLIGHT': -0.3, 'HUMIDITY': 0.6}  
        self.threshold = 0.5  

    def calculate_allowable_quantity(self, product: str, order_type: str, quantity: int):
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
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        for product in state.order_depths:
            print(f'Product: {product}')
            if(product == 'STARFRUIT' or product == 'AMETHYSTS'):
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                acceptable_price = 10000 
                print("Acceptable price : " + str(acceptable_price))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "BUY", best_ask_amount)
                        print(str(product), "BUY", str(quantity) + "x", best_ask)
                        orders.append(Order(product, best_ask, quantity))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        quantity = self.calculate_allowable_quantity(product, "SELL", best_bid_amount)
                        print(str(product), "SELL", str(-quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -quantity))
                
                result[product].extend(orders)

            if(product == 'ORCHIDS'):
                orchid_observation = state.observations.conversionObservations['ORCHIDS']
                order_depth = state.order_depths['ORCHIDS']

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                current_position = self.position['ORCHIDS']

                # Calculate the predicted price using the model coefficients
                predicted_price = self.model_coefficients['TRANSPORT_FEES'] * orchid_observation.transportFees + \
                                self.model_coefficients['EXPORT_TARIFF'] * orchid_observation.exportTariff + \
                                self.model_coefficients['IMPORT_TARIFF'] * orchid_observation.importTariff + \
                                self.model_coefficients['SUNLIGHT'] * orchid_observation.sunlight+ \
                                self.model_coefficients['HUMIDITY'] * orchid_observation.humidity
                print(f'!!!!! Predicted price: {predicted_price} !!!!! BEST ASK PRICE: {best_ask} !!!!! BEST BID PRICE: {best_bid} !!!!!')
                # Calculate if price is likely to go up or down
                if predicted_price > best_ask + self.threshold:
                    # Buy if predicted price is significantly higher than best ask price
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_ask, best_ask_amount)
                    if allowable_quantity > 0:
                        print(str(product), "BUY", str(allowable_quantity) + "x", best_ask)
                        result[product].append(Order(product, best_bid, quantity))
                elif predicted_price < best_bid - self.threshold and current_position > 0:
                    # Sell if predicted price is significantly lower than best bid price and we have a position to sell
                    allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_bid, -best_bid_amount)
                    if allowable_quantity > 0:
                        print(str(product), "SELL", str(-allowable_quantity) + "x", best_bid)
                        result[product].append(Order(product, best_bid, -quantity))

    
        return result, 0, "success"