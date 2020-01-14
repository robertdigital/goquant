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
  id: ""
  key: ""
binance:
  key: ""
  secret: ""
aws:
  id: ""
  key: ""
bitmex:
  id: ""
  key: ""
service:
  airflow:
    email: ["your email"]
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
Step 4. Start workflow
```bash
make run
```

## Dev Guide: Ubuntu - AWS EC2 Ubuntu 18
1. Init instance
```bash
sudo apt update
sudo apt-get install libmysqlclient-dev
sudo apt-get install libssl-dev
sudo apt install make
sudo apt install python3
sudo apt install python3-pip
```

2. Create project python env 
```bash
make install
source env/bin/activate
```

3. Create private config in `config/priv.yaml`. Register account at different websites.
follow this format:
```yaml
alpaca:
  id: ""
  key: ""
binance:
  key: ""
  secret: ""
aws:
  id: ""
  key: ""
bitmex:
  id: ""
  key: ""
service:
  airflow:
    email: ["your email"]
```

4. Install and config mysql
```bash
sudo apt install mysql-server
sudo mysql
```
then in mysql cmd:
```bash
CREATE DATABASE airflow;
CREATE USER 'airflow'@'localhost' IDENTIFIED BY 'airflow';
GRANT ALL PRIVILEGES ON airflow. * TO 'airflow'@'localhost';
SET GLOBAL explicit_defaults_for_timestamp = 1;
```
start mysql
```bash
sudo /etc/init.d/mysql start
```

5. Config airflow
create default config:
```bash
make airflow
make airflow-stop
```
modify `airflow/airflow.cfg`, change those lines:
```bash
executor = LocalExecutor
sql_alchemy_conn = mysql://airflow:airflow@localhost:3306/airflow
```

6. Install Kafka
```bash
sudo apt install default-jre
wget http://ftp.wayne.edu/apache/kafka/2.4.0/kafka_2.12-2.4.0.tgz -O kafka.tgz 
mv kafka_2.12-2.4.0 kafka
```
start kafka
```bash
setsid nohup ./kafka/bin/zookeeper-server-start.sh kafka/config/zookeeper.properties &
setsid nohup ./kafka/bin/kafka-server-start.sh kafka/config/server.properties &
```
create kafka topics:
```bash
./kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic bitmex_orderbook
```

7. Run!
```bash
setsid nohup make airflow &
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

