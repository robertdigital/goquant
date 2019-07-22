"""
Example send order to IB
"""
from gateways.ib_gateway import IBGateway

ib = IBGateway()
ib.start()
ib.send_order(ib.ORDER_BUY, "AMD", 1)
