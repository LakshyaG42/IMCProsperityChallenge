from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import statistics
import math
import numpy as np
import pandas as pd
import jsonpickle

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0, 'ORCHIDS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100}
        self.starfruit_cache = []
        self.amethyst_cache = []
        self.orchids_cache = []
        self.cache_size = {'STARFRUIT': 20, 'AMETHYSTS': 6}


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = 1190  
            if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        #print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acceptable_price:
                    #print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            result[product] = orders

        print("Trader Data = " + state.traderData)
        print("Observations = " + str(state.observations))
        print("Listings = " + str(state.listings))
        print ("Order Depths = " + str(state.order_depths))
        print("Own Trades = " + str(state.own_trades))
        print("Market Trades = " + str(state.market_trades))
        print("Position = " + str(state.position))
        
        return result, 0, jsonpickle.encode("Hello World!")
            
    