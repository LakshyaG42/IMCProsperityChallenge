import collections
import pandas as pd
import jsonpickle
from typing import List, Tuple
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0, 'CHOCOLATE': 0, 'STRAWBERRIES': 0, 'ROSES': 0, 'GIFT_BASKET': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}
        self.signal_window = 5
        self.humidityList = []
        self.prev_humidity = None 
        self.basket_std = 117
        self.cont_buy_basket_unfill = 0
        self.cont_sell_basket_unfill = 0

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
    

    def compute_orders_basket(self, order_depth):
        orders = {'CHOCOLATE': [], 'STRAWBERRIES': [], 'ROSES': [], 'GIFT_BASKET': []}
        prods = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
        sell_orders_dict, buy_orders_dict, best_sell_price, best_buy_price = {}, {}, {}, {}
        worst_sell_price, worst_buy_price, mid_prices, volume_buy, volume_sell = {}, {}, {}, {}, {}
        for product in prods:
            sell_orders_dict[product] = collections.OrderedDict(sorted(order_depth[product].sell_orders.items()))
            buy_orders_dict[product] = collections.OrderedDict(sorted(order_depth[product].buy_orders.items(), reverse=True))

            best_sell_price[product] = next(iter(sell_orders_dict[product]))
            best_buy_price[product] = next(iter(buy_orders_dict[product]))

            worst_sell_price[product] = next(reversed(sell_orders_dict[product]))
            worst_buy_price[product] = next(reversed(buy_orders_dict[product]))

            mid_prices[product] = (best_sell_price[product] + best_buy_price[product]) / 2
            volume_buy[product], volume_sell[product] = 0, 0
            for price, vol in buy_orders_dict[product].items():
                volume_buy[product] += vol
                if volume_buy[product] >= self.position_limit[product] / 10:
                    break
            for price, vol in sell_orders_dict[product].items():
                volume_sell[product] += -vol
                if volume_sell[product] >= self.position_limit[product] / 10:
                    break


        res_buy = mid_prices['GIFT_BASKET'] - mid_prices['CHOCOLATE'] * 4 - mid_prices['STRAWBERRIES'] * 6 - mid_prices['ROSES'] - 375
        res_sell = mid_prices['GIFT_BASKET'] - mid_prices['CHOCOLATE'] * 4 - mid_prices['STRAWBERRIES'] * 6 - mid_prices['ROSES'] - 375

        trade_at = self.basket_std * 0.5

        pb_pos = self.position['GIFT_BASKET']
        pb_neg = self.position['GIFT_BASKET']


        if self.position['GIFT_BASKET'] == self.position_limit['GIFT_BASKET']:
            self.cont_buy_basket_unfill = 0
        if self.position['GIFT_BASKET'] == -self.position_limit['GIFT_BASKET']:
            self.cont_sell_basket_unfill = 0

        if res_sell > trade_at:
            vol = self.position['GIFT_BASKET'] + self.position_limit['GIFT_BASKET']
            self.cont_buy_basket_unfill = 0  
            assert (vol >= 0)
            if vol > 0:
                orders['GIFT_BASKET'].append(Order('GIFT_BASKET', worst_buy_price['GIFT_BASKET'], -vol))
                self.cont_sell_basket_unfill += 2
                pb_neg -= vol
        elif res_buy < -trade_at:
            vol = self.position_limit['GIFT_BASKET'] - self.position['GIFT_BASKET']
            self.cont_sell_basket_unfill = 0 
            assert (vol >= 0)
            if vol > 0:
                orders['GIFT_BASKET'].append(Order('GIFT_BASKET', worst_sell_price['GIFT_BASKET'], vol))
                self.cont_buy_basket_unfill += 2
                pb_pos += vol

        return orders

    def calculate_coconut_momentum_signal(self, order_depth: OrderDepth) -> Tuple[float, int]:
        signal = 0  # Default no signal
        conversions = 0
        
        # Check if there are enough buy and sell orders for coconut and coconut coupons
        if 'COCONUT' in order_depth and 'COCONUT_COUPON' in order_depth:
            coconut_orders = order_depth['COCONUT']
            coupon_orders = order_depth['COCONUT_COUPON']
            
            # Check if there are enough buy and sell orders for coconut
            if len(coconut_orders.sell_orders) > 0 and len(coconut_orders.buy_orders) > 0:
                best_coconut_sell_price = next(iter(coconut_orders.sell_orders))
                best_coconut_buy_price = next(iter(coconut_orders.buy_orders))

                # Check if there are enough buy and sell orders for coconut coupons
                if len(coupon_orders.sell_orders) > 0 and len(coupon_orders.buy_orders) > 0:
                    best_coupon_sell_price = next(iter(coupon_orders.sell_orders))
                    best_coupon_buy_price = next(iter(coupon_orders.buy_orders))

                    # Calculate the momentum signal based on coconut and coconut coupon prices
                    if best_coconut_sell_price < best_coupon_sell_price:
                        signal = 1  # Buy signal
                    elif best_coconut_buy_price > best_coupon_buy_price:
                        signal = -1  # Sell signal

                    # Calculate conversions based on signal
                    if signal == 1:
                        conversions = self.calculate_allowable_quantity('COCONUT_COUPON', 'SELL', self.position_limit['COCONUT_COUPON'])
                    elif signal == -1:
                        conversions = self.calculate_allowable_quantity('COCONUT_COUPON', 'BUY', self.position_limit['COCONUT_COUPON'])

        return signal, conversions





    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            conversions = 0
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
                self.humidityList.append(state.observations.conversionObservations['ORCHIDS'].humidity)
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                current_position = self.position['ORCHIDS']
                signal = self.generate_signal(state, self.humidityList)
                print(f"  !!!Signal: {signal}, humidityList: {self.humidityList}!!!  ")
                # Calculate the predicted price using the model coefficients
                if signal == 1:
                    if len(order_depth.sell_orders) != 0:
                        # Buy if predicted price is significantly higher than best ask price
                        allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_ask, best_ask_amount)
                        print(str(product), "BUY", str(best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, best_ask_amount))
                        self.update_position(product, "BUY", best_ask_amount)
                        conversions = best_ask_amount
                        
                if signal == -1:
                    if len(order_depth.buy_orders) != 0:
                        # Sell if predicted price is significantly lower than best bid price and we have a position to sell
                        allowable_quantity = self.calculate_allowable_quantity('ORCHIDS', best_bid, -best_bid_amount)
                        print(str(product), "SELL", str(-best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                        self.update_position(product, "SELL", best_bid_amount)
                        conversions = best_bid_amount
                
               

            if(product in ('CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET')):
                if(product == 'CHOCOLATE'):
                    acceptable_price = 8000
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
                if(product == 'STRAWBERRIES'):
                    acceptable_price = 4020
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
                if(product == 'ROSES'):
                    acceptable_price = 14600
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
                            

                if(product == 'GIFT_BASKET'):
                    orders += self.compute_orders_basket(state.order_depths)["GIFT_BASKET"]

                    # acceptable_price = 71000
                    # if len(order_depth.sell_orders) != 0:
                    #     best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    #     if int(best_ask) < acceptable_price:
                    #         quantity = self.calculate_allowable_quantity(product, "BUY", best_ask_amount)
                    #         print(str(product), "BUY", str(best_ask_amount) + "x", best_ask)
                    #         orders.append(Order(product, best_ask, best_ask_amount))
                    #         self.update_position(product, "BUY", best_ask_amount)
        
                    # if len(order_depth.buy_orders) != 0:
                    #     best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    #     if int(best_bid) > acceptable_price:
                    #         quantity = self.calculate_allowable_quantity(product, "SELL", best_bid_amount)
                    #         print(str(product), "SELL", str(-best_bid_amount) + "x", best_bid)
                    #         orders.append(Order(product, best_bid, -best_bid_amount))
                    #         self.update_position(product, "SELL", best_bid_amount)
            result[product] = orders    
        data = jsonpickle.encode("hello")
        print(f"Conversions: {conversions}")
        return result, conversions, data

