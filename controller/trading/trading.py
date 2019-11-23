import time

from gateway.alpaca import AlpacaGateway
from util.logger import logger


class Trading(object):
    def __init__(self, run_freq_s=30, algos={}, trading_wait_time=10):
        self.alpaca = AlpacaGateway()
        self.run_freq_s = run_freq_s
        self.algos = algos
        self.wait_time = trading_wait_time
        if run_freq_s <= self.wait_time:
            raise ValueError("please set run_freq_s > trading_wait_time: {} > {}".format(
                run_freq_s, self.wait_time))

    def start(self):
        self.alpaca.start()

        logger.info('init algo')
        for algo in self.algos:
            self.algos[algo].init()

        counter = 0
        while True:
            start_time = time.time()
            clock = self.alpaca.api.get_clock()
            now = clock.timestamp
            logger.info("-------count: {}, now: {}, algos:{}--------".format(counter, now, self.algos.keys()))
            for algo in self.algos:
                orders = self.algos[algo].run()
                logger.info("algo: {}, orders: {}".format(algo, [o.__dict__ for o in orders]))
                self._trade(orders)
            counter += 1
            spend_sec = time.time() - start_time
            sleep_sec = self.run_freq_s - spend_sec
            if sleep_sec < 0:
                logger.warning("algo run time + trading time > run_freq_s: {} > {}, "
                               "try to use larger run_freq_s to fix it".format(spend_sec, self.run_freq_s))
                sleep_sec = 0
            else:
                logger.info("algo run time + traing time: {}, sleep time: {}".format(spend_sec, sleep_sec))
            time.sleep(sleep_sec)

    def _trade(self, orders):
        self.alpaca.trade(orders, wait=self.wait_time)
