import logging
import time
import pandas as pd

import alpaca_trade_api as tradeapi

from config.config import TradingConfig

NY = 'America/New_York'


class AlpacaGateway(object):
    def __init__(self):
        self.cfg = TradingConfig()

        logging.basicConfig()
        logging.getLogger().setLevel(self.cfg.logging_level)

        self.api = None

    def start(self):
        self.api = tradeapi.REST(
            key_id=self.cfg.alpaca_id,
            secret_key=self.cfg.alpaca_key,
            base_url=self.cfg.alpaca_url
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
            logging.error("Orders is empty, return")
            return
        if self.api is None:
            logging.error("please run start() first")
            return

        # process the sell orders first
        sells = [o for o in orders if o.side == 'sell']
        for order in sells:
            try:
                logging.info(f'submit(sell): {order}')
                self.api.submit_order(**order.get_dict())
            except Exception as e:
                logging.error(e)
        count = wait
        while count > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                logging.info(f'all sell orders done')
                break
            logging.info(f'{len(pending)} sell orders pending...')
            time.sleep(1)
            count -= 1

        # process the buy orders next
        buys = [o for o in orders if o.side == 'buy']
        for order in buys:
            try:
                logging.info(f'submit(buy): {order}')
                self.api.submit_order(**order.get_dict())
            except Exception as e:
                logging.error(e)
        count = wait
        while count > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                logging.info(f'all buy orders done')
                break
            logging.info(f'{len(pending)} buy orders pending...')
            time.sleep(1)
            count -= 1

    def _get_prices(self, symbols, end_dt, max_workers=5):
        '''Get the map of DataFrame price data from Alpaca's data API.'''

        start_dt = end_dt - pd.Timedelta('50 days')
        start = start_dt.strftime('%Y-%m-%d')
        end = end_dt.strftime('%Y-%m-%d')

        def get_barset(symbols):
            return self.api.get_barset(
                symbols,
                'day',
                limit=50,
                start=start,
                end=end
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

    def get_prices(self, symbols):
        '''Get the map of prices in DataFrame with the symbol name key.'''
        now = pd.Timestamp.now(tz=NY)
        end_dt = now
        if now.time() >= pd.Timestamp('09:30', tz=NY).time():
            end_dt = now - \
                pd.Timedelta(now.strftime('%H:%M:%S')) - pd.Timedelta('1 minute')
        return self._get_prices(symbols, end_dt)


class AlpacaOrder(object):
    symbol = ""
    qty = ""
    side = ""
    type = ""
    time_in_force = ""

    def __init__(self, symbol, qty, side, type="market", time_in_force="day"):
        self.symbol = symbol
        self.qty = qty
        self.side = side
        self.type = type
        self.time_in_force = time_in_force

    def get_dict(self):
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "type": self.type,
            "time_in_force": self.time_in_force,
        }
