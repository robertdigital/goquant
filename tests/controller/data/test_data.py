import unittest
import pytest
import os
import pandas as pd
import math

from datetime import datetime, timedelta
from entity.constants import *
from controller.data.data import GQData


class TestData(unittest.TestCase):
    @pytest.mark.skipif(os.environ[ENV_TEST_LEVEL]
                        == TEST_LEVEL_UNIT, reason="unit test")
    def test_get_data_alpaca(self):
        self._test_datasource(GQData(), ["SPY", "UBER"], DATASOURCE_ALPACA)

    @pytest.mark.skipif(os.environ[ENV_TEST_LEVEL]
                        == TEST_LEVEL_UNIT, reason="unit test")
    def test_get_data_binance(self):
        self._test_datasource(
            GQData(), [
                "ETHBTC", "BTCUSDT"], DATASOURCE_BINANCE)

    def test_fill_nan(self):
        df1 = pd.DataFrame.from_dict({
            "date": [datetime(2019, 1, 1), datetime(2019, 1, 2), datetime(2019, 1, 3)],
            "value": [1, 2, 3],
        }).set_index("date")
        df2 = pd.DataFrame.from_dict({
            "date": [datetime(2019, 1, 1), datetime(2019, 1, 3)],
            "value": [1, 3],
        }).set_index("date")
        df1.index = pd.to_datetime(df1.index, unit='ms')
        df2.index = pd.to_datetime(df2.index, unit='ms')
        data_dict = {
            "s1": df1,
            "s2": df2,
        }
        data_dict_out = GQData._fill_nan(data_dict, fill_nan_method=None)
        self.assertEqual(data_dict_out["s1"].shape, (3, 1))
        self.assertEqual(data_dict_out["s2"].shape, (3, 1))
        self.assertTrue(math.isnan(data_dict_out["s2"]["value"][1]))

        data_dict_out = GQData._fill_nan(data_dict, fill_nan_method="ffill")
        self.assertEqual(data_dict_out["s1"].shape, (3, 1))
        self.assertEqual(data_dict_out["s2"].shape, (3, 1))
        self.assertEqual(data_dict_out["s2"]["value"][1], 1)

    def _test_datasource(self, data, symbols, datasource,
                         start_datetime=None, end_datetime=None):
        if start_datetime is None or end_datetime is None:
            end_datetime = datetime.today()
            start_datetime = end_datetime - timedelta(weeks=1)
        # test load data remote
        data.clean_cache()
        df_dict = data.get_data(symbols=symbols,
                                freq=FREQ_DAY,
                                start_date=start_datetime,
                                end_date=end_datetime,
                                datasource=datasource,
                                use_cache=True,
                                dict_output=True)

        self._check_data(symbols, df_dict)

        # test load from cache
        df_dict = data.get_data(symbols=symbols,
                                freq=FREQ_DAY,
                                start_date=start_datetime,
                                end_date=end_datetime,
                                datasource=datasource,
                                use_cache=True,
                                dict_output=True)
        self._check_data(symbols, df_dict)

        for symbol in symbols:
            data_key = data.get_data_key(
                symbol, FREQ_DAY, start_datetime, end_datetime)
            self.assertTrue(data.check_data_key(data_key))
        data.clean_cache()

    def _check_data(self, symbols, df_dict):
        assert len(df_dict) == len(symbols)
        for symbol in symbols:
            assert symbol in df_dict
            assert df_dict[symbol].shape[0] >= 4
            assert df_dict[symbol].shape[0] <= 8
            assert df_dict[symbol].shape[1] == 7
            assert df_dict[symbol].shape[1] == 7
            self.assertListEqual(
                list(df_dict[symbol].columns),
                DATA_HISTORICAL_COLS)
