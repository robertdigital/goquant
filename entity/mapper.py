import pandas as pd
import time
import math
from datetime import datetime
import pytz
import logging

from entity.constants import *
from controller.trading.order import GQOrder
import gateway.binance_api.enums as binance_enums
from pyalgotrade.dataseries import SequenceDataSeries


def alpaca_to_goquant(symbol, in_data):
    cur_df = in_data[symbol].rename(
        {'open': DATA_OPEN, 'high': DATA_HIGH, 'low': DATA_LOW,
         'close': DATA_CLOSE, 'volume': DATA_VOLUME},
        axis=1)
    cur_df[DATA_ADJCLOSE] = cur_df[DATA_CLOSE]
    cur_df[DATA_SYMBOL] = symbol
    cur_df.index.names = [DATA_DATETIME]
    cur_df.dropna(inplace=True)
    return cur_df[DATA_HISTORICAL_COLS]


def binance_to_goquant(symbol, in_data):
    in_data[DATA_DATETIME] = pd.to_datetime(in_data[DATA_DATETIME], unit='ms')
    df_binance = in_data.set_index(DATA_DATETIME)
    df_binance[DATA_SYMBOL] = symbol
    df_binance[DATA_ADJCLOSE] = df_binance[DATA_CLOSE]
    return df_binance[DATA_HISTORICAL_COLS]


def order_goquant_to_binance(order: GQOrder):
    side_map = {
        ORDER_BUY: binance_enums.SIDE_BUY,
        ORDER_SELL: binance_enums.SIDE_SELL
    }
    type_map = {
        ORDER_TYPE_MARKET: binance_enums.ORDER_TYPE_MARKET,
        ORDER_TYPE_LIMIT: binance_enums.ORDER_TYPE_LIMIT,
    }
    time_in_force_map = {
        ORDER_TIME_IN_FORCE_GTC: binance_enums.TIME_IN_FORCE_GTC
    }
    ret = {
        "symbol": order.symbol,
        "side": side_map[order.side],
        "type": type_map[order.type],
        "price": order.price,
        "quantity": order.qty,
        "timeInForce": time_in_force_map[order.time_in_force],
    }
    return ret


def data_polygon_to_goquant(in_df):
    in_df[DATA_DATETIME] = pd.to_datetime(in_df[POLYGON_TS], unit='ms')
    in_df = in_df.set_index(DATA_DATETIME)
    col_map = {
        POLYGON_VOLUME: DATA_VOLUME,
        POLYGON_OPEN: DATA_OPEN,
        POLYGON_CLOSE: DATA_CLOSE,
        POLYGON_HIGH: DATA_HIGH,
        POLYGON_LOW: DATA_LOW,
        POLYGON_SYMBOL: DATA_SYMBOL,
    }
    in_df = in_df.rename(columns=col_map)
    in_df[DATA_ADJCLOSE] = in_df[DATA_CLOSE]
    return in_df[DATA_HISTORICAL_COLS]


def order_goquant_to_backtest(order: GQOrder):
    qty = order.qty
    # if order.side == ORDER_SELL:
    #     qty = -order.qty
    ret = {
        "instrument": order.symbol,
        "quantity": qty,
        "goodTillCanceled": True,
        "allOrNone": True,
    }
    # limit order: # instrument, limitPrice, quantity, goodTillCanceled=False, allOrNone=False
    if order.type == ORDER_TYPE_LIMIT:
        ret["limitPrice"] = order.price
    return ret


def order_goquant_to_backtest_old(order: GQOrder):
    qty = order.qty
    if order.side == ORDER_SELL:
        qty = -order.qty
    ret = {
        "instrument": order.symbol,
        "quantity": qty,
        "goodTillCanceled": True,
        "allOrNone": True,
    }
    if order.type == ORDER_TYPE_MARKET:
        ret["onClose"] = False
        return ret
    elif order.type == ORDER_TYPE_LIMIT:
        ret["limitPrice"] = order.price
        return ret
    else:
        raise ValueError(
            "order_goquant_to_backtest unknown order type:{}".format(
                order.type))


