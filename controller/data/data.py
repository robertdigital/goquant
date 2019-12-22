import pandas as pd
import os
import pytz
from datetime import datetime, timezone
from util.logger import logger
import shutil


from gateway.alpaca import AlpacaGateway
from entity.constants import *
from config.config import TradingConfig

from gateway.binance import BinanceGateway
from entity.mapper import binance_to_goquant, alpaca_to_goquant


class Data(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.binance = BinanceGateway()
        self.cfg = TradingConfig()
        self.alpaca.start()
        self.df_all = None

    def get_data(self,
                 symbols,
                 freq,
                 start_date,
                 end_date=datetime.now(timezone.utc),
                 datasource=DATASOURCE_ALPACA,
                 use_cache=True,
                 dict_output=False):
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
        :return: dataframe
            dataframe contains symbols historical data
        """
        if datasource not in VALID_DATASOURCE:
            raise(
                "datasource {} not in valid list {}".format(
                    datasource, VALID_DATASOURCE))

        if freq not in VALID_FREQ:
            raise(
                "freq {} not in valid list {}".format(
                    freq, VALID_FREQ))
        logger.info("loading data...")

        start_date = start_date.astimezone(pytz.utc)
        end_date = end_date.astimezone(pytz.utc)

        # get cached data
        df_dict = {}
        load_symbol = []
        if use_cache:
            for symbol in symbols:
                data_key = self.get_data_key(symbol, freq, start_date, end_date)
                if self.check_data_key(data_key):
                    cur_df = self.load_df(data_key)
                    df_dict[symbol] = cur_df
                else:
                    load_symbol.append(symbol)
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
                data_key = self.get_data_key(symbol, freq, start_date, end_date)
                self.save_df(df_dict[symbol], data_key, False)

        logger.info("loaded done. symbol number {}".format(len(df_dict)))

        if dict_output:
            return df_dict
        else:
            ret = None
            for symbol in df_dict:
                if ret is None:
                    ret = df_dict[symbol]
                else:
                    ret = pd.concat([ret, df_dict[symbol]])
            return ret

    def check_data_key(self, data_key):
        filepath = self._get_data_file_path(data_key)
        return os.path.isfile(filepath)

    def get_data_key(self, symbol, freq, start_date, end_date):
        start_date = start_date.astimezone(pytz.utc)
        end_date = end_date.astimezone(pytz.utc)
        start_date_str = start_date.strftime(TIME_FMT)
        end_date_str = end_date.strftime(TIME_FMT)
        key = DATA_FILE_FMT.format(
            symbol=symbol, freq=freq, start_date=start_date_str, end_date=end_date_str)
        return key

    def save_df(self, df, data_key, overwrite=False):
        if not os.path.exists(self.cfg.csv_data_path):
            os.makedirs(self.cfg.csv_data_path)
        filepath = self._get_data_file_path(data_key)
        if not overwrite and os.path.isfile(filepath):
            logger.debug("exist data file, skip: {}".format(filepath))
        else:
            logger.info("saving data file to: {}".format(filepath))
            df.to_csv(filepath)

    def load_df(self, data_key):
        filepath = self._get_data_file_path(data_key)
        if os.path.isfile(filepath):
            logger.debug("loading data from file: {}".format(filepath))
            df = pd.read_csv(filepath)
            df.set_index("Date Time", inplace=True)
            return df
        else:
            return None

    def _get_data_file_path(self, data_key):
        return "{}/{}.csv".format(self.cfg.csv_data_path, data_key)

    def clean_cache(self):
        if os.path.exists(self.cfg.csv_data_path):
            shutil.rmtree(self.cfg.csv_data_path)

    def _get_prices_remote(self, symbols, freq, start_date, end_date, datasource):
        df_dict = {}
        if datasource == DATASOURCE_ALPACA:
            if freq == FREQ_DAY:
                delta = end_date - start_date
                length = delta.days
            elif freq == FREQ_MINUTE:
                delta = end_date - start_date
                length = delta.days * 8 * 60
            else:
                raise ValueError("unsupported freq: {}".format(freq))
            df_dict = self._alpaca_get_prices_to_today(
                symbols=symbols, freq=freq, length=length)
            # cut days
            for symbol in df_dict:
                df_dict[symbol] = df_dict[symbol].loc[start_date:]
        elif datasource == DATASOURCE_BINANCE:
            df_dict = self._binance_get_prices(
                symbols=symbols,
                freq=freq,
                start_datetime=start_date,
                end_datetime=end_date,
            )
        else:
            logger.error("unsupported datasource: {}".format(datasource))

        return df_dict

    def _alpaca_get_prices_to_today(self, symbols, freq, length):
        data_df = self.alpaca.get_prices(symbols=symbols,
                                         freq=freq,
                                         length=length)
        self._check_data(data_df)

        out_dict = {}
        for symbol in symbols:
            cur_df = alpaca_to_goquant(symbol=symbol,
                                       in_data=data_df)
            out_dict[symbol] = cur_df
        return out_dict

    def _binance_get_prices(self, symbols, freq, start_datetime, end_datetime):
        out_dict = {}
        for symbol in symbols:
            data_df = self.binance.get_historical_klines(
                symbol=symbol,
                freq=freq,
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            self._check_data(data_df)

            cur_df = binance_to_goquant(
                symbol=symbol,
                in_data=data_df)
            out_dict[symbol] = cur_df
        return out_dict

    def _check_data(self, data_df):
        if data_df.empty:
            err = ValueError("get_prices return empty data")
            logger.error(err)
            raise err
        else:
            logger.debug("get number of data shape: " + str(data_df.shape))





