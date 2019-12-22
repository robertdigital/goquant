from controller.trading.trading import Trading
from controller.trading.base_algo import BaseAlgo
from entity.order import Order


class GQTrading(object):
    def __init__(self, algos, trading_platform, run_freq_s=1):
        """
        trading system
        :param run_freq_s: int
            running frequency in sec
        :param trading_platform: string
            alpha or binance
        :param algos: dict
            name string -> GQAlgo object
        """
        self.trading_engine = Trading(trading_platform=trading_platform, run_freq_s=run_freq_s, algos=algos)

    def start(self):
        """
        start load algo and start trading
        sync model now
        :return:
        """
        self.trading_engine.start()


class GQOrder(Order):
    def __init__(self, symbol, qty, side, type="market", time_in_force="day"):
        """
        create order
        :param symbol: string
        :param qty: int
        :param side: string
            buy or sell
        :param type: string
            market
        :param time_in_force: string
            day
        """
        super().__init__(symbol, qty, side, type=type, time_in_force=time_in_force)


class GQAlgo(object):
    def __init__(self, trading_platform):
        self.algo = BaseAlgo(trading_platform)

    def init(self):
        pass

    def run(self):
        raise NotImplementedError

    def get_cash(self):
        """
        get current cash in USD
        :return:
        """
        return self.algo.account.get_cash()

    def get_positions(self):
        """
        get current positions
        :return:
        """
        return self.algo.account.get_positions()
