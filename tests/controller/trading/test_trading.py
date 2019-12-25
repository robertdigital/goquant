import unittest

from entity.constants import *
from controller.trading.trading import GQTrading
from controller.trading.algo import GQAlgo


class TestTrading(unittest.TestCase):
    def test_new_trading(self):
        test_algo = GQAlgo(TRADING_ALPACA, DATASOURCE_ALPACA)
        GQTrading(algos={"testAlgo1": test_algo, "testAlgo2": test_algo})
