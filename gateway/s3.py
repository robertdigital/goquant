from kafka import KafkaConsumer
from json import loads

import logging
import datetime
import pytz
import boto3
from datetime import datetime
import pickle
from entity.kafka import decode_kafka_msg
from entity.constants import DATASOURCE_BITMEX, TIME_FMT_MIN

from config.config import TradingConfig


class S3Gateway(object):
    s3_client = None

    def __init__(self):
        self.cfg = TradingConfig()
        logging.info("connecting to s3")
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=self.cfg.aws_id,
                                      aws_secret_access_key=self.cfg.aws_key)
        logging.info("connected to s3")

    def consume_orderbook_kafka_to_s3(self):
        logging.info("connecting to kafka topic: {}".format(self.cfg.kafka_topic_bitmex_orderbook))
        consumer = KafkaConsumer(
            self.cfg.kafka_topic_bitmex_orderbook,
            bootstrap_servers=[self.cfg.kafka_bootstrap_servers],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda x: loads(x.decode('utf-8')))

        prev_ts = ""
        aggregate_data = {}
        for message in consumer:
            data, ts = decode_kafka_msg(message)
            ts = datetime.fromtimestamp(ts, tz=pytz.utc).strftime(TIME_FMT_MIN)
            symbol, freq = data["symbol"], data["freq"]
            logging.debug("receive kafka msg ts: {}, symbol: {}".format(ts, symbol))

            if ts != prev_ts:
                # get new key, move to next minute, push old data to s3
                for s in aggregate_data:
                    key = self.get_min_orderbook_key(s, freq, ts, source=DATASOURCE_BITMEX)
                    logging.info("saving to s3, key: {}".format(key))
                    self.s3_client.put_object(Bucket=self.cfg.bitmex_orderbook_s3,
                                              Key=key,
                                              Body=pickle.dumps(aggregate_data[s]))
                prev_ts = ts
                aggregate_data = {}
            cur_list = aggregate_data.get(symbol, [])
            cur_list.append(data)
            aggregate_data[symbol] = cur_list
        raise ValueError("save_kafka_to_s3 shouldn't close")

    def get_min_orderbook_key(self, symbol, freq, ts_str, source=DATASOURCE_BITMEX):
        key = "orderbook_{source}_{freq}_{symbol}_{ts}".format(source=source,
                                                               freq=freq,
                                                               symbol=symbol,
                                                               ts=ts_str)
        return key


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    test_gateway = S3Gateway()
    test_gateway.consume_orderbook_kafka_to_s3()
