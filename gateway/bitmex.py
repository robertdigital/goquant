"""
get API from https://github.com/BitMEX/api-connectors
there is a bug in util import
"""
from gateway.bitmex_api.bitmex_websocket import BitMEXWebsocket
#from bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep


class BitmexGateway(object):
    TESTNET_ENDPOINT = "https://testnet.bitmex.com/api/v1"
    BITMEX_ENDPOINT = "https://www.bitmex.com/api/v1"

    def __init__(self):
        pass

    def record_bitmex_order_book(self, symbol):
        """
        XBTUSD
        :param symbol:
        :return:
        """
        ws = BitMEXWebsocket(endpoint=self.TESTNET_ENDPOINT,
                             symbol=symbol,
                             api_key=None,
                             api_secret=None)

        logging.info("Instrument data: %s" % ws.get_instrument())

        # Run forever
        while ws.ws.sock.connected:
            logging.info("Ticker: %s" % ws.get_ticker())
            logging.info("Market Depth: %s" % ws.market_depth())
            logging.info("Recent Trades: %s\n\n" % ws.recent_trades())
            sleep(1)


if __name__ == "__main__":
    test_gateway = BitmexGateway()
    test_gateway.record_bitmex_order_book("XBTUSD")
