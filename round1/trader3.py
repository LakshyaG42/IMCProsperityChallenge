import collections
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import statistics

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT': 0, 'AMETHYSTS': 0}
        self.position_limit = {'STARFRUIT': 20, 'AMETHYSTS': 20}
        self.starfruit_cache = []
        self.amethyst_cache = []
        self.cache_size = {'STARFRUIT': 4, 'AMETHYSTS': 3}

    def _extract_values(self, order_dict, buy=False):
        total_volume = 0
        best_value = -1
        max_volume = -1

        for price, volume in order_dict.items():
            if buy:
                volume *= -1
            total_volume += volume
            if total_volume > max_volume:
                max_volume = total_volume
                best_value = price

        return total_volume, best_value

    def _calculate_next_price(self, cache):
        if len(cache) < 2:
            return None

        X = list(range(1, len(cache) + 1))
        y = cache

        mean_X = statistics.mean(X)
        mean_y = statistics.mean(y)

        numerator = sum((X[i] - mean_X) * (y[i] - mean_y) for i in range(len(X)))
        denominator = sum((X[i] - mean_X) ** 2 for i in range(len(X)))

        m = numerator / denominator
        b = mean_y - m * mean_X

        next_day = len(cache) + 1
        return m * next_day + b

    def _adjust_orders(self, orders, product):
        total_amount = sum(order.quantity for order in orders)
        if total_amount > self.position_limit[product]:
            diff = total_amount - self.position_limit[product]
            orders.sort(key=lambda x: x.quantity)
            while diff > 0 and orders:
                order = orders.pop()
                if order.quantity <= diff:
                    diff -= order.quantity
                else:
                    order.quantity -= diff
                    orders.append(order)
                    diff = 0
        return orders
    def _compute_orders(self, product, order_depth, acc_bid, acc_ask):
        orders = []

        sell_orders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        buy_orders = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self._extract_values(sell_orders)
        buy_vol, best_buy_pr = self._extract_values(buy_orders, buy=True)

        current_pos = self.position[product]
        LIMIT = self.position_limit[product]

        for ask, vol in sell_orders.items():
            if ((ask <= acc_bid) or ((current_pos < 0) and (ask == acc_bid + 1))) and current_pos < LIMIT:
                order_for = min(-vol, LIMIT - current_pos)
                current_pos += order_for
                assert order_for >= 0
                orders.append(Order(product, ask, order_for))

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid)
        sell_pr = max(undercut_sell, acc_ask)

        if current_pos < LIMIT:
            num = LIMIT - current_pos
            orders.append(Order(product, bid_pr, num))
            current_pos += num

        current_pos -= 13  # Adjusting position for trading

        for bid, vol in buy_orders.items():
            if ((bid >= acc_ask) or ((current_pos > 0) and (bid + 1 == acc_ask))) and current_pos > -LIMIT:
                order_for = max(-vol, -LIMIT - current_pos)
                current_pos += order_for
                assert order_for <= 0
                orders.append(Order(product, bid, order_for))

        if current_pos > -LIMIT:
            num = -LIMIT - current_pos
            orders.append(Order(product, sell_pr, num))
            current_pos += num

        self._adjust_orders(orders, product)
        self.position[product] = current_pos
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {'STARFRUIT': [], 'AMETHYSTS': []}

        for key, val in state.position.items():
            self.position[key] = val

        for product in ['STARFRUIT', 'AMETHYSTS']:
            order_depth = state.order_depths[product]
            _, bs = self._extract_values(collections.OrderedDict(sorted(order_depth.sell_orders.items())))
            _, bb = self._extract_values(collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True)), buy=True)
            cache = self.starfruit_cache if product == 'STARFRUIT' else self.amethyst_cache
            cache.append((bs + bb) / 2)
            if len(cache) > self.cache_size[product]:
                cache.pop(0)

            next_price = self._calculate_next_price(cache)
            acc_bid = next_price - 1 if next_price is not None else 0
            acc_ask = next_price + 1 if next_price is not None else float('inf')

            orders = self._compute_orders(product, order_depth, acc_bid, acc_ask)
            orders = self._adjust_orders(orders, product)
            result[product] += orders

        conversions = 1  # Placeholder value, modify as needed
        trader_data = "SAMPLE"  # Placeholder value, modify as needed

        return result, conversions, trader_data
