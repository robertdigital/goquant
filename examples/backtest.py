from datetime import datetime

from entity.constants import *
from controller.backtesting.backtest import GQBacktest
from examples.example_algo import AlgoBuySPYDip, Universe


if __name__ == '__main__':
    symbols = Universe
    start_datetime = datetime(2019, 12, 1)
    end_datetime = datetime(2019, 12, 7)
    my_algo = AlgoBuySPYDip(trading_platform=TRADING_BACKTEST, datasource=DATASOURCE_ALPACA)
    gq_backtest = GQBacktest(algo=my_algo,
                             symbols=symbols,
                             start_datetime=start_datetime,
                             end_datetime=end_datetime,
                             data_freq=FREQ_DAY,
                             initial_cash=10000)
    gq_backtest.run()

