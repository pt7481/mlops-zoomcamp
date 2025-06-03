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

def download_trip_data(color, year, month, execution_date, **context):
    url=f"https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{year}-{month:02d}.parquet"
    df = pd.read_parquet(url)

    s3_client = boto3.client("s3")
    run_date_str = execution_date.strftime("%Y-%m-%d")
    key = f"{S3_PREFIX}/{run_date_str}/{RAW_FOLDER}/{color}_tripdata_{year}-{month:02d}.parquet"

    if not s3_object_exists(s3_client, S3_BUCKET, key):
        print(f"Uploading {key} to S3 bucket {S3_BUCKET}")
        s3_client.put_object(Bucket=S3_BUCKET, Key=key, Body=df.to_parquet(index=False))
    else:
        print(f"{key} already exists in S3 bucket {S3_BUCKET}")

    context['ti'].xcom_push(key='trip_data_s3_key', value=key)
