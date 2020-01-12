from airflow.operators.python_operator import PythonOperator

from gateway.bitmex import BitmexGateway
import logging


def _record_bitmex_data(symbol, **context):
    cfg = context["ti"].xcom_pull(task_ids='config')

    logging.info("pull cfg: {}".format(cfg))
    bitmex = BitmexGateway()
    bitmex.produce_orderbook_to_kafka(symbol)


def new_record_bitmex_data_task(dag, symbol):
    task = PythonOperator(
        task_id='record_bitmex_data_{}'.format(symbol),
        python_callable=_record_bitmex_data,
        op_kwargs={'symbol': symbol},
        dag=dag,
    )
    return task
