[![codecov](https://codecov.io/gh/hyu2707/goquant/branch/master/graph/badge.svg)](https://codecov.io/gh/hyu2707/goquant)
![](https://github.com/hyu2707/goquant/workflows/.github/workflows/pythonapp.yml/badge.svg)
# goquant trading system
Lightweight end-to-end trading system for US stock and crypto. Support market data, algorithm development and backtesting, live and paper trading. 

## Current Status
### Data Source
```diff
+ US stock: Polygon, minute-level, 2015 to now
+ US crypto: Binance, minute-level, last 3 month
- CN data source: None
```
### Backtest
based on pyalgotrade
```diff
+ stock
+ crypto
```
### Live Trading Platform
```diff
+ US stock: Alpaca
+ US crypto: Binance
- CN stock: None
```
### Paper Trading Platform
based on pyalgotrade
```diff
+ US stock: Alpaca
- US crypto: Bitmex
- CN stock: None
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

