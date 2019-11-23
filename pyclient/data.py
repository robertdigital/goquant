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
                        end_date):
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
        start_date_str = start_date.strftime(TIME_FMT)
        end_daate_str = end_date.strftime(TIME_FMT)
        out_dict = self.data.get_data(
            symbols=symbols,
            freq=freq,
            start_date=start_date_str,
            end_date=end_daate_str,
            datasource=DATASOURCE_ALPACA,
            use_cache=True
        )

        # convert to output format
        out_df = None
        for symbol in out_dict:
            cur_df = out_dict[symbol]
            cur_df[DATA_SYMBOL] = symbol
            if out_df is None:
                out_df = cur_df
            else:
                out_df = pd.concat([out_df, cur_df])
        # reorder columns
        if out_df is None:
            logger.error("get empty historical data")
            return
        out_df = out_df[DATA_HISTORICAL_COLS]
        return out_df

    def clean_cache(self):
        """
        clean all data cache, reload all data
        :return:
        """
        self.data.clean_cache()
