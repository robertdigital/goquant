from controller.trading.account import get_account_class


class BaseAlgo(object):
    def __init__(self, trading_platform):
        self.account = get_account_class(trading_platform)

    def init(self):
        pass

    def run(self) -> [list]:
        pass
