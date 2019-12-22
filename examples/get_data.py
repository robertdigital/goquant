
from pyclient.data import GQData
from entity.constants import *

# # us stock
# minute level
gqdata = GQData()
df = gqdata.get_data(["UBER"], FREQ_MINUTE, "2019-12-20")
print(df)

# day level
gqdata = GQData()
df = gqdata.get_data(["UBER", "SPY"], FREQ_DAY, "2019-11-14")
print(df)

# bitcoin
data = Data()
df = data.get_data(symbols=["ETHBTC", "BTCUSDT"],
                 freq=FREQ_DAY,
                 start_date="2019-01-01",
                 end_date="2019-02-01",
                 datasource=DATASOURCE_BINANCE,
                 use_cache=True)
print(df)




