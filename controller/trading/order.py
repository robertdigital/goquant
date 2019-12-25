from entity.constants import *


class GQOrder(object):
    symbol = ""
    qty = ""
    side = ""
    type = ""
    time_in_force = ""

    def __init__(self, symbol, qty, side, type=ORDER_TYPE_MARKET,
                 time_in_force="day"):
        self.symbol = symbol
        self.qty = float(qty)
        self.side = side
        self.type = type
        self.time_in_force = time_in_force
        if self.qty <= 0:
            raise ValueError("GQOrder get <= 0 qty: {}".format(qty))

    def get_dict(self):
        """
        import function for alpaca trading
        :return:
        """
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "type": self.type,
            "time_in_force": self.time_in_force,
        }
