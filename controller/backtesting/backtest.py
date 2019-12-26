"""
use pyalgotrade
http://gbeced.github.io/pyalgotrade/docs/v0.20/html/tutorial.html
"""
from pyalgotrade import strategy
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.bar import Frequency, Bars
from pyalgotrade.stratanalyzer import returns
from pyalgotrade import plotter

from controller.trading.algo import GQAlgo
from controller.data.data import GQData
from entity.mapper import order_goquant_to_backtest
from entity.constants import *
from util.logger import logger


class GQBacktest(object):
    def __init__(self,
                 algo: GQAlgo,
                 symbols,
                 start_datetime,
                 end_datetime,
                 data_freq=FREQ_DAY,
                 initial_cash=10000,
                 ):
        self.algo = algo
        self.symbols = symbols
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.data_freq = data_freq
        self.datasource = algo.datasource
        self.initial_cash = initial_cash

        self.data = GQData()

        freq_map = {
            FREQ_DAY: Frequency.DAY,
            FREQ_MINUTE: Frequency.MINUTE,
        }
        self.datafeed = csvfeed.GenericBarFeed(freq_map[data_freq])
        self._load_datafeed()

        self.my_strategy = MyStrategy(
            self.datafeed,
            self.symbols,
            self.algo,
            self.initial_cash)
        self.returnsAnalyzer = returns.Returns()
        self.my_strategy .attachAnalyzer(self.returnsAnalyzer)

    def _load_datafeed(self):
        # loading all data
        self.data.get_data(
            symbols=self.symbols,
            freq=self.data_freq,
            start_date=self.start_datetime,
            end_date=self.end_datetime,
            datasource=self.datasource,
            use_cache=True,
        )

        data_files = {}
        for symbol in self.symbols:

            data_key = self.data.get_data_key(
                symbol=symbol,
                freq=self.data_freq,
                start_date=self.start_datetime,
                end_date=self.end_datetime,
            )
            file_path = self.data.get_data_file_path(data_key)
            data_files[symbol] = file_path

            logger.debug("add csv file {} into data feed".format(file_path))
            self.datafeed.addBarsFromCSV(symbol, file_path, skipMalformedBars=True)

    def run(self, plot=True):
        if plot:
            plt = plotter.StrategyPlotter(self.my_strategy)
            plt.getOrCreateSubplot("returns").addDataSeries(
                "Simple returns", self.returnsAnalyzer.getReturns())

        self.my_strategy.run()
        logger.info(
            "Final portfolio value: $%.2f" %
            self.my_strategy.getBroker().getEquity())

        if plot:
            plt.plot()


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, symbols, gq_algo: GQAlgo, initial_cash):
        super(MyStrategy, self).__init__(feed, initial_cash)
        self.setUseAdjustedValues(True)
        self.symbols = symbols
        self.gq_algo = gq_algo
        self.gq_algo.init_backtest(self)

    def onBars(self, bars: Bars):
        t = bars.getDateTime()
        self.gq_algo.prerun(t)
        gq_orders = self.gq_algo.run()
        for gq_order in gq_orders:
            if gq_order.type == ORDER_TYPE_MARKET:
                market_order = order_goquant_to_backtest(gq_order)
                logger.info(
                    "submit order to backtest: {}".format(market_order))
                self.marketOrder(**market_order)
            else:
                raise ValueError(
                    "backtest unsupport order type: {}".format(
                        gq_orders.type))
