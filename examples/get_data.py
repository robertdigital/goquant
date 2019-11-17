
from controller.data.data import Data
from entity.constants import *

# minute level
data = Data()
df = data.get_data(["UBER"], FREQ_MINUTE, "2019-11-14")
print(df)

# day level
data = Data()
df = data.get_data(["UBER", "SPY"], FREQ_DAY, "2019-11-14")
print(df)


