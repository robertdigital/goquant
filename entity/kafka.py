import time


def encode_kafka_msg(data):
    return {
        "data": data,
        "ts": time.time()
    }


def decode_kafka_msg(msg):
    msg = msg.value
    return msg["data"], float(msg["ts"])
