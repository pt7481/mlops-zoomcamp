import boto3
import pickle
import pandas as pd
from sklearn.feature_extraction import DictVectorizer

S3_BUCKET = "thoughtswork-co"
S3_PREFIX = "ml_pipelines/mlops_zoomcamp"
PROCESSED_FOLDER = "processed"

DOWNLOAD_TASK_ID = 'download_trip_data'
TRIP_DATA_S3_KEY = 'trip_data_s3_key'
PREPROCESS_DATA_TASK_ID = 'preprocess_data'
DV_S3_KEY = 'dv_s3_key'
PROCESSED_DATA_S3_KEY = 'processed_data_s3_key'

def preprocess_data(execution_date, fit_dv, **context):
    run_date_str = execution_date.strftime("%Y-%m-%d")

    # Obtain the raw trip data from S3
    ti = context['ti']
    s3_client = boto3.client("s3")
    key = ti.xcom_pull(task_ids=DOWNLOAD_TASK_ID, key=TRIP_DATA_S3_KEY)
    trip_data_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    df = pd.read_parquet(trip_data_obj['Body'])

    ### Preprocess the data

    # Create new duration field (target), filter trips to durations >= 1 and <= 60 minutes
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    # Create feature PU_DO by concatenating PULocationID and DOLocationID
    df['PU_DO'] = df['PULocationID'].astype(str) + '_' + df['DOLocationID'].astype(str)

    # Create feature dictionary and vectorize it
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    if fit_dv:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)

        # Persist DV to central storage for future use
        dv_key = f"{S3_PREFIX}/{run_date_str}/{PROCESSED_FOLDER}/dv_{run_date_str}.pkl"
        dv_bytes = pickle.dumps(dv)
        s3_client.put_object(Bucket=S3_BUCKET, Key=dv_key, Body=dv_bytes)
        print(f"DictVectorizer saved to S3 at {dv_key}")
        ti.xcom_push(key=DV_S3_KEY, value=dv_key)
    else:

        # Load the existing DictVectorizer from S3
        dv_key = ti.xcom_pull(task_ids=PREPROCESS_DATA_TASK_ID, key=DV_S3_KEY)
        dv_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=dv_key)
        dv_bytes = dv_obj['Body'].read()
        dv = pickle.loads(dv_bytes)
        print(f"DictVectorizer loaded from S3 at {dv_key}")
        
        # Transform the data using the loaded DictVectorizer
        X = dv.transform(dicts)

    # Persist the processed data to S3
    processed_key = f"{S3_PREFIX}/{run_date_str}/{PROCESSED_FOLDER}/tripdata_{run_date_str}.parquet"
    bytes_io = df.to_parquet(index=False)
    s3_client.put_object(Bucket=S3_BUCKET, Key=processed_key, Body=bytes_io)
    print(f"Processed data saved to S3 at {processed_key}")

    # Push the DictVectorizer and processed data keys to XCom for downstream tasks
    ti.xcom_push(key=DV_S3_KEY, value=dv_key)
    ti.xcom_push(key=PROCESSED_DATA_S3_KEY, value=processed_key)

