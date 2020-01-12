from airflow import DAG
from datetime import datetime, timedelta

from config.config import TradingConfig

from tasks.load_config_task import new_load_config_task
from tasks.record_bitmex_data_task import new_record_bitmex_data_task
from tasks.consume_orderbook_kafka_to_s3_task import new_consume_orderbook_kafka_to_s3_task


default_args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'start_date': datetime.today(),
    'email': ['hyu2707@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 10,
    'retry_delay': timedelta(seconds=10),
    'provide_context': True,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('master_workflow', default_args=default_args, schedule_interval=timedelta(days=1))

env = "development"
cfg = TradingConfig(config=env)

load_config_task = new_load_config_task(dag, env=env)
for symbol in cfg.bitmex_orderbook_symbols:
    record_bitmex_data_task = new_record_bitmex_data_task(dag, symbol=symbol)
    record_bitmex_data_task.set_upstream(load_config_task)

consume_orderbook_kafka_to_s3_task = new_consume_orderbook_kafka_to_s3_task(dag)
consume_orderbook_kafka_to_s3_task.set_upstream(load_config_task)