def order_goquant_to_alpaca(order: GQOrder):
    tif = {
        ORDER_TIME_IN_FORCE_GTC: "day"
    }
    ret = {
        "symbol": order.symbol,
        "qty": order.qty,
        "side": order.side,
        "limit_price": order.price,
        "type": order.type,
        "time_in_force": tif[order.time_in_force],
    }
    return ret


def metric_goquant_to_backtest(metric_data_series):
    ret = SequenceDataSeries()
    for i, v in metric_data_series.items():
        ret.appendWithDateTime(i, v)
    return ret


def stream_bitmex_to_orderbook(data_json, freq):
    orderbook = {
        "ts": time.time(),
        "freq": freq,
        "symbol": "",
        "is_buy": [], # 0 sell, 1 buy
        "price": [],
        "size": [],
    }
    if len(data_json) == 0:
        return orderbook
    orderbook["symbol"] = data_json[0]["symbol"]

    n = len(data_json)
    is_buy, prices, sizes = [0]*n, [0]*n, [0]*n
    for i in range(len(data_json)):
        record = data_json[i]
        if record["side"] == "Buy":
            is_buy[i] = 1
        prices[i] = record["price"]
        sizes[i] = record["size"]
    orderbook["is_buy"] = is_buy
    orderbook["price"] = prices
    orderbook["size"] = sizes
    return orderbook


def orderbook_to_orderbook_df(orderbook, depth_precentage=0.1, depth_bin=20, include_tail=False):
    ret = None
    if orderbook is None:
        return ret
    for row in orderbook:
        row_dict = {
            DATA_DATETIME: datetime.fromtimestamp(row["ts"], tz=pytz.utc),
            DATA_SYMBOL: row["symbol"],
        }
        price_list = row["price"]
        size_list = row["size"]
        is_buy_list = row["is_buy"]

        n = len(is_buy_list)
        # find mid price
        bid, ask = -math.inf, math.inf
        for i in range(n):
            price, size, is_buy = price_list[i], size_list[i], is_buy_list[i]
            if is_buy == 1:
                bid = max(price, bid)
            elif is_buy == 0:
                ask = min(price, ask)
            else:
                raise ValueError("unexpected is_buy value: {}".format(is_buy))
        mid = (bid+ask)/2.0
        row_dict[DATA_BID] = bid
        row_dict[DATA_ASK] = ask

        # count size for each price
        while len(price_list) > 0:
            price, size, is_buy = price_list.pop(), size_list.pop(), is_buy_list.pop()
            if is_buy == 1:
                data_col = DATA_BUY_PCT
                pct = ((mid - price) / price) / depth_precentage
            else:
                data_col = DATA_SELL_PCT
                pct = ((price - mid) / price) / depth_precentage
            if pct < 0:
                logging.warning("orderbook pct should >=0: ask/bid: {} mid:{}".format(price, mid))
            if not include_tail and pct > 1:
                continue
            pct = max(min(pct, 0.9999999999), 0)
            bin_idx = int(pct * depth_bin)
            col = data_col.format(bin_idx=bin_idx)
            row_dict[col] = row_dict.get(col, 0) + size
        # cummulative size
        for i in range(1, depth_bin):
            prev_col = DATA_BUY_PCT.format(bin_idx=i - 1)
            col = DATA_BUY_PCT.format(bin_idx=i)
            row_dict[col] = row_dict.get(col, 0) + row_dict.get(prev_col, 0)

            prev_col = DATA_SELL_PCT.format(bin_idx=i - 1)
            col = DATA_SELL_PCT.format(bin_idx=i)
            row_dict[col] = row_dict.get(col, 0) + row_dict.get(prev_col, 0)

        row_dict_df = pd.DataFrame([row_dict], columns=row_dict.keys())
        # append to ret
        if ret is None:
            ret = row_dict_df
        else:
            ret = ret.append(row_dict_df, ignore_index=True, sort=False)
    if ret is not None and not ret.empty:
        ret = ret.set_index(DATA_DATETIME)
    return ret

