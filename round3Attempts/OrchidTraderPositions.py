import pandas as pd
import jsonpickle
from typing import List, Tuple
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.signal_window = 5
        self.humidityList = []
        self.prev_humidity = None 

    def update_position(self, product, order_type: str, quantity: int):
        if order_type == 'BUY':
            self.position[product] += quantity
        elif order_type == 'SELL':
            self.position[product] -= quantity

    def calculate_allowable_quantity(self, product: str, order_type: str, quantity: int) -> int:
        current_position = self.position[product]
        position_limit = self.position_limit[product]
        allowable_quantity = quantity
        
        if order_type == "BUY":
            max_buy_quantity = position_limit - current_position
            allowable_quantity = min(quantity, max_buy_quantity) if max_buy_quantity >= 0 else 0
            # if current_position + quantity <= position_limit:
            #     allowable_quantity = quantity
            # else:
            #     allowable_quantity = min(position_limit - current_position, quantity)
        if order_type == "SELL":
            max_sell_quantity = current_position + position_limit if current_position < 0 else position_limit - current_position
            allowable_quantity = min(quantity, max_sell_quantity) if max_sell_quantity >= 0 else 0
            # if current_position - quantity >= -position_limit:
            #     allowable_quantity = quantity
            # else:
            #     if current_position < 0:
            #         allowable_quantity = current_position + position_limit
            #     else:
            #         allowable_quantity = min((-position_limit) - current_position, quantity)
        return allowable_quantity
    
    def generate_signal(self, state: TradingState, humidityList) -> Tuple[float, float]:
        signal = 0  # Default no signal

        # Ensure at least signal_window + 1 data points are available for analysis
        if len(humidityList) > self.signal_window:
            # Extract the last data points for analysis
            last_humidity = humidityList[-1]
            prev_humidity = humidityList[-2]

            # Check if humidity is low and starting to go back up
            if last_humidity < prev_humidity:
                # Check if humidity has been going up for the past 5 intervals
                if all(humidityList[-i] < humidityList[-i-1] for i in range(1, self.signal_window+1)):
                    signal = 1  # Buy signal

            # Check if humidity is high and starting to go back down
            elif last_humidity > prev_humidity:
                # Check if humidity has been going down for the past 5 intervals
                if all(humidityList[-i] > humidityList[-i-1] for i in range(1, self.signal_window+1)):
                    signal = -1  # Sell signal
        
        return signal

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            print(f"Product: {product}")
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if product in ('STARFRUIT', 'AMETHYSTS'):
                acceptable_price = 10000
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        allowable_quantity = self.calculate_allowable_quantity(product, "BUY", -best_ask_amount)
                        print(str(product), "BUY", str(best_ask_amount) + "x", str(allowable_quantity) + "x", best_ask )
                        orders.append(Order(product, best_ask, allowable_quantity))
                        self.update_position(product, "BUY", allowable_quantity)
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        allowable_quantity = self.calculate_allowable_quantity(product, "SELL", best_bid_amount)
                        print(str(product), "SELL", str(-best_bid_amount) + "x", str(allowable_quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -allowable_quantity))
                        self.update_position(product, "SELL", allowable_quantity)

            if(product == 'ORCHIDS'):
                self.humidityList.append(state.observations.conversionObservations['ORCHIDS'].humidity)

                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                signal = self.generate_signal(state, self.humidityList)
                print(f"  !!!Signal: {signal}, humidityList: {self.humidityList}!!!  ")
                # Calculate the predicted price using the model coefficients
                if signal == 1:
                    if len(order_depth.sell_orders) != 0:
                        # Buy if predicted price is significantly higher than best ask price
                        allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', "BUY", -best_ask_amount)
                        print(str(product), "BUY", str(best_ask_amount) + "x", str(allowable_quantity) + "x", best_ask)
                        orders.append(Order(product, best_ask, allowable_quantity))
                        self.update_position(product, "BUY", allowable_quantity)
                if signal == -1:
                    if len(order_depth.buy_orders) != 0:
                        # Sell if predicted price is significantly lower than best bid price and we have a position to sell

                        allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', "SELL", best_bid_amount)
                        print(str(product), "SELL", str(-best_bid_amount) + "x", str(allowable_quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -allowable_quantity))
                        self.update_position(product, "SELL", allowable_quantity)
            result[product] = orders
            print(f"  !!!Position: {self.position}!!!  ")
            
        data = jsonpickle.encode("hello")
        return result, 0, data

