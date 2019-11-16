"""
Example send order to IB
"""
import threading
import time

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.execution import ExecutionFilter
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import RealTimeBar

from config.config import TradingConfig
from util.logger import logger


# ====================================================
# Public
# ====================================================
class IBGateway(object):
    ORDER_BUY = "BUY"
    ORDER_SELL = "SELL"

    def __init__(self):
        self.app = IBApp()
        self.cfg = TradingConfig()

    def start(self):
        class IBAPIThread(threading.Thread):
            def __init__(self, IBGateway):
                threading.Thread.__init__(self)
                self.ib = IBGateway

            def run(self):
                self.ib.app.run()

        logger.info("start IBAPI connection...")
        self.app.connect(
            self.cfg.ib_ip,
            self.cfg.ib_port,
            clientId=self.cfg.ib_clientId)
        logger.info("connection done. serverVersion:%s connectionTime:%s" % (self.app.serverVersion(),
                                                                             self.app.twsConnectionTime()))
        logger.info("start IBAPIThread...")
        t1 = IBAPIThread(self)
        t1.start()
        logger.info("wait IBAPIThread fully start...")
        while not self._is_IB_ready():
            time.sleep(0.1)
        logger.info("IBAPIThread started. run() Done.")

    def send_order(self, contract: Contract, order: Order):
        logger.info(
            "sending order: action: %s, symbol: %s, quantity: %s" %
            (order.action, contract.symbol, order.totalQuantity))
        self.app.orderOperations_req(contract, order)

    def gen_contract(self, symbol, secType="STK",
                     currency="USD", exchange="ISLAND"):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.currency = currency
        # In the API side, NASDAQ is always defined as ISLAND in the exchange
        # field
        contract.exchange = exchange
        return contract

    def gen_order(self, action, quantity, orderType="MKT"):
        # build order setting
        order = Order()
        order.action = action
        order.orderType = orderType
        order.totalQuantity = quantity
        return order

    def get_realtime_bar(self, contract: Contract,
                         whatToShow="MIDPOINT", useRTH=True):
        logger.info("send realtime bar request...")
        id = self.app.realTimeBarsOperations_req(contract, whatToShow, useRTH)
        logger.info(
            "waiting for realtime bar request results, request id: %d" %
            id)
        while not self._id_IB_get_realtime_data(id):
            time.sleep(0.1)
        return self.app.realtimeData[id]

    # ===== private

    def _is_IB_ready(self):
        return self.app.nextValidOrderId is not None

    def _id_IB_get_realtime_data(self, reqId):
        return reqId in self.app.realtimeData


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
        self.nextValidTickerId = 0
        self.realtimeData = {}  # tickerid -> bardata

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logger.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        logger.debug("NextValidId: %d", orderId)

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

    def nextTickerId(self):
        oid = self.nextValidTickerId
        self.nextValidTickerId += 1
        return oid

    def orderOperations_req(self, contract: Contract, order: Order):
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

        self.placeOrder(self.simplePlaceOid, contract, order)

        # Request the day's executions
        self.reqExecutions(10001, ExecutionFilter())

        # Requesting completed orders
        self.reqCompletedOrders(False)

    def realTimeBarsOperations_req(
            self, contract: Contract, whatToShow="MIDPOINT", useRTH=True):
        tickerId = self.nextTickerId()
        # send request
        self.reqRealTimeBars(tickerId, contract, 5, whatToShow, useRTH, [])
        return tickerId

    def realtimeBar(self, reqId: int, time: int, open_: float, high: float, low: float, close: float,
                    volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        bar = RealTimeBar(time, -1, open_, high, low,
                          close, volume, wap, count)
        logger.info("RealTimeBar. TickerId:", reqId, bar)
        self.realtimeData[reqId] = bar
