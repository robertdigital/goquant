import unittest

from datetime import datetime, timedelta
from entity.constants import *
from controller.data.data import Data


class TestData(unittest.TestCase):
    def test_get_data_alpaca(self):
        self._test_datasource(Data(), ["SPY", "UBER"], DATASOURCE_ALPACA)

    def test_get_data_binance(self):
        self._test_datasource(
            Data(), [
                "ETHBTC", "BTCUSDT"], DATASOURCE_BINANCE)

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
            assert df_dict[symbol].shape[0] >= 5
            assert df_dict[symbol].shape[0] <= 8
            assert df_dict[symbol].shape[1] == 7
            assert df_dict[symbol].shape[1] == 7
            self.assertListEqual(
                list(df_dict[symbol].columns),
                DATA_HISTORICAL_COLS)
