import unittest

from datetime import datetime, timedelta
from entity.constants import TIME_FMT, FREQ_DAY, DATASOURCE_ALPACA, DATASOURCE_CACHE
from controller.data.data import Data


class TestData(unittest.TestCase):
    def test_get_data(self):
        data = Data()
        cur_datetime = datetime.today()
        end_datetime_str = cur_datetime.strftime(TIME_FMT)
        start_datetime = cur_datetime - timedelta(weeks=1)
        start_datetime_str = start_datetime.strftime(TIME_FMT)

        # test load data remote
        data.clean_cache()
        df_dict = data.get_data(symbols=["SPY", "UBER"],
                                freq=FREQ_DAY,
                                start_date=start_datetime_str,
                                end_date=end_datetime_str,
                                datasource=DATASOURCE_ALPACA,
                                use_cache=True)

        assert len(df_dict) == 2
        assert "SPY" in df_dict
        assert "UBER" in df_dict
        assert df_dict["SPY"].shape == (5, 6)
        assert df_dict["UBER"].shape == (5, 6)
        self.assertListEqual(
            list(
                df_dict["SPY"].columns), [
                'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])

        # test load from cache
        df_dict = data.get_data(symbols=["SPY", "UBER"],
                                freq=FREQ_DAY,
                                start_date=start_datetime_str,
                                end_date=end_datetime_str,
                                datasource=DATASOURCE_CACHE,
                                use_cache=True)
        assert df_dict["SPY"].shape == (5, 6)
        assert df_dict["UBER"].shape == (5, 6)

        file_path = data.get_data_path(["SPY", "UBER"],
                                       freq=FREQ_DAY,
                                       start_date=start_datetime_str,
                                       end_date=end_datetime_str)
        assert len(file_path) == 2
        assert "UBER" in file_path
        assert "SPY" in file_path
        data.clean_cache()
