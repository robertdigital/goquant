from gateway.alpaca import AlpacaGateway
from util.logger import logger

class Data(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.alpaca.start()

    def get_prices(self, symbols, freq, length):
        """
        get price to today
        :param symbols:
        :param length:
        :param freq:
        :return:
        """
        data_df = self.alpaca.get_prices(symbols=symbols,
                                         freq=freq,
                                         length=length)
        if data_df.empty:
            logger.error("data get_price return empty")
            return
        else:
            logger.debug("get number of data shape: " + str(data_df.shape))
        return data_df

data = Data()