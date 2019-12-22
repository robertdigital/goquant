from gateway.alpaca import AlpacaGateway
from gateway.binance import BinanceGateway

from entity.constants import *


def get_account_class(trading_platform):
    if trading_platform == TRADING_ALPACA:
        return AlpacaAccount()
    elif trading_platform == TRADING_BINANCE:
        return BinanceAccount()


class Account(object):
    def get_cash(self):
        raise NotImplementedError

    def get_positions(self):
        raise NotImplementedError


class AlpacaAccount(Account):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.alpaca.start()

    def get_cash(self):
        account = self.alpaca.api.get_account()
        return account.cash

    def get_positions(self):
        ret = {}
        positions = self.alpaca.api.list_positions()
        p_side_map = {
            'long': ORDER_BUY,
            'short': ORDER_SELL,
        }
        for p in positions:
            ret[p.symbol] = {
                "qty": p.qty,
                "side": p_side_map[p.side]
            }
        return ret


class BinanceAccount(Account):
    def __init__(self):
        self.binance = BinanceGateway()
        self.assets = {}  # symbol->USD dollar
        self.cash = 0.0

    def get_cash(self):
        self._update_account_info()
        return self.cash

    def get_positions(self):
        self._update_account_info()
        return self.assets

    def _update_account_info(self):
        self.account_info = self.binance.client.get_account()
        for asset in self.account_info["balances"]:
            free_qty = float(asset["free"])
            symbol = "{}USDT".format(asset["asset"])
            if symbol == "USDUSDT":
                self.cash = free_qty
            elif free_qty != 0.0:
                self.assets[symbol] = {
                    "qty": free_qty,
                    "side": ORDER_BUY,
                }
