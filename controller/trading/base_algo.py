from controller.data.data import Data
from controller.trading.account import Account


class BaseAlgo(object):
    def __init__(self):
        self.data = Data()
        self.account = Account()

    def init(self):
        pass

    def start(self):
        pass
