import collections
from typing import Dict, List
from datamodel import OrderDepth, UserId, TradingState, Order
import pandas as pd
import statistics


class Trader:
    position = {}
    POSITION_LIMIT = {'STARFRUIT':20, 'AMETHYSTS':20}
    starfruit_cache = []
    amethyst_cache = []
    starfruit_dim = 4
    amethyst_dim = 3
    def update_cache(self, order_depth_starfruit, order_depth_amethyst):
        # Update the caches for STARFRUIT and AMETHYSTS based on order depth data
        
        self.starfruit_cache.append((bs_starfruit + bb_starfruit) / 2)

        _, bs_amethyst = self.values_extract(collections.OrderedDict(sorted(order_depth_amethyst.sell_orders.items())))
        _, bb_amethyst = self.values_extract(collections.OrderedDict(sorted(order_depth_amethyst.buy_orders.items(), reverse=True)), 1)
        self.amethyst_cache.append((bs_amethyst + bb_amethyst) / 2)

        # Maintain cache dimensions
        if len(self.starfruit_cache) == self.starfruit_dim + 1:
            self.starfruit_cache.pop(0)
        if len(self.amethyst_cache) == self.amethyst_dim + 1:
            self.amethyst_cache.pop(0)

        return bs_starfruit, bb_starfruit, bs_amethyst, bb_amethyst

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
        


    def compute_orders(self, product, acc_bid, acc_ask, best_bid, best_ask):
        if product == "STARFRUIT":
            return self.compute_orders_starfruit(product, acc_bid, acc_ask, best_bid, best_ask, self.POSITION_LIMIT[product])
        elif product == "AMETHYSTS":
            return self.compute_orders_amethyst(product, acc_bid, acc_ask, best_bid, best_ask, self.POSITION_LIMIT[product])
        else:
            return []  # Return empty list for other products

    def compute_orders_starfruit(self, product, acc_bid, acc_ask, best_bid, best_ask, position_limit):
        # Define a list to hold the orders
        orders = []

        # Calculate the average price from the cache
        avg_price = statistics.mean(self.starfruit_cache)

        # Define the buy and sell thresholds
        buy_threshold = 0.95  # Buy if the current ask price is 5% less than the average price
        sell_threshold = 1.05  # Sell if the current bid price is 5% more than the average price

        # If the current bid price is higher than the sell threshold, we want to sell
        if acc_bid > avg_price * sell_threshold:
            # Check if we have enough in our position to sell
            if self.position.get(product, 0) > 0:
                # Create a sell order
                order = Order(product, acc_bid, -best_bid)
                orders.append(order)

        # If the current ask price is lower than the buy threshold, we want to buy
        elif acc_ask < avg_price * buy_threshold:
            # Check if buying won't exceed our position limit
            if self.position.get(product, 0) < position_limit:
                # Create a buy order
                order = Order(product, acc_ask, -best_ask)
                orders.append(order)

        return orders

    def compute_orders_amethyst(self, product, acc_bid, acc_ask, best_bid, best_ask, position_limit):
        # Define a list to hold the orders
        orders = []

        # Calculate the average price from the cache
        avg_price = statistics.mean(self.amethyst_cache)

        # If the current bid price is higher than the average price, we want to sell
        if acc_bid > avg_price:
            # Check if we have enough in our position to sell
            if self.position.get(product, 0) > 0:
                # Create a sell order
                order = Order(product, acc_bid, -best_bid)
                orders.append(order)

        # If the current ask price is lower than the average price, we want to buy
        elif acc_ask < avg_price:
            # Check if buying won't exceed our position limit
            if self.position.get(product, 0) < position_limit:
                # Create a buy order
                order = Order(product, acc_ask, best_ask)
                orders.append(order)

        return orders
            
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        result = {'STARFRUIT': [], 'AMETHYSTS': []}
        order_depth_starfruit = state.order_depths['STARFRUIT']
        order_depth_amethyst = state.order_depths['AMETHYSTS']

        self.update_cache(order_depth_starfruit, order_depth_amethyst)
        print(self.starfruit_cache)
        print(self.amethyst_cache)
        INF = 1e9
        starfruit_lower = -INF
        starfruit_upper = INF
        if(len(self.starfruit_cache) > 0):
            starfruit_lower = min(self.starfruit_cache)
            starfruit_upper = max(self.starfruit_cache)
        amethyst_lower = -INF
        amethyst_upper = INF
        if(len(self.amethyst_cache) > 0):
            amethyst_lower = min(self.amethyst_cache)
            amethyst_upper = max(self.amethyst_cache)

        
        Sbest_ask_amount = list(state.order_depths['STARFRUIT'].sell_orders.items())[0]
        Abest_bid_amount = list(state.order_depths['AMETHYSTS'].buy_orders.items())[0]
        acc_bid = {'STARFRUIT': starfruit_lower, 'AMETHYSTS': amethyst_lower}
        
        acc_ask = {'STARFRUIT': starfruit_upper, 'AMETHYSTS': amethyst_upper}
        
        for product in state.order_depths.keys():
            orders = self.compute_orders(product, acc_bid[product], acc_ask[product], Sbest_ask_amount, Abest_bid_amount)
            result[product] += orders
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1
        return result, conversions, traderData