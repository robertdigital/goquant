import time

from gateway.alpaca import AlpacaGateway
from util.logger import logger


class Trading(object):
    def __init__(self, run_freq_s=1, algos={}):
        self.alpaca = AlpacaGateway()
        self.run_freq_s = run_freq_s
        self.algos = algos

    def start(self):
        done = None
        self.alpaca.start()

        logger.info('init algo')
        for algo in self.algos:
            self.algos[algo].init()

        counter = 0
        while True:
            clock = self.alpaca.api.get_clock()
            now = clock.timestamp
            logger.info("count: {}, now: {}, algos:{}".format(counter, now, self.algos.keys()))
            for algo in self.algos:
                orders = self.algos[algo].run()
                logger.info("algo: {}, orders: {}".format(algo, orders))
                self._trade(orders)
            time.sleep(self.run_freq_s)

    def _trade(self, orders):
        self.alpaca.trade(orders)
