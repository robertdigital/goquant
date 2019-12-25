"""
Example of SP500 buy dip
"""
from datetime import datetime, timedelta

# from entity.order import Order
from pyclient import GQAlgo, GQOrder
from pyclient.constants import *
from util.logger import logger

# SP500
Universe = ['MMM', 'ABT', 'ABBV', 'ACN', 'ATVI']  # noqa

'''
# SP100
# python -c "import requests; import re; print( sorted(line.split('\"')[1] for line in re.findall('\[\"[A-Z]+\",', requests.get('http://www.nasdaq.com/quotes/nasdaq-100-stocks.aspx').text)))"
Universe = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO', 'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX', 'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX', 'FOXA', 'GILD', 'GOOG', 'GOOGL', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD', 'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL', 'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG', 'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA', 'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']
'''  # noqa


class AlgoBuySPYDip(GQAlgo):
    def init(self):
        self.position_size = 100
        self.max_positions = 5

    def run(self):
        '''Calculate the scores within the universe to build the optimal
        portfolio as of today, and extract orders to transition from our
        current portfolio to the desired state.
        '''

        # get data
        interval = timedelta(days=7)
        price_dict = self.algo_get_data(symbols=Universe,
                                        freq=FREQ_DAY,
                                        interval_timedelta=interval)

        # rank the stocks based on the indicators.
        ranked = self._calc_scores(price_dict)
        to_buy = set()
        to_sell = set()
        # take the top one 2th out of ranking,
        # excluding stocks too expensive to buy a share
        for symbol, _ in ranked[:len(ranked)//2]:
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
            shares = positions[symbol]["qty"]
            orders.append(GQOrder(symbol=symbol, qty=shares, side='sell'))
            logger.info(f'order(sell): {symbol} for {shares}')

        # likewise, if the portfoio is missing stocks from the
        # desired portfolio, buy them. We sent a limit for the total
        # position size so that we don't end up holding too many positions.
        max_to_buy = self.max_positions - (len(positions) - len(to_sell))
        for symbol in to_buy:
            if max_to_buy <= 0:
                break
            shares = self.position_size // float(price_dict[symbol].Close.values[-1])
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
        param = 2
        for symbol in price_dict:
            df = price_dict[symbol]
            if len(df.Close.values) <= param:
                continue
            ema = df.Close.ewm(span=param).mean()[dayindex]
            last = df.Close.values[dayindex]
            diff = (last - ema) / last
            diffs[symbol] = diff
        return sorted(diffs.items(), key=lambda x: x[1])
