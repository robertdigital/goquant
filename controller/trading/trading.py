import time
from datetime import datetime, timezone

from entity.constants import TRADING_BINANCE, TRADING_ALPACA
from gateway.binance import BinanceGateway
from gateway.alpaca import AlpacaGateway
from util.logger import logger


class TradingEngine(object):
    def start(self):
        raise NotImplementedError

    def trade(self, orders):
        raise NotImplementedError

    @staticmethod
    def factory(trading_platform, **kwargs):
        if trading_platform == TRADING_ALPACA:
            return TradingEngineAlpaca(**kwargs)
        if trading_platform == TRADING_BINANCE:
            return TradingEngineBinance(**kwargs)


class TradingEngineAlpaca(TradingEngine):
    def __init__(self, **kwargs):
        self.trading_wait_time = 10
        self.alpaca = AlpacaGateway()

        if kwargs['run_freq_s'] <= self.trading_wait_time:
            raise ValueError("alpaca: please set run_freq_s > trading_wait_time: {} > {}".format(
                kwargs['run_freq_s'], self.trading_wait_time))

    def start(self):
        self.alpaca.start()

    def trade(self, orders):
        self.alpaca.trade(orders, wait=self.trading_wait_time)


class TradingEngineBinance(TradingEngine):
    def __init__(self, **kwargs):
        self.binance = BinanceGateway()

    def start(self):
        self.binance.start()

    def trade(self, orders):
        self.binance.trade(orders)


class GQTrading(object):
    def __init__(self, algos, run_freq_s=30):
        self.arg = {
            "run_freq_s": run_freq_s,
        }
        # check algos
        self._preprocess_algos(algos)
        self.trading_engine = TradingEngine.factory(
            self.trading_platform, **self.arg)
        self.run_freq_s = run_freq_s
        self.algos = algos

    def _preprocess_algos(self, algos):
        if len(algos) == 0:
            raise ValueError("input algorithm is empty")

        trading_platform = None
        for algo_name in algos:
            algo = algos[algo_name]
            cur_trading_platform = algo.get_trading_platform()
            if trading_platform is None:
                trading_platform = cur_trading_platform
            elif cur_trading_platform != trading_platform:
                raise ValueError(
                    "only support one trading platform for all algorithms")
        self.trading_platform = trading_platform

    def start(self):
        self.trading_engine.start()

        counter = 0
        while True:
            start_time = time.time()
            logger.info(
                "-------count: {}, algos:{}--------".format(counter, self.algos.keys()))
            for algo in self.algos:
                self.algos[algo].prerun(t=datetime.now(timezone.utc))
                orders = self.algos[algo].run()
                logger.info(
                    "algo: {}, orders: {}".format(
                        algo, [
                            o.__dict__ for o in orders]))
                self._trade(orders)
            counter += 1
            spend_sec = time.time() - start_time
            sleep_sec = self.run_freq_s - spend_sec
            if sleep_sec < 0:
                logger.warning("algo run time + trading time > run_freq_s: {} > {}, "
                               "try to use larger run_freq_s to fix it".format(spend_sec, self.run_freq_s))
                sleep_sec = 0
            else:
                logger.info(
                    "algo run time + traing time: {}, sleep time: {}".format(spend_sec, sleep_sec))
            time.sleep(sleep_sec)

    def _trade(self, orders):
        self.trading_engine.trade(orders)
