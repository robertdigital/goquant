[![codecov](https://codecov.io/gh/hyu2707/goquant/branch/master/graph/badge.svg)](https://codecov.io/gh/hyu2707/goquant)
![](https://github.com/hyu2707/goquant/workflows/.github/workflows/pythonapp.yml/badge.svg)
# goquant-trading
Send order to different broker. (Support IB, Alpaca and Binance right now)

## Current Status
```diff
+ US stock data source: Polygon
+ US stock trading platform: Alpaca
+ US Bitcoin data source: Binance (last 3 month)
+ US Bitcoin trading platform: Binance
- CN data source: None
- CN trading platfoorm: None
```


## Use Guide
Step 1. Create private config in `config/priv.yaml`
register free account in Alpaca
follow this format:
```
alpaca:
  id: "<YOUR_ID>"
  key: "<YOUR_KEY>"
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

