import unittest
import pytest

import os
from datetime import datetime, timedelta
from pyclient.constants import *
from pyclient import GQData


class TestData(unittest.TestCase):
    @pytest.mark.skipif(os.environ[ENV_TEST_LEVEL]
                        == TEST_LEVEL_UNIT, reason="unit test")
    def test_alpaca_datasource(self):
        symbols = ["SPY", "AAPL"]

        # test data end today
        out_df_7day = self._test_datasource(
            symbols, DATASOURCE_ALPACA, FREQ_DAY, timedelta(weeks=1))
        assert out_df_7day.shape[0] >= len(symbols) * 5
        assert out_df_7day.shape[0] <= len(symbols) * 7

        # test data at 2016 year
        end_datetime = datetime(2015, 1, 17)
        out_df_7day = self._test_datasource(
            symbols, DATASOURCE_ALPACA, FREQ_DAY, timedelta(
                weeks=1), end_datetime)
        assert out_df_7day.shape[0] == len(symbols) * 5

        out_df_1daymin = self._test_datasource(  # 9am-1am
            symbols, DATASOURCE_ALPACA, FREQ_MINUTE, timedelta(days=1), end_datetime)
        assert len(symbols) * 12 * \
            60 <= out_df_1daymin.shape[0] <= len(symbols) * 13.5 * 60

    @pytest.mark.skipif(os.environ[ENV_TEST_LEVEL]
                        == TEST_LEVEL_UNIT, reason="unit test")
    def test_binance_datasource(self):
        symbols = ["BTCUSD", "ETHBTC"]

        # test data end today
        out_df_7day = self._test_datasource(
            symbols, DATASOURCE_BINANCE, FREQ_DAY, timedelta(weeks=1))
        assert out_df_7day.shape[0] == len(symbols) * 7

        out_df_60min = self._test_datasource(
            symbols,
            DATASOURCE_BINANCE,
            FREQ_MINUTE,
            timedelta(
                hours=1))
        assert len(symbols) * 59 <= out_df_60min.shape[0] <= len(symbols) * 61

        # test data for last 3 month
        end_datetime = datetime.now() - timedelta(days=30 * 3 - 7)
        out_df_7day = self._test_datasource(
            symbols, DATASOURCE_BINANCE, FREQ_DAY, timedelta(weeks=1), end_datetime)
        assert out_df_7day.shape[0] == len(symbols) * 7

        out_df_60min = self._test_datasource(
            symbols,
            DATASOURCE_BINANCE,
            FREQ_MINUTE,
            timedelta(hours=1),
            end_datetime)
        assert len(symbols) * 59 <= out_df_60min.shape[0] <= len(symbols) * 61

    def _test_datasource(self, symbols, data_source, freq,
                         time_delta, end_datetime=datetime.today()):
        gq_data = GQData()
        gq_data.clean_cache()

        # test 7 days
        start_datetime = end_datetime - time_delta
        out_df = gq_data.get_data(
            symbols=symbols,
            freq=freq,
            start_date=start_datetime,
            end_date=end_datetime,
            datasource=data_source
        )
        self.assertEqual(set(out_df[DATA_SYMBOL].unique()), set(symbols))
        self.assertListEqual(
            list(out_df.columns), DATA_HISTORICAL_COLS)
        gq_data.clean_cache()
        return out_df
