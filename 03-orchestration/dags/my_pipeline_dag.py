from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators import PythonOperator

from my_pipeline import download_trip_data
from my_pipeline import preprocess_data
from my_pipeline import train_model

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="nyc_taxi_ml_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 6, 1),
    schedule_interval=None,  # Trigger manually or via API, passing color/year/month in dag_run.conf
    catchup=False,
) as dag:

    # 1) Ingest task: download train+val Parquet into S3, push XCom keys "train_s3_key" and "val_s3_key"
    ingest = PythonOperator(
        task_id="download_trip_data",
        python_callable=download_trip_data,
        op_kwargs={
            "color": "{{ dag_run.conf['color'] }}",
            "year": "{{ dag_run.conf['year'] }}",
            "month": "{{ dag_run.conf['month'] }}",
        },
        provide_context=True,
    )

    # 2) Preprocess training data: fits a new DictVectorizer, transforms train dicts, saves DV and (X,y).npz for train
    preprocess_train = PythonOperator(
        task_id="preprocess_data_train",
        python_callable=preprocess_data,
        op_kwargs={"training_data": True},
        provide_context=True,
    )

    # 3) Preprocess validation data: loads DV from train, transforms val dicts, saves (X,y).npz for val
    preprocess_val = PythonOperator(
        task_id="preprocess_data_val",
        python_callable=preprocess_data,
        op_kwargs={"training_data": False},
        provide_context=True,
    )

    # 4) Train task: load processed train/val NPZ from XCom, train XGBoost, log metrics to MLflow
    train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
        provide_context=True,
    )

    # DAG dependencies: ingest → preprocess_train → preprocess_val → train
    ingest >> preprocess_train >> preprocess_val >> train
