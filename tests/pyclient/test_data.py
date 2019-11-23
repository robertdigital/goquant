import unittest
from datetime import datetime, timedelta
from entity.constants import *
from pyclient.data import GQData


class TestData(unittest.TestCase):
    def test_historical_data_freq_day_7day(self):
        cur_datetime = datetime.today()
        start_datetime = cur_datetime - timedelta(weeks=1)
        gq_data = GQData()
        out_df = gq_data.historical_data(
            symbols=["SPY", "UBER"],
            freq=FREQ_DAY,
            start_date=start_datetime,
            end_date=cur_datetime,
        )
        self.assertEqual(set(out_df[DATA_SYMBOL].unique()), set(["SPY", "UBER"]))
        self.assertListEqual(
            list(out_df.columns), DATA_HISTORICAL_COLS)
        assert out_df.shape[0] >= 10
        assert out_df.shape[0] <= 14

    def test_historical_data_freq_minute_2day(self):
        cur_datetime = datetime.today()
        start_datetime = cur_datetime - timedelta(days=2)
        gq_data = GQData()
        out_df = gq_data.historical_data(
            symbols=["SPY", "UBER"],
            freq=FREQ_MINUTE,
            start_date=start_datetime,
            end_date=cur_datetime,
        )
        self.assertEqual(set(out_df[DATA_SYMBOL].unique()), set(["SPY", "UBER"]))
        self.assertListEqual(
            list(out_df.columns), DATA_HISTORICAL_COLS)
        assert out_df.shape[0] >= 500
