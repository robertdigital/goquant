
class Order(object):
    symbol = ""
    qty = ""
    side = ""
    type = ""
    time_in_force = ""

    def __init__(self, symbol, qty, side, type="market", time_in_force="day"):
        self.symbol = symbol
        self.qty = qty
        self.side = side
        self.type = type
        self.time_in_force = time_in_force

    def get_dict(self):
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "type": self.type,
            "time_in_force": self.time_in_force,
        }
