from airflow.operators.python_operator import PythonOperator

from config.config import TradingConfig


def _load_config_function(env, **context):
    cfg = TradingConfig(config=env)
    return cfg


def new_load_config_task(dag, env):
    task = PythonOperator(
        task_id='config',
        python_callable=_load_config_function,
        op_kwargs={'env': env},
        dag=dag,
    )
    return task
