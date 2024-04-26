import collections
from typing import Dict, List
from datamodel import OrderDepth, UserId, TradingState, Order
import pandas as pd
import statistics

class Trader:
    position = {'STARFRUIT':0, 'AMETHYSTS':0}
    POSITION_LIMIT = {'STARFRUIT':20, 'AMETHYSTS':20}
    starfruit_cache = []
    amethyst_cache = []
    starfruit_dim = 4
    amethyst_dim = 3

    def values_extract(self, order_dict, buy=0):
        total_volume = 0
        best_value = -1
        max_volume = -1

        for price, volume in order_dict.items():
            if buy == 0:
                volume *= -1
            total_volume += volume
            if total_volume > max_volume:
                max_volume = total_volume
                best_value = price

        return total_volume, best_value
    def calc_next_price_starfruit(self):
        # calc_next_price_starfruit cache stores price from 1 day ago, current day resp
        # by price, here we mean mid price

        X = list(range(1, len(self.starfruit_cache) + 1))  # Days as X values
        y = self.starfruit_cache  # Historical prices as y values

        # Calculate the mean of X and y
        mean_X = statistics.mean(X)
        mean_y = statistics.mean(y)

        # Calculate the terms needed for the slope (m) and y-intercept (b) of the regression line
        numerator = sum((X[i] - mean_X) * (y[i] - mean_y) for i in range(len(X)))
        denominator = sum((X[i] - mean_X) ** 2 for i in range(len(X)))

        # Calculate the slope (m) and y-intercept (b)
        m = numerator / denominator
        b = mean_y - m * mean_X

        # Predict the next price based on the next day (assuming len(self.starfruit_cache) days so far)
        next_day = len(self.starfruit_cache) + 1
        next_price = m * next_day + b
        return next_price


    def compute_orders(self, product, order_depth, acc_bid, acc_ask):
            return self.compute_orders_starfruit(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])
    
    def compute_orders_starfruit(self, product, order_depth, acc_bid, acc_ask, LIMIT):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        cpos = self.position[product]

        for ask, vol in osell.items():
            if ((ask <= acc_bid) or ((self.position[product]<0) and (ask == acc_bid+1))) and cpos < LIMIT:
                order_for = min(-vol, LIMIT - cpos)
                if cpos + order_for > LIMIT:  # Check if adding this order would exceed the limit
                    order_for = LIMIT - cpos
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask)

        if cpos < LIMIT:
            num = LIMIT - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product] - 13

        

        for bid, vol in obuy.items():
            if ((bid >= acc_ask) or ((self.position[product]>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
                order_for = max(-vol, -LIMIT-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if cpos > -LIMIT:
            num = -LIMIT-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]: 
        result = {'STARFRUIT': [], 'AMETHYSTS': []}

        if len(self.starfruit_cache) == self.starfruit_dim + 1:
            self.starfruit_cache.pop(0)
        if len(self.amethyst_cache) == self.amethyst_dim + 1:
            self.amethyst_cache.pop(0)

        for key, val in state.position.items():
            self.position[key] = val
        for key, val in self.position.items():
            print(f'{key} position: {val}')

        order_depth_starfruit = state.order_depths['STARFRUIT']
        _, bs_starfruit = self.values_extract(collections.OrderedDict(sorted(order_depth_starfruit.sell_orders.items())))
        _, bb_starfruit = self.values_extract(collections.OrderedDict(sorted(order_depth_starfruit.buy_orders.items(), reverse=True)), 1)
        self.starfruit_cache.append((bs_starfruit + bb_starfruit) / 2)
        order_depth_amethyst = state.order_depths['AMETHYSTS']
        _, bs_amethyst = self.values_extract(collections.OrderedDict(sorted(order_depth_amethyst.sell_orders.items())))
        _, bb_amethyst = self.values_extract(collections.OrderedDict(sorted(order_depth_amethyst.buy_orders.items(), reverse=True)), 1)
        self.amethyst_cache.append((bs_amethyst + bb_amethyst) / 2)
        
        INF = 1e9
    
        starfruit_lb = 0
        starfruit_ub = 0
        if(len(self.starfruit_cache) > 1):
            starfruit_lb = self.calc_next_price_starfruit()-1
            starfruit_ub = self.calc_next_price_starfruit()+1

        amethyst_lb = 10000
        amethyst_ub = 10000

        # CHANGE FROM HERE

        acc_bid = {'AMETHYSTS' : amethyst_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : amethyst_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above
        for product in ['AMETHYSTS', 'STARFRUIT']:
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            result[product] += orders

        conversions = 1
        traderData = "SAMPLE"
        return result, conversions, traderData