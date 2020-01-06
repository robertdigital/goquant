from airflow.operators.python_operator import PythonOperator

from gateway.bitmex import BitmexGateway
import logging


def _record_bitmex_data(symbols, **context):
    cfg = context["ti"].xcom_pull(task_ids='config')

    logging.info("pull cfg: {}".format(cfg))
    bitmex = BitmexGateway()
    bitmex.record_bitmex_order_book(symbols[0])


def new_record_bitmex_data_task(dag, symbols):
    task = PythonOperator(
        task_id='record_bitmex_data',
        python_callable=_record_bitmex_data,
        op_kwargs={'symbols': symbols},
        dag=dag,
    )
    return task
