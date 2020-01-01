from entity.constants import *
from util.logger import logger


class GQOrder(object):
    symbol = ""
    qty = ""
    side = ""
    price = None
    type = ""
    time_in_force = ""
    fraction_qty = False
    valid = False

    def __init__(self,
                 symbol,
                 qty,
                 side,
                 price=None,
                 type=ORDER_TYPE_MARKET,
                 time_in_force=ORDER_TIME_IN_FORCE_GTC,
                 fraction_qty=False):
        self.symbol = symbol
        self.qty = float(qty)
        self.side = side
        self.price = price
        self.type = type
        self.time_in_force = time_in_force
        self.fraction_qty = fraction_qty
        if not fraction_qty:
            self.qty = round(self.qty, 0)
        if self.qty <= 0:
            logger.error("Invalide order, GQOrder get <= 0 qty: {}".format(qty))
            return
        if self.type == ORDER_TYPE_LIMIT:
            if self.price is None or self.price < 0:
                logger.error("Invalide order, GQOrder get price < 0: {}".format(price))
                return
        self.valid = True

    @staticmethod
    def get_valid_orders(orders):
        valid_orders = []
        for cur_order in orders:
            if cur_order.valid:
                valid_orders.append(cur_order)
        return valid_orders
