import time
import pandas as pd
import numpy as np

from gateway.binance_api.client import Client
from config.config import TradingConfig

from entity.constants import FREQ_DAY, FREQ_MINUTE, KLINES_DATA_COLS
from util.logger import logger
from util.date import interval_to_milliseconds, date_to_milliseconds
from entity.mapper import order_goquant_to_binance


class BinanceGateway(object):
    def __init__(self, requests_params=None):
        self.cfg = TradingConfig()
        self.client = Client(api_key=self.cfg.binance_api_key,
                             api_secret=self.cfg.binance_secret_key,
                             requests_params=requests_params)

    def get_historical_klines(
            self, symbol, freq, start_datetime, end_datetime=None):
        """Get Historical Klines from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param freq: str
            day, minute
        :type start_datetime: datetime
            data start time
        :param end_datetime: datetime
            data end time
        :return: dataframe
            list of OHLCV values
        """
        interval_map = {
            FREQ_DAY: Client.KLINE_INTERVAL_1DAY,
            FREQ_MINUTE: Client.KLINE_INTERVAL_1MINUTE
        }
        interval = interval_map[freq]

        # init our list
        output_data = []

        # setup the max limit
        limit = 500

        # convert interval to useful value in seconds
        timeframe = interval_to_milliseconds(interval)

        # convert our date strings to milliseconds
        start_ts = date_to_milliseconds(start_datetime)

        # if an end time was passed convert it
        end_ts = None
        if end_datetime:
            end_ts = date_to_milliseconds(end_datetime)

        idx = 0
        # it can be difficult to know when a symbol was listed on Binance so
        # allow start time to be before list date
        symbol_existed = False
        while True:
            # fetch the klines from start_ts up to max 500 entries or the
            # end_ts if set
            logger.debug("get_klines input: symbol:{}, interval:{}, limit:{}, startTime:{}, endTime:{}".format(
                symbol, interval, limit, start_ts, end_ts
            ))
            temp_data = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=start_ts,
                endTime=end_ts
            )

            # handle the case where our start date is before the symbol pair
            # listed on Binance
            if not symbol_existed and len(temp_data):
                symbol_existed = True

            if symbol_existed:
                # append this loops data to our output data
                output_data += temp_data

                # update our start timestamp using the last value in the array
                # and add the interval timeframe
                start_ts = temp_data[len(temp_data) - 1][0] + timeframe
            else:
                # it wasn't listed yet, increment our start date
                start_ts += timeframe

            idx += 1
            # check if we received less than the required limit and exit the
            # loop
            if len(temp_data) < limit:
                # exit the while loop
                break

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)
        df_binance = pd.DataFrame(
            output_data,
            columns=KLINES_DATA_COLS).astype(
            np.float64)
        return df_binance

    def start(self):
        pass

    def trade(self, orders: list):
        for order in orders:
            binance_order = order_goquant_to_binance(order)
            logger.debug("binance order: {}".format(binance_order))
            response = self.client.create_order(**binance_order)
            logger.debug("binance order response: {}".format(response))
