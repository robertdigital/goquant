from pyclient.constants import *
from pyclient import GQTrading
from .example_algo_crypto import AlgoBuySPYDip


if __name__ == "__main__":
    trading_platform = TRADING_BINANCE
    trade = GQTrading(
        run_freq_s=600000,  # only run algo once
        algos={
            "AlgoBuySPYDip": AlgoBuySPYDip(trading_platform, DATASOURCE_BINANCE)
        })
    trade.start()
