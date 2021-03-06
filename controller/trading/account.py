from pyalgotrade import strategy

from gateway.alpaca import AlpacaGateway
from gateway.binance import BinanceGateway

from entity.constants import *


def get_account_class(trading_platform):
    if trading_platform == TRADING_ALPACA:
        return AlpacaAccount()
    elif trading_platform == TRADING_BINANCE:
        return BinanceAccount()
    elif trading_platform == TRADING_BACKTEST:
        return BacktestAccount()


class Account(object):
    cash = 0.0
    positions = {}  # symbol->{'qty': 1, 'side': 'buy'}

    def get_cash(self):
        self._clean()
        self._update_account_info()
        return self.cash

    def get_positions(self):
        self._clean()
        self._update_account_info()
        return self.positions

    def _update_account_info(self):
        raise NotImplementedError

    def _add_position(self, symbol, qty):
        self.positions[symbol] = {'qty': qty}

    def _clean(self):
        self.cash = 0.0
        self.positions = {}


class AlpacaAccount(Account):
    POSITION_LONG = "long"
    POSITION_SHORT = "short"

    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.alpaca.start()

    def _update_account_info(self):
        account = self.alpaca.api.get_account()
        self.cash = account.cash

        positions = self.alpaca.api.list_positions()

        for p in positions:
            if p.qty < 0:
                raise ValueError("get alpaca position qty < 0, qty: {}".format(p.qty))
            if p.side == self.POSITION_LONG:
                self._add_position(p.symbol, p.qty)
            elif p.side == self.POSITION_SHORT:
                self._add_position(p.symbol, -p.qty)
            else:
                raise ValueError("unknown alpaca position side: {}".format(p.side))


class BinanceAccount(Account):
    def __init__(self):
        self.binance = BinanceGateway()

    def _update_account_info(self):
        self.account_info = self.binance.client.get_account()
        for asset in self.account_info["balances"]:
            free_qty = float(asset["free"])
            symbol = "{}USDT".format(asset["asset"])
            if symbol == "USDUSDT":
                self.cash = free_qty
            elif free_qty != 0.0:
                self._add_position(symbol, free_qty)


class BacktestAccount(Account):
    def __init__(self):
        self.strategy = None

    def _update_account_info(self):
        if self.strategy is None:
            raise ValueError(
                "call set_backtest_strategy to set strategy first")
        broker = self.strategy.getBroker()

        self.cash = broker.getCash()
        positions = broker.getPositions()
        for symbol in positions:
            qty = positions[symbol]
            self._add_position(symbol, qty)

    def set_backtest_strategy(self, strategy: strategy.BacktestingStrategy):
        self.strategy = strategy
