"""
Example send order to IB
"""
from gateways.ib_gateway import IBGateway
from ibapi.common import RealTimeBar

# start IB connection
ib = IBGateway()
ib.start()

# send order to IB
contract = ib.gen_contract("AMD")
order = ib.gen_order("BUY", 1)
ib.send_order(contract, order)

# get real-time market data
contract2 = ib.gen_contract("UBER")
bar = ib.get_realtime_bar(contract2)
print(bar)



