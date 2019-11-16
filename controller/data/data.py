import pandas as pd
import os
from datetime import datetime
from util.logger import logger
import shutil


from gateway.alpaca import AlpacaGateway
from entity.constants import *
from config.config import TradingConfig


class Data(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.cfg = TradingConfig()
        self.alpaca.start()
        self.df_all = None

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
        # check end date
        today_str = datetime.today().strftime(TIME_FMT)
        if end_date != today_str:
            logger.error(
                "end_date only support today, {} != {}".format(
                    end_date, today_str))

        if datasource not in VALID_DATASOURCE:
            logger.error(
                "datasource {} not in valid list {}".format(
                    datasource, VALID_DATASOURCE))

        if freq not in VALID_FREQ:
            logger.error(
                "freq {} not in valid list {}".format(
                    freq, VALID_FREQ))

        # get cached data
        df_dict = {}
        load_symbol = []
        if use_cache:
            for symbol in symbols:
                filename = DATA_FILE_FMT.format(
                    symbol=symbol, freq=freq, start_date=start_date, end_date=end_date)
                cur_df = self.load_df(filename)
                if cur_df is None:
                    load_symbol.append(symbol)
                else:
                    df_dict[symbol] = cur_df
        else:
            load_symbol = symbols

        # get data from data provider
        if len(load_symbol) > 0 and datasource != DATASOURCE_CACHE:
            new_df_dict = self._get_prices_remote(
                load_symbol, freq, start_date, end_date, datasource)
            df_dict.update(new_df_dict)

        # save output
        if use_cache:
            for symbol in df_dict:
                filename = DATA_FILE_FMT.format(
                    symbol=symbol, freq=freq, start_date=start_date, end_date=end_date)
                self.save_df(df_dict[symbol], filename, False)

        return df_dict

    def get_data_path(self, symbols, freq, start_date, end_date):
        """
        get saved data path
        :param symbols: list of string
            symbols
        :param freq: string
            frequency
        :param start_date: string
            in YYYY-MM-DD format
        :param end_date: striing
            in YYYY-MM-DD format
        :return: dict
            symbol->data path
        """
        ret = {}
        for symbol in symbols:
            key = DATA_FILE_FMT.format(
                symbol=symbol, freq=freq, start_date=start_date, end_date=end_date)
            filepath = "{}/{}.csv".format(self.cfg.csv_folder, key)
            if os.path.isfile(filepath):
                os.path.abspath(filepath)
                ret[symbol] = filepath
        return ret

    def save_df(self, df, key, overwrite=False):
        if not os.path.exists(self.cfg.csv_folder):
            os.makedirs(self.cfg.csv_folder)
        filepath = "{}/{}.csv".format(self.cfg.csv_folder, key)
        if not overwrite and os.path.isfile(filepath):
            logger.info("exist data file, skip: {}".format(filepath))
        else:
            logger.info("saving data file to: {}".format(filepath))
            df.to_csv(filepath)

    def load_df(self, key):
        filepath = "{}/{}.csv".format(self.cfg.csv_folder, key)
        if os.path.isfile(filepath):
            logger.info("loading data from file: {}".format(filepath))
            df = pd.read_csv(filepath)
            df.set_index("Date Time", inplace=True)
            return df
        else:
            return None

    def clean_cache(self):
        if os.path.exists(self.cfg.csv_folder):
            shutil.rmtree(self.cfg.csv_folder)

    def _get_prices_remote(self, symbols, freq, start_date,
                           end_date=datetime.today().strftime(TIME_FMT),
                           datasource=DATASOURCE_ALPACA):
        start_datetime = datetime.strptime(start_date, TIME_FMT)
        end_datetime = datetime.strptime(end_date, TIME_FMT)

        df_dict = {}
        if datasource == DATASOURCE_ALPACA and freq == FREQ_DAY:
            delta = end_datetime - start_datetime
            days = delta.days
            df_dict = self._get_prices_to_today(
                symbols=symbols, freq="day", length=days)
            # cut days
            for symbol in df_dict:
                df_dict[symbol] = df_dict[symbol].loc[start_date:]
        else:
            logger.error("unsupported datasource and freq")

        return df_dict

    def _get_prices_to_today(self, symbols, freq, length):
        data_df = self.alpaca.get_prices(symbols=symbols,
                                         freq=freq,
                                         length=length)
        if data_df.empty:
            err = ValueError("data get_price return empty")
            logger.error(err)
            raise err
        else:
            logger.debug("get number of data shape: " + str(data_df.shape))

        df_dict = {}
        for symbol in symbols:
            cur_df = data_df[symbol].rename(
                {'open': 'Open', 'high': 'High', 'low': 'Low',
                    'close': 'Close', 'volume': 'Volume'},
                axis=1)
            cur_df['Adj Close'] = cur_df['Close']
            cur_df.index.names = ['Date Time']
            cur_df.index = cur_df.index.astype(str).str[:-6]
            cur_df.dropna(inplace=True)
            df_dict[symbol] = cur_df

        return df_dict
