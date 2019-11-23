from controller.trading.account import Account


class BaseAlgo(object):
    def __init__(self):
        self.account = Account()

    def init(self):
        pass

    def run(self)->[list]:
        pass
