from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    position = {'STARFRUIT': 0, 'AMETHYSTS': 0}
    position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20}
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
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if(product == "AMETHYSTS"):
                acceptable_price = 10000  # Participant should calculate this value
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                allowable_quantity = self.calculate_allowable_quantity(product, 'BUY', -best_ask_amount)
                quantity = min(allowable_quantity, -best_ask_amount)
                if int(best_ask) < acceptable_price:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, quantity))
                    self.update_position(product, -quantity)
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                allowable_quantity = self.calculate_allowable_quantity(product, 'SELL', -best_bid_amount)
                quantity = min(allowable_quantity, -best_bid_amount)
                if int(best_bid) > acceptable_price:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, quantity))
                    self.update_position(product, quantity)
            
            result[product] = orders
    
    
        #next_trader_data = jsonpickle.encode(state.traderData)
        traderData = jsonpickle.encode(result)
        
        conversions = 1
        return result, conversions, traderData