"""
Example about how to use data interface
"""
from handler.goquantdata import GoquantData

symbols = ["SPY", "VTI", "VEU", "IEF", "VNQ", "DBC"]

gq_data = GoquantData()
data_dict = gq_data.get_data(symbols=symbols,
                 freq='day',
                 start_date='2019-10-01',
                             savecsv_path='raw_data')
print(data_dict["SPY"].to_string())
