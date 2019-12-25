[![codecov](https://codecov.io/gh/hyu2707/goquant/branch/master/graph/badge.svg)](https://codecov.io/gh/hyu2707/goquant)
![](https://github.com/hyu2707/goquant/workflows/.github/workflows/pythonapp.yml/badge.svg)
# goquant trading system
Lightweight end-to-end trading system for US stock and crypto. Support market data, algorithm development and backtesting, live and paper trading. 

## Current Status

```diff
+ [data] US stock: Polygon, minute-level, 2015 to now
+ [backtest] PyAlgoTrade, stock
+ [paperTrading] US stock: Alpaca
+ [liveTrading] US stock: Alpaca

+ [data] crypto: Binance, minute-level, last 3 month
+ [backtest] PyAlgoTrade, crypto
- [paperTrading] crypto: Bitmex
+ [liveTrading] crypto: Binance

- [data] CN data source: None
+ [backtest] PyAlgoTrade, stock
- [paperTrading] CN stock: None
- [liveTrading] CN stock: None
```

## Use Guide
Step 1. Create private config in `config/priv.yaml`
register free account in Alpaca
follow this format:
```
alpaca:
  id: "<YOUR_ID>"
  key: "<YOUR_KEY>"
binance:
  key: "<YOUR_API_KEY>"
  secret: "<YOUR_API_SECRET_KEY>"
```
Step 2. Build env
```
make install
```
then activate env:
```bash
source env/bin/activate
```
Step 3. Check tests

unittest (fast)
```bash
make test
```
full test (slow), it contains integration test, run it before submit code
```bash
make test_all
```

## Dev Guide
### Test
```bash
make test
```
### Lint
```bash
make lint
```

### Jupyter Notebook env
```bash
make research
```

