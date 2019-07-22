"""
Example send order to IB
"""
import threading
import logging
import time

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.execution import ExecutionFilter
from ibapi.contract import Contract
from ibapi.order import Order

from config.config import TradingConfig


# ====================================================
# Public
# ====================================================
class IBGateway(object):
    ORDER_BUY = "BUY"
    ORDER_SELL = "SELL"

    def __init__(self):
        self.app = IBApp()
        self.cfg = TradingConfig()
        logging.basicConfig()
        logging.getLogger().setLevel(self.cfg.logging_level)

    def start(self):
        class IBAPIThread(threading.Thread):
            def __init__(self, IBGateway):
                threading.Thread.__init__(self)
                self.ib = IBGateway

            def run(self):
                self.ib.app.run()

        logging.info("start IBAPI connection...")
        self.app.connect(self.cfg.ib_ip, self.cfg.ib_port, clientId=self.cfg.ib_clientId)
        logging.info("connection done. serverVersion:%s connectionTime:%s" % (self.app.serverVersion(),
                                                             self.app.twsConnectionTime()))
        logging.info("start IBAPIThread...")
        t1 = IBAPIThread(self)
        t1.start()
        logging.info("wait IBAPIThread fully start...")
        while not self._is_IB_ready():
            time.sleep(0.1)
        logging.info("IBAPIThread started. run() Done.")

    def send_order(self, action, symbol, quantity):
        logging.info("sending order: action: %s, symbol: %s, quantity: %s" % (action, symbol, quantity))
        self.app.order_stock_mkt(action, symbol, quantity)

    def _is_IB_ready(self):
        return self.app.nextValidOrderId is not None


# ====================================================
# Private
# ====================================================
class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class IBWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)


class IBApp(IBWrapper, IBClient):
    def __init__(self):
        IBWrapper.__init__(self)
        IBClient.__init__(self, wrapper=self)
        self.started = False
        self.nextValidOrderId = None

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        logging.debug("NextValidId: %d", orderId)

        # we can start now
        self.start()

    def start(self):
        if self.started:
            return
        self.started = True

    def nextOrderId(self):
        oid = self.nextValidOrderId
        if oid is None:
            raise ValueError("IB not ready, nextValidId() not called.")
        self.nextValidOrderId += 1
        return oid

    def order_stock_mkt(self, action, symbol, quantity):
        # Requesting the next valid id
        # The parameter is always ignored.
        self.reqIds(-1)

        # Requesting all open orders
        self.reqAllOpenOrders()

        # Taking over orders to be submitted via TWS
        self.reqAutoOpenOrders(True)

        # Requesting this API client's orders
        self.reqOpenOrders()

        # Placing/modifying an order - remember to ALWAYS increment the
        # nextValidId after placing an order so it can be used for the next one!
        # Note if there are multiple clients connected to an account, the
        # order ID must also be greater than all order IDs returned for orders
        # to orderStatus and openOrder to this client.

        self.simplePlaceOid = self.nextOrderId()

        # build stock contract
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.currency = "USD"
        # In the API side, NASDAQ is always defined as ISLAND in the exchange field
        contract.exchange = "ISLAND"

        # build order setting
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity

        self.placeOrder(self.simplePlaceOid, contract, order)

        # Request the day's executions
        self.reqExecutions(10001, ExecutionFilter())

        # Requesting completed orders
        self.reqCompletedOrders(False)
