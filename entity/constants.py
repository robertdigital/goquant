
TIME_FMT = "%Y-%m-%dT%H:%M:%S%z"

DATASOURCE_ALPACA = 'alpaca'
DATASOURCE_BINANCE = 'binance'
DATASOURCE_CACHE = 'cache'
FREQ_DAY = 'day'
FREQ_MINUTE = 'minute'

TRADING_ALPACA = 'alpaca'
TRADING_BINANCE = 'binance'
TRADING_BACKTEST = 'backtest'

TRADING_PLATFORM_DATASOURCE = {
    TRADING_ALPACA: DATASOURCE_ALPACA,
    TRADING_BINANCE: DATASOURCE_BINANCE,
}

VALID_DATASOURCE = [DATASOURCE_ALPACA, DATASOURCE_BINANCE, DATASOURCE_CACHE]
VALID_FREQ = [FREQ_DAY, FREQ_MINUTE]

DATA_FILE_FMT = "{symbol}_{freq}_{start_date}_{end_date}"

DATA_KEY_DF = "df"
DATA_KEY_PATH = "path"

DATA_DATETIME = "Date Time"  # index
DATA_SYMBOL = 'Symbol'
DATA_OPEN = "Open"
DATA_HIGH = "High"
DATA_LOW = "Low"
DATA_CLOSE = "Close"
DATA_VOLUME = "Volume"
DATA_ADJCLOSE = "Adj Close"
DATA_HISTORICAL_COLS = [
    DATA_SYMBOL,
    DATA_OPEN,
    DATA_HIGH,
    DATA_LOW,
    DATA_CLOSE,
    DATA_VOLUME,
    DATA_ADJCLOSE]


ORDER_TYPE_MARKET = "market"
ORDER_BUY = "buy"
ORDER_SELL = "sell"

# BINANCE
KLINES_DATA_COLS = [DATA_DATETIME, DATA_OPEN, DATA_HIGH, DATA_LOW, DATA_CLOSE, DATA_VOLUME, "CloseTime",
                    "QuoteVolume", "Trades", "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume",
                    "ignore"]

# Polygon get_historical_data, /v2/aggs/ticker/
POLYGON_VOLUME = 'v'
POLYGON_OPEN = 'o'
POLYGON_CLOSE = 'c'
POLYGON_HIGH = 'h'
POLYGON_LOW = 'l'
POLYGON_TS = 't'
POLYGON_AGG_WINDOW = 'n'
POLYGON_SYMBOL = 'T'

POLYGON_DATA_COLS = []

# test
ENV_TEST_LEVEL = "TEST_LEVEL"
TEST_LEVEL_UNIT = "unit"
TEST_LEVEL_INTEGRATION = "integration"

# logger
LOGGER_GOQUANT = "goquant"