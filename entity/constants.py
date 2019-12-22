
TIME_FMT = "%Y-%m-%dT%H:%M:%S%z"

DATASOURCE_ALPACA = 'alpaca'
DATASOURCE_BINANCE = 'binance'
DATASOURCE_CACHE = 'cache'
FREQ_DAY = 'day'
FREQ_MINUTE = 'minute'

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
DATA_HISTORICAL_COLS = [DATA_SYMBOL, DATA_OPEN, DATA_HIGH, DATA_LOW, DATA_CLOSE, DATA_VOLUME, DATA_ADJCLOSE]


ORDER_TYPE_MARKET = "market"
ORDER_BUY = "buy"
ORDER_SELL = "sell"

# BINANCE
KLINES_DATA_COLS = [DATA_DATETIME, DATA_OPEN, DATA_HIGH, DATA_LOW, DATA_CLOSE, DATA_VOLUME, "CloseTime",
                    "QuoteVolume", "Trades", "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume",
                    "ignore"]
