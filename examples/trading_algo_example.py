from pyclient.constants import *
from pyclient import GQTrading
from .example_algo import AlgoBuySPYDip

if __name__ == '__main__':
    trading_platform = TRADING_ALPACA
    trade = GQTrading(
        run_freq_s=600000,  # only run algo once
        algos={
            "AlgoBuySPYDip": AlgoBuySPYDip(trading_platform, DATASOURCE_ALPACA)
        })
    trade.start()
