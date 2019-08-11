# goquant-trading
Send order to different broker. (Support IB and Alpaca right now)
For project progress please see: https://github.com/hyu2707/goquant-trading/projects/2

## Use Guide
### IB
see `algo/ib_trading`
### Alpaca
see `algo/buy_spy_dip.py`

## Dev Setup
```bash
GOQUANT_TRADING_PATH=`pwd`
```
0. (For IB user) Setup IB API
https://ibkr.info/article/2484
```
cd $GOQUANT_TRADING_PATH/gateways/ib/
unzip twsapi_macunix.976.01.zip -d .
```
Follow instruction here to setup IB Workstation: http://interactivebrokers.github.io/tws-api/initial_setup.html

1. Setup python env
```bash
cd $GOQUANT_TRADING_PATH
virtualenv -p python3.7 venv_py3
source venv_py3/bin/activate
pip install -r requirements.txt
ipython kernel install --user --name=goquant
cd gateways/ib/IBJts/source/pythonclient
python setup.py install
```

## Dev Guide
### Framework
