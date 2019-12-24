"""
https://polygon.io/docs/#getting-started

historical data: https://api.polygon.io/v2/aggs/ticker/AAPL/range/

"""
import logging
import requests
import pandas as pd

from entity.constants import *
from config.config import TradingConfig
from util.date import datestr_to_datetime


class PolygonGateway(object):
    DATE_FMT = "%Y-%m-%d"

    BASE_URL = "https://api.polygon.io/"
    HISTORICAL_DATA_URL = "/v2/aggs/ticker/{symbol}/range/{multiplier}/{freq}/{start_date_str}/{end_date_str}"

    VALID_FREQ = ["day", "minute", "hour"]

    def __init__(self):
        self.cfg = TradingConfig()
        self.api_key = self.cfg.alpaca_id
        self.session = self._init_session()

    def get_historical_data(
            self, symbol, freq, start_date_str, end_date_str, unadjusted=False):
        # check input format
        datestr_to_datetime(start_date_str, self.DATE_FMT)
        datestr_to_datetime(end_date_str, self.DATE_FMT)

        if freq not in self.VALID_FREQ:
            raise PolygonRequestException(
                "freq {} is not in valid freq list {}".format(
                    freq, self.VALID_FREQ))

        path = self.HISTORICAL_DATA_URL.format(
            symbol=symbol,
            freq=freq,
            multiplier=1,
            start_date_str=start_date_str,
            end_date_str=end_date_str,
        )
        res = self._request_api("get", path, unadjusted=unadjusted)
        res_df = pd.DataFrame.from_records(res["results"])
        res_df[POLYGON_SYMBOL] = symbol
        return res_df

    def _init_session(self):
        session = requests.session()
        session.headers.update({'Accept': 'application/json'})
        return session

    def _request_api(self, method, path, **kwargs):
        api_kwargs = dict()
        api_kwargs["params"] = kwargs
        api_kwargs["params"]["apiKey"] = self.api_key

        uri = "{}/{}".format(self.BASE_URL, path)
        logging.debug("polygon send request: method: {}, uri_apikey:{}, api_kwargs:{}".format(
            method, uri, api_kwargs
        ))
        self.response = getattr(self.session, method)(uri, **api_kwargs)
        return self._handle_response()

    def _handle_response(self):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(self.response.status_code).startswith('2'):
            raise PolygonAPIException(self.response)
        try:
            return self.response.json()
        except ValueError:
            raise PolygonRequestException(
                'Invalid Response: %s' %
                self.response.text)


class PolygonAPIException(Exception):

    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Polygon: {}'.format(
                response.text)
        else:
            self.message = json_res['message']
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'Polygon APIError: %s' % self.message


class PolygonRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'PolygonRequestException: %s' % self.message
