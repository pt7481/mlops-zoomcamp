import pandas as pd
import boto3
from botocore.exceptions import ClientError

S3_BUCKET = "thoughtswork-co"
S3_PREFIX = "ml_pipelines/mlops_zoomcamp"
RAW_FOLDER = "raw"

def s3_object_exists(s3_client, bucket_name, key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise

def download_trip_data(color, year, month, logical_date, **context):
    year = int(year)
    month = int(month)
    training_data_url=f"https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{year}-{month:02d}.parquet"
    train_df = pd.read_parquet(training_data_url)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    validation_data_url=f"https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{next_year}-{next_month:02d}.parquet"
    val_df = pd.read_parquet(validation_data_url)

    def save_trip_data_to_s3(s3_key_suffix, df, color, year, month, logical_date, **context):
        s3_client = boto3.client("s3")
        run_date_str = logical_date.strftime("%Y-%m-%d")
        key = f"{S3_PREFIX}/{run_date_str}/{RAW_FOLDER}/{s3_key_suffix}_{color}_tripdata_{year}-{month:02d}.parquet"

        if not s3_object_exists(s3_client, S3_BUCKET, key):
            print(f"Uploading {key} to S3 bucket {S3_BUCKET}")
            s3_client.put_object(Bucket=S3_BUCKET, Key=key, Body=df.to_parquet(index=False))
        else:
            print(f"{key} already exists in S3 bucket {S3_BUCKET}")

        context['ti'].xcom_push(key=f'{s3_key_suffix}_s3_key', value=key)

    save_trip_data_to_s3("train", train_df, color, year, month, logical_date, **context)
    save_trip_data_to_s3("val", val_df, color, next_year, next_month, logical_date, **context)
