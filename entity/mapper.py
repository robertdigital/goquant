import pandas as pd
import numpy as np
from entity.constants import *


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



