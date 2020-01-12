from airflow.operators.python_operator import PythonOperator
import airflow.hooks.S3_hook

from gateway.s3 import S3Gateway
import logging


def _consume_orderbook_kafka_to_s3(s3_hock, **context):
    cfg = context["ti"].xcom_pull(task_ids='config')

    logging.info("pull cfg: {}".format(cfg))
    logging.info("get S3 airflow connection")

    s3 = S3Gateway(s3_hock)
    logging.info("start to consume msg from kafka topic")
    s3.consume_orderbook_kafka_to_s3()


def new_consume_orderbook_kafka_to_s3_task(dag):
    s3_hook = airflow.hooks.S3_hook.S3Hook('my_S3_conn')
    conn = s3_hook.get_conn()
    # conn.create_bucket(Bucket="mybucket")
    # s3_hook.load_string("Content", "my_key", "mybucket")

    task = PythonOperator(
        task_id='consume_orderbook_kafka_to_s3',
        python_callable=_consume_orderbook_kafka_to_s3,
        op_kwargs={'s3_hock': s3_hook},
        dag=dag,
    )
    return task
