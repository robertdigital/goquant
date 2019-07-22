# goquant-trading
send order to different broker

## Use Guide
### IB
see `samples/ib_trading`

## Dev Setup
```bash
GOQUANT_TRADING_PATH=`pwd`
```
1. Setup IB API
https://ibkr.info/article/2484
```
cd $GOQUANT_TRADING_PATH/gateways/ib/
unzip twsapi_macunix.976.01.zip -d .
```
Follow instruction here to setup IB Workstation: http://interactivebrokers.github.io/tws-api/initial_setup.html

2. Setup python env
```bash
cd $GOQUANT_TRADING_PATH
virtualenv -p python3.7 venv_py3
source venv_py3/bin/activate
pip install -r requirements.txt
cd gateways/ib/IBJts/source/pythonclient
python setup.py install
```
