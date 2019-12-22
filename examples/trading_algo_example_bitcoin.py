"""
Example of SP500 buy dip
"""
from datetime import datetime, timedelta, timezone

# from entity.order import Order
from pyclient.data import GQData
from pyclient.trading import GQAlgo, GQOrder
from pyclient.trading import GQTrading
from entity.constants import *
from util.logger import logger

Universe = ['BTCUSDT', 'ETHUSDT']


class AlgoBuySPYDip(GQAlgo):
    def init(self):
        self.position_size = 1000
        self.max_positions = 5
        self.data = GQData()

    def run(self):
        '''Calculate the scores within the universe to build the optimal
        portfolio as of today, and extract orders to transition from our
        current portfolio to the desired state.
        '''

        # get data
        start_date = datetime.today() - timedelta(days=50)
        price_dict = self.data.historical_data(symbols=Universe,
                                  freq=FREQ_DAY,
                                  start_date=start_date,
                                  end_date=datetime.now(timezone.utc),
                                  datasource=DATASOURCE_BINANCE,
                                               dict_output=True)

        # rank the stocks based on the indicators.
        ranked = self._calc_scores(price_dict)
        to_buy = set()
        to_sell = set()
        # take the top one twentieth out of ranking,
        # excluding stocks too expensive to buy a share
        for symbol, _ in ranked[:1]:
            price = float(price_dict[symbol].Close.values[-1])
            if price > float(self.get_cash()):
                continue
            to_buy.add(symbol)

        # now get the current positions and see what to buy,
        # what to sell to transition to today's desired portfolio.
        positions = self.get_positions()
        logger.info(positions)
        holding_symbol = set(positions.keys())
        to_sell = holding_symbol - to_buy
        to_buy = to_buy - holding_symbol
        orders = []

        # if a stock is in the portfolio, and not in the desired
        # portfolio, sell it
        for symbol in to_sell:
            shares = positions[symbol].qty
            orders.append(GQOrder(symbol=symbol, qty=shares, side='sell'))
            logger.info(f'order(sell): {symbol} for {shares}')

        # likewise, if the portfoio is missing stocks from the
        # desired portfolio, buy them. We sent a limit for the total
        # position size so that we don't end up holding too many positions.
        max_to_buy = self.max_positions - (len(positions) - len(to_sell))
        for symbol in to_buy:
            if max_to_buy <= 0:
                break
            # support fractional share for bitcoin
            shares = self.position_size / float(price_dict[symbol].Close.values[-1])
            if shares == 0.0:
                continue
            orders.append(GQOrder(symbol=symbol, qty=shares, side='buy'))
            logger.info(f'order(buy): {symbol} for {shares}')
            max_to_buy -= 1
        return orders

    def _calc_scores(self, price_dict, dayindex=-1):
        '''Calculate scores based on the indicator and
        return the sorted result.
        '''
        diffs = {}
        param = 10
        for symbol in price_dict:
            df = price_dict[symbol]
            if len(df.Close.values) <= param:
                continue
            ema = df.Close.ewm(span=param).mean()[dayindex]
            last = df.Close.values[dayindex]
            diff = (last - ema) / last
            diffs[symbol] = diff
        return sorted(diffs.items(), key=lambda x: x[1])


if __name__ == "__main__":
    trading_platform = TRADING_BINANCE
    trade = GQTrading(
        trading_platform=trading_platform,
        run_freq_s=600000,
        algos={
            "AlgoBuySPYDip": AlgoBuySPYDip(trading_platform)
        })
    trade.start()
