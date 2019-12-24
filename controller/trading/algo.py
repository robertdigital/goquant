from controller.trading.account import get_account_class


class GQAlgo(object):
    def __init__(self, trading_platform):
        self.trading_platform = trading_platform
        self.account = get_account_class(trading_platform)

    def get_trading_platform(self):
        return self.trading_platform

    def init(self):
        pass

    def run(self) -> [list]:
        raise NotImplementedError

    def get_cash(self):
        """
        get current cash in USD
        :return:
        """
        return self.account.get_cash()

    def get_positions(self):
        """
        get current positions
        :return:
        """
        return self.account.get_positions()
