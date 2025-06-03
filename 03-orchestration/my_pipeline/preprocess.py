import io
import boto3
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer

S3_BUCKET = "thoughtswork-co"
S3_PREFIX = "ml_pipelines/mlops_zoomcamp"
PROCESSED_FOLDER = "processed"

DOWNLOAD_TASK_ID = 'download_trip_data'
TRAINING_DATA_S3_KEY = 'train_s3_key'
VALIDATION_DATA_S3_KEY = 'val_s3_key'
PREPROCESS_DATA_TRAIN_TASK_ID = 'preprocess_data_train'
DV_S3_KEY = 'dv_s3_key'
PROCESSED_DATA_S3_KEY = 'processed_data_s3_key'

def preprocess_data(training_data, logical_date, **context):
    run_date_str = logical_date.strftime("%Y-%m-%d")

    # Obtain either the training or validation raw trip data from S3
    ti = context['ti']
    s3_client = boto3.client("s3")
    key = ti.xcom_pull(task_ids=DOWNLOAD_TASK_ID, key=TRAINING_DATA_S3_KEY if training_data else VALIDATION_DATA_S3_KEY)
    trip_data_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    body_bytes = trip_data_obj["Body"].read()    
    buffer     = io.BytesIO(body_bytes)          
    df         = pd.read_parquet(buffer)      

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

    if training_data:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)

        # Persist DV to central storage for future use
        dv_key = f"{S3_PREFIX}/{run_date_str}/{PROCESSED_FOLDER}/dv_{run_date_str}.pkl"
        dv_bytes = pickle.dumps(dv)
        s3_client.put_object(Bucket=S3_BUCKET, Key=dv_key, Body=dv_bytes)
        print(f"DictVectorizer saved to S3 at {dv_key}")
    else:

        # Load the existing DictVectorizer from S3
        dv_key = ti.xcom_pull(task_ids=PREPROCESS_DATA_TRAIN_TASK_ID, key=DV_S3_KEY)
        dv_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=dv_key)
        dv_bytes = dv_obj['Body'].read()
        dv = pickle.loads(dv_bytes)
        print(f"DictVectorizer loaded from S3 at {dv_key}")
        
        # Transform the data using the loaded DictVectorizer
        X = dv.transform(dicts)

    y = df['duration'].values

    # Persist the processed data to S3
    processed_data_key_prefix = "train" if training_data else "val"
    processed_key = f"{S3_PREFIX}/{run_date_str}/{PROCESSED_FOLDER}/{processed_data_key_prefix}_tripdata_{run_date_str}.npz"
    buffer = io.BytesIO()
    np.savez(buffer,
         X_data=X.data,
         X_indices=X.indices,
         X_indptr=X.indptr,
         X_shape=X.shape,
         y=y)
    buffer.seek(0)
    s3_client.put_object(Bucket=S3_BUCKET, Key=processed_key, Body=buffer.getvalue())
    print(f"Processed data saved to S3 at {processed_key}")

    # Push the DictVectorizer and processed data keys to XCom for downstream tasks
    if training_data:
        ti.xcom_push(key=DV_S3_KEY, value=dv_key)
    ti.xcom_push(key=PROCESSED_DATA_S3_KEY, value=processed_key)

