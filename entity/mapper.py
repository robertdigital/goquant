import pandas as pd
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

def stream_binance_to_db():
    pass
