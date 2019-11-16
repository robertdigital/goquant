from gateway.alpaca import AlpacaGateway


class Account(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()
        self.alpaca.start()

    def get_cash(self):
        account = self.alpaca.api.get_account()
        return account.cash

    def get_positions(self):
        return self.alpaca.api.list_positions()
