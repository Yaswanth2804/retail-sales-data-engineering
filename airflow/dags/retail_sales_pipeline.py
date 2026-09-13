from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="retail_sales_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["retail", "data-engineering"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command="python /opt/scripts/generate_retail_data.py",
    )

    upload_to_s3 = BashOperator(
        task_id="upload_to_s3",
        bash_command="python /opt/scripts/upload_to_s3.py",
    )

    load_snowflake = BashOperator(
        task_id="load_snowflake",
        bash_command="python /opt/scripts/load_snowflake.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/dbt/retail_sales_dbt && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/dbt/retail_sales_dbt && dbt test",
    )

    generate_data >> upload_to_s3 >> load_snowflake >> dbt_run >> dbt_test