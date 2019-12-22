import unittest
import pandas as pd
import numpy as np

from entity.mapper import binance_to_goquant
from entity.constants import *


class TestMapper(unittest.TestCase):
    def test_binance_klines_to_goquant(self):
        in_data_raw = [
            [
                1514444400000,
                "13656.98000000",
                "14100.00000000",
                "13656.98000000",
                "13984.39000000",
                "870.29864700",
                1514447999999,
                "12143589.71018280",
                5638,
                "503.24284700",
                "7021722.44454967",
                "0"
            ],
            [
                1514448000000,
                "13984.38000000",
                "14170.00000000",
                "13752.00000000",
                "14054.99000000",
                "772.16566400",
                1514451599999,
                "10768222.47966626",
                5537,
                "432.89126000",
                "6040111.77771890",
                "0"
            ]
        ]
        in_data = pd.DataFrame(in_data_raw, columns=KLINES_DATA_COLS).astype(np.float64)
        out_data = binance_to_goquant("test_symbol", in_data)
        self.assertEqual(out_data.shape, (2, len(DATA_HISTORICAL_COLS)))
        self.assertEqual(out_data[DATA_SYMBOL][0], "test_symbol")
        self.assertEqual(out_data[DATA_OPEN][0], 13656.98000000)
        self.assertEqual(out_data.index[0], pd.Timestamp(year=2017, month=12, day=28, hour=7))
