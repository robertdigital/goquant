from kafka import KafkaConsumer
from json import loads

import logging
import datetime
import pytz
import boto3
from datetime import datetime
import pickle
from entity.kafka import decode_kafka_msg
from entity.constants import DATASOURCE_BITMEX, TIME_FMT_MIN, FREQ_MINUTE, FREQ_DAY

from config.config import TradingConfig


class S3Gateway(object):
    s3_client = None

    def __init__(self):
        self.cfg = TradingConfig()
        logging.info("connecting to s3")
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=self.cfg.aws_id,
                                      aws_secret_access_key=self.cfg.aws_key)
        self.s3_orderbook_bucket = self.cfg.bitmex_orderbook_s3
        logging.info("connected to s3")

    def get_min_orderbook_key(self, symbol, freq, time_str, source=DATASOURCE_BITMEX):
        key = "orderbook_{source}_{freq}_{symbol}_{time_str}".format(source=source,
                                                               freq=freq,
                                                               symbol=symbol,
                                                               time_str=time_str)
        return key

    # write data
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
                    self.s3_client.put_object(Bucket=self.s3_orderbook_bucket,
                                              Key=key,
                                              Body=pickle.dumps(aggregate_data[s]))
                prev_ts = ts
                aggregate_data = {}
            cur_list = aggregate_data.get(symbol, [])
            cur_list.append(data)
            aggregate_data[symbol] = cur_list
        raise ValueError("save_kafka_to_s3 shouldn't close")

    # load data
    def get_orderbook(self, symbol, ts):
        # ts in milliseconds
        ts = ts/1000.0
        time_str = datetime.fromtimestamp(ts, tz=pytz.utc).strftime(TIME_FMT_MIN)
        freq = self.cfg.bitmex_orderbook_freq
        key = self.get_min_orderbook_key(symbol, freq, time_str, source=DATASOURCE_BITMEX)

        ret = None
        try:
            obj = self.s3_client.get_object(Bucket=self.s3_orderbook_bucket, Key=key)
            ret = pickle.loads(obj['Body'].read())
        except Exception as e:
            logging.error("error during read obj {} from s3, full error: {}".format(key, e))
        return ret


from util.date import date_to_milliseconds
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    test_gateway = S3Gateway()
    ts_date = datetime(2020, 1, 15, 2, 23, 0, 0, pytz.UTC)
    ts = date_to_milliseconds(ts_date)
    orderbook = test_gateway.get_orderbook("XBTUSD", ts)

    from entity.mapper import orderbook_to_orderbook_df
    orderbook_df = orderbook_to_orderbook_df(orderbook, depth_precentage=0.1, depth_bin=20, include_tail=False)
    print(orderbook_df)
