import time

from gateway.alpaca import AlpacaGateway
from util.logger import logger
from algo.buy_spy_dip import AlgoBuySPYDip


class Trading(object):
    def __init__(self):
        self.alpaca = AlpacaGateway()

    def start(self):
        done = None
        self.alpaca.start()
        logger.info('start running')
        algo_list = self._load_algo()

        logger.info('init algo')
        for algo in algo_list:
            algo.init()

        while True:
            # clock API returns the server time including
            # the boolean flag for market open
            clock = self.alpaca.api.get_clock()
            now = clock.timestamp
            if done != now.strftime('%Y-%m-%d'):
                for algo in algo_list:
                    orders = algo.start()
                    self._trade(orders)

                    # flag it as done so it doesn't work again for the day
                    # TODO: this isn't tolerant to process restarts, so this
                    # flag should probably be saved on disk
                    done = now.strftime('%Y-%m-%d')
                    logger.info(f'done for {done}')
            time.sleep(1)

    def _trade(self, orders):
        self.alpaca.trade(orders)

    def _load_algo(self):
        logger.info("loading algo")
        algo_list = []
        algo = AlgoBuySPYDip()
        algo_list.append(algo)
        return algo_list
