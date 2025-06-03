from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from my_pipeline.ingest   import download_trip_data
from my_pipeline.preprocess import preprocess_data
from my_pipeline.train    import train_model

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
    catchup=False,
    schedule="@monthly",
    params={  
        "color": "green",
        "year": 2021,
        "month": 1
    }
) as dag:

    # 1) Ingest task: download train+val Parquet into S3, push XCom keys "train_s3_key" and "val_s3_key"
    ingest = PythonOperator(
        task_id="download_trip_data",
        python_callable=download_trip_data,
        op_kwargs={
            "color": "{{ params.color }}",
            "year": "{{ params.year }}",
            "month": "{{ params.month }}",
        }
    )

    # 2) Preprocess training data: fits a new DictVectorizer, transforms train dicts, saves DV and (X,y).npz for train
    preprocess_train = PythonOperator(
        task_id="preprocess_data_train",
        python_callable=preprocess_data,
        op_kwargs={"training_data": True}
    )

    # 3) Preprocess validation data: loads DV from train, transforms val dicts, saves (X,y).npz for val
    preprocess_val = PythonOperator(
        task_id="preprocess_data_val",
        python_callable=preprocess_data,
        op_kwargs={"training_data": False}
    )

    # 4) Train task: load processed train/val NPZ from XCom, train XGBoost, log metrics to MLflow
    train = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )

    # DAG dependencies: ingest → preprocess_train → preprocess_val → train
    ingest >> preprocess_train >> preprocess_val >> train
