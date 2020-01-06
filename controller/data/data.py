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
from gateway.polygon_gateway import PolygonGateway, PolygonRequestException
from entity.mapper import binance_to_goquant, data_polygon_to_goquant


class GQData(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.binance = BinanceGateway()
        self.polygon = PolygonGateway()
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
                 dict_output=False,
                 fill_nan_method=None,
                 remove_nan_rows=True):
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
        :param fill_nan_method: string
            fill nan method, default not fill, see more parameters here:
            https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
        :param remove_nan_rows: bool
            remove nan rows after fill nan
        :return: dataframe
            dataframe contains symbols historical data
        """
        if datasource not in VALID_DATASOURCE:
            raise (
                "datasource {} not in valid list {}".format(
                    datasource, VALID_DATASOURCE))

        if freq not in VALID_FREQ:
            raise (
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
                data_key = self.get_data_key(
                    symbol, freq, start_date, end_date)
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

        # post-process data, such as data clean, fill nan
        df_dict = self._post_process_data(df_dict, fill_nan_method=fill_nan_method, remove_nan_rows=remove_nan_rows)

        # save output
        if use_cache:
            for symbol in df_dict:
                data_key = self.get_data_key(
                    symbol, freq, start_date, end_date)
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

    def get_order_book(self, symbols, datasource):
        ret = {}
        if datasource == DATASOURCE_BINANCE:
            for symbol in symbols:
                cur_data = self.binance.get_order_book(symbol)
                ret[symbol] = cur_data
        else:
            logger.error("{} not support order book data yet".format(datasource))
        return ret

    def check_data_key(self, data_key):
        filepath = self.get_data_file_path(data_key)
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
        filepath = self.get_data_file_path(data_key)
        if not overwrite and os.path.isfile(filepath):
            logger.debug("exist data file, skip: {}".format(filepath))
        else:
            logger.info("saving data file to: {}".format(filepath))
            df.index.name = DATA_DATETIME
            df.to_csv(filepath, date_format='%Y-%m-%d %H:%M:%S')

    def load_df(self, data_key):
        filepath = self.get_data_file_path(data_key)
        if os.path.isfile(filepath):
            logger.debug("loading data from file: {}".format(filepath))
            df = pd.read_csv(filepath)
            df.set_index("Date Time", inplace=True)
            return df
        else:
            return None

    def get_data_file_path(self, data_key):
        return "{}/{}.csv".format(self.cfg.csv_data_path, data_key)

    def clean_cache(self):
        if os.path.exists(self.cfg.csv_data_path):
            shutil.rmtree(self.cfg.csv_data_path)

    def _post_process_data(self, data_dict, fill_nan_method, remove_nan_rows):
        data_dict = self._fill_nan(data_dict, fill_nan_method, remove_nan_rows)
        # make sure symbol is not nan
        for symbol in data_dict:
            data_dict[symbol][DATA_SYMBOL] = symbol
        return data_dict

    @staticmethod
    def _fill_nan(data_dict, fill_nan_method=None, remove_nan_rows=False):
        union_index = pd.Index([])
        for symbol in data_dict:
            cur_df = data_dict[symbol]
            union_index = union_index.union(cur_df.index)
        union_index = union_index.sort_values()
        keep_index = None
        ret_dict = {}
        for symbol in data_dict:
            cur_df = data_dict[symbol]
            new_df = cur_df.reindex(union_index)
            if fill_nan_method is not None:
                new_df = new_df.fillna(method=fill_nan_method)
            if remove_nan_rows:
                keep_df = new_df.dropna(how='any')
                if keep_index is None:
                    keep_index = keep_df.index
                else:
                    keep_index = keep_index.intersection(keep_df.index)
            ret_dict[symbol] = new_df.copy()
        if remove_nan_rows and keep_index is not None:
            for symbol in ret_dict:
                ret_dict[symbol] = ret_dict[symbol].loc[keep_index, :]

        return ret_dict

    def _get_prices_remote(self, symbols, freq,
                           start_date, end_date, datasource):
        df_dict = {}
        if datasource == DATASOURCE_ALPACA:
            df_dict = self._alpaca_get_prices(
                symbols, freq, start_date, end_date)
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

    def _alpaca_get_prices(self, symbols, freq, start_datetime, end_datetime):
        df_dict = {}
        for symbol in symbols:
            try:
                cur_df = self.polygon.get_historical_data(
                    symbol=symbol,
                    freq=freq,
                    start_date_str=start_datetime.strftime(
                        PolygonGateway.DATE_FMT),
                    end_date_str=end_datetime.strftime(
                        PolygonGateway.DATE_FMT),
                    unadjusted=False,
                )
            except PolygonRequestException as err:
                logger.warning(
                    "alpaca get error when load data, err:{}".format(err))
                continue
            gq_cur_df = data_polygon_to_goquant(cur_df)
            df_dict[symbol] = gq_cur_df
        return df_dict

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
