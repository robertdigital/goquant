from airflow.operators.python_operator import PythonOperator
from gateway.s3 import S3Gateway
import logging


def _consume_orderbook_kafka_to_s3(**context):
    logging.info("get S3 airflow connection")
    s3 = S3Gateway()
    logging.info("start to consume msg from kafka topic")
    s3.consume_orderbook_kafka_to_s3()


def new_consume_orderbook_kafka_to_s3_task(dag):
    task = PythonOperator(
        task_id='consume_bitmex_orderbook_kafka_to_s3',
        python_callable=_consume_orderbook_kafka_to_s3,
        dag=dag,
    )
    return task
