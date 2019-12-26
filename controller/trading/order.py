from entity.constants import *


class GQOrder(object):
    symbol = ""
    qty = ""
    side = ""
    price = None
    type = ""
    time_in_force = ""

    def __init__(self,
                 symbol,
                 qty,
                 side,
                 price=None,
                 type=ORDER_TYPE_MARKET,
                 time_in_force=ORDER_TIME_IN_FORCE_GTC):
        self.symbol = symbol
        self.qty = float(qty)
        self.side = side
        self.price = price
        self.type = type
        self.time_in_force = time_in_force
        if self.qty <= 0:
            raise ValueError("GQOrder get <= 0 qty: {}".format(qty))
        if self.type == ORDER_TYPE_LIMIT:
            if self.price is None or self.price < 0:
                raise ValueError("GQOrder get price < 0: {}".format(price))
