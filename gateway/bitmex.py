"""
get API from https://github.com/BitMEX/api-connectors
there is a bug in util import
"""
from gateway.bitmex_api.bitmex_websocket import BitMEXWebsocket
from kafka import KafkaProducer
from json import dumps
import logging
import time
from time import sleep

from entity.kafka import encode_kafka_msg
from entity.mapper import stream_bitmex_to_orderbook
from config.config import TradingConfig


class BitmexGateway(object):
    TESTNET_ENDPOINT = "https://testnet.bitmex.com/api/v1"
    BITMEX_ENDPOINT = "https://www.bitmex.com/api/v1"

    def __init__(self):
        self.cfg = TradingConfig()
        self.freq = self.cfg.bitmex_orderbook_freq

    def produce_orderbook_to_kafka(self, symbol):
        ws = BitMEXWebsocket(endpoint=self.BITMEX_ENDPOINT,
                             symbol=symbol,
                             api_key=self.cfg.bitmex_id,
                             api_secret=self.cfg.bitmex_key)

        logging.info("Instrument data: %s" % ws.get_instrument())

        kafka_producer = KafkaProducer(bootstrap_servers=[self.cfg.kafka_bootstrap_servers],
                                       value_serializer=lambda x:
                                       dumps(x).encode('utf-8'))

        # Run forever
        while ws.ws.sock.connected:
            start_time = time.time()
            depth = ws.market_depth()
            orderbook = stream_bitmex_to_orderbook(depth, freq=self.freq)
            kafka_producer.send(self.cfg.kafka_topic_bitmex_orderbook,
                                value=encode_kafka_msg(data=orderbook))
            sleep(self.freq)
            logging.info("market depth Size: {}, runtiime {} s".format(len(depth), time.time() - start_time))


if __name__ == "__main__":
    test_gateway = BitmexGateway()
    test_gateway.produce_orderbook_to_kafka("XBTUSD")
