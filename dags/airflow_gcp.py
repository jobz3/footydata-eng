
from airflow import DAG
from datetime import datetime
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
import kagglehub
import os


def download_dataset():
    path = kagglehub.dataset_download("marcohuiii/english-premier-league-epl-match-data-2000-2025")
    csv_file = [f for f in os.listdir(path) if f.endswith('.csv')][0]
    return os.path.join(path, csv_file)

with DAG(
    dag_id='upload_data_gcp_task',
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    download_task = PythonOperator(
        task_id="download_kaggle_dataset",
        python_callable=download_dataset,
    )

    upload_task = LocalFilesystemToGCSOperator(
        task_id="upload_task",
        gcp_conn_id="google_cloud_default",
        src="{{ ti.xcom_pull(task_ids='download_kaggle_dataset') }}",
        dst="epl_data.csv",
        bucket="dbt-demo-bucket",
    )

    download_task >> upload_task