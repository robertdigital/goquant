"""
official api: https://github.com/alpacahq/alpaca-trade-api-python/
alpaca account can use polygon.io account
https://polygon.io/docs/#getting-started
"""
import time
from deprecated.sphinx import deprecated

import alpaca_trade_api as tradeapi

from config.config import TradingConfig
from util.logger import logger


class AlpacaGateway(object):
    def __init__(self):
        self.cfg = TradingConfig()
        self.api = None

    def start(self):
        self.api = tradeapi.REST(
            key_id=self.cfg.alpaca_id,
            secret_key=self.cfg.alpaca_key,
            base_url=self.cfg.alpaca_url,
            api_version='v2'
        )
        pass

    def trade(self, orders: list, wait=30):
        '''
        This is where we actually submit the orders and wait for them to fill.
        Waiting is an important step since the orders aren't filled automatically,
        which means if your buys happen to come before your sells have filled,
        the buy orders will be bounced. In order to make the transition smooth,
        we sell first and wait for all the sell orders to fill before submitting
        our buy orders.
        '''

        if len(orders) == 0:
            logger.error("Orders is empty, return")
            return
        if self.api is None:
            logger.error("please run start() first")
            return

        # process the sell orders first
        sells = [o for o in orders if o.side == 'sell']
        for order in sells:
            try:
                logger.info(f'submit(sell): {order.get_dict()}')
                self.api.submit_order(**order.get_dict())
            except Exception as e:
                logger.error(e)
        wait = wait // 2  # both sell and buy
        count = wait
        while count > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                logger.info(f'all sell orders done')
                break
            logger.info(
                f'{len(pending)} sell orders pending... wait time {count}')
            logger.debug("pending orders detail: {}".format(
                [p.__dict__ for p in pending]))
            time.sleep(1)
            count -= 1

        # process the buy orders next
        buys = [o for o in orders if o.side == 'buy']
        for order in buys:
            try:
                logger.info(f'submit(buy): {order.get_dict()}')
                self.api.submit_order(**order.get_dict())
            except Exception as e:
                logger.error(e)
        count = wait
        while count > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                logger.info(f'all buy orders done')
                break
            logger.info(
                f'{len(pending)} buy orders pending... wait time {count}')
            logger.debug("pending orders detail: {}".format(
                [p.__dict__ for p in pending]))
            time.sleep(1)
            count -= 1

    @deprecated(
        reason="alpaca data function has data limit, please use polygon data interface")
    def get_prices(self, symbols, freq='day', length=50):
        def get_barset(symbols):
            return self.api.get_barset(
                symbols,
                freq,
                limit=length
            )

        # The maximum number of symbols we can request at once is 200.
        barset = None
        idx = 0
        while idx <= len(symbols) - 1:
            if barset is None:
                barset = get_barset(symbols[idx:idx + 200])
            else:
                barset.update(get_barset(symbols[idx:idx + 200]))
            idx += 200

        return barset.df
