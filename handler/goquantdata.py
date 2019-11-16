"""
goquant data public interface
"""

from datetime import datetime

from entity.constants import *
from controller.data.data import Data


class GoquantData(object):
    def __init__(self):
        self.data = Data()

    def get_data(self,
                 symbols,
                 freq,
                 start_date,
                 end_date=datetime.today().strftime(TIME_FMT),
                 datasource=DATASOURCE_ALPACA,
                 use_cache=True):
        """
        get historical data
        :param symbols: list of string
            list of symbols
        :param freq: string
            sec, min, day, week
        :param start_date: string
            start_date in YYYY-MM-DD format
        :param end_date:
            end_date in YYYY-MM-DD format
        :param datasource: string
            data source
        :param use_cache: bool
            use saved file
        :return: dict of dataframe
            symbol ->  dataframe
            dataframe contains symbols historical data
        """
        return self.data.get_data(symbols=symbols,
                                  freq=freq,
                                  start_date=start_date,
                                  end_date=end_date,
                                  datasource=datasource,
                                  use_cache=use_cache)
