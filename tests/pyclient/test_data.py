import unittest
from datetime import datetime, timedelta
from entity.constants import *
from pyclient.data import GQData


class TestData(unittest.TestCase):
    def test_alpacaa_datasource(self):
        symbols = ["SPY", "UBER"]
        out_df_7day = self._test_datasource(symbols, DATASOURCE_ALPACA, FREQ_DAY, timedelta(weeks=1))
        assert out_df_7day.shape[0] >= 10
        assert out_df_7day.shape[0] <= 14

        out_df_2daymin = self._test_datasource(symbols, DATASOURCE_ALPACA, FREQ_MINUTE, timedelta(days=2))
        assert out_df_2daymin.shape[0] >= 500

    def test_binance_datasource(self):
        symbols = ["BTCUSDT", "ETHBTC"]
        out_df_7day = self._test_datasource(symbols, DATASOURCE_BINANCE, FREQ_DAY, timedelta(weeks=1))
        assert out_df_7day.shape[0] >= 10
        assert out_df_7day.shape[0] <= 14

        out_df_60min = self._test_datasource(symbols, DATASOURCE_BINANCE, FREQ_MINUTE, timedelta(hours=1))
        assert out_df_60min.shape[0] == 120

    def _test_datasource(self, symbols, data_source, freq, time_delta):
        gq_data = GQData()
        gq_data.clean_cache()

        # test 7 days
        cur_datetime = datetime.today()
        start_datetime = cur_datetime - time_delta
        out_df = gq_data.historical_data(
            symbols=symbols,
            freq=freq,
            start_date=start_datetime,
            end_date=cur_datetime,
            datasource=data_source
        )
        self.assertEqual(set(out_df[DATA_SYMBOL].unique()), set(symbols))
        self.assertListEqual(
            list(out_df.columns), DATA_HISTORICAL_COLS)
        gq_data.clean_cache()
        return out_df
