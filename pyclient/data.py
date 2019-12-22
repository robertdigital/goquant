from controller.data.data import Data
import pandas as pd
from entity.constants import *
from util.logger import logger


class GQData(object):
    def __init__(self):
        self.data = Data()

    def historical_data(self,
                        symbols,
                        freq,
                        start_date,
                        end_date,
                        datasource=DATASOURCE_ALPACA):
        """
        get historical data for symbols
        :param symbols: list of string
            list of symbols
        :param freq: string
            sec, min, day, week
        :param start_date: datetime
            data start time
        :param end_date: datetime
            data end time
        :return: dataframe
            time (index), symbol, ...
        """
        out_df = self.data.get_data(
            symbols=symbols,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            datasource=datasource,
            use_cache=True,
            dict_output=False,
        )
        return out_df

    def clean_cache(self):
        """
        clean all data cache, reload all data
        :return:
        """
        self.data.clean_cache()
