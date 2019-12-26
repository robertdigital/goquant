from datetime import datetime, timezone
from pyalgotrade import strategy

from entity.constants import *
from controller.trading.account import get_account_class
from controller.data.data import GQData
from util.logger import logger


class GQAlgo(object):
    def __init__(self, trading_platform, datasource):
        self.trading_platform = trading_platform
        self.datasource = datasource
        self.account = get_account_class(trading_platform)
        self.data = GQData()
        self.t = None  # current time in UTC

        self.backtest_strategy = None

        self.init()

    def init(self):
        pass

    def run(self) -> [list]:
        raise NotImplementedError

    def get_trading_platform(self):
        return self.trading_platform

    def get_time(self):
        return self.t

    def get_cash(self):
        """
        get current cash in USD
        :return:
        """
        return self.account.get_cash()

    def get_positions(self):
        """
        get current positions
        :return: dict
            symbol->position
        """
        return self.account.get_positions()

    def algo_get_data(self, symbols, interval_timedelta, freq):
        """
        get data until now (time t, get from get_time())
        :param symbols: list
            list of symbols
        :param interval_timedelta: deltatime
            used to calculate start time
        :param freq: string
            day, minute data level
        :return:
        """
        end_datetime = datetime.now(timezone.utc)
        if self.trading_platform == TRADING_BACKTEST:
            end_datetime = self.get_time()
            if end_datetime is None:
                raise ValueError("please run prerun() function first")
        start_datetime = end_datetime - interval_timedelta
        data = self.data.get_data(symbols=symbols,
                                  freq=freq,
                                  start_date=start_datetime,
                                  end_date=end_datetime,
                                  datasource=self.datasource,
                                  dict_output=True)
        return data

    def init_backtest(self, strategy: strategy.BacktestingStrategy):
        self.backtest_strategy = strategy
        self.account.set_backtest_strategy(strategy)

    def prerun(self, t, verbose=True):
        if verbose:
            msg = "=============\nAlgorithm Time: {}\nCash: {}\nPositions: {}\n".format(
                t, self.get_cash(), self.get_positions()
            )
            logger.info(msg)
        self.t = t
