import os
import sys

import uuid
import pickle

from datetime import datetime
import pandas as pd
import mlflow

from prefect import task, flow, get_run_logger
from prefect.context import get_run_context

from dateutil.relativedelta import relativedelta

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline

def generate_uuids(n):
    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids

def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    df['ride_id'] = generate_uuids(len(df))

    return df

def prepare_dictionaries(df: pd.DataFrame):
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts

def load_model(run_id: str):
    logged_model_s3 = f's3://thoughtswork-co/mlflow/4/{run_id}/artifacts/model'
    model = mlflow.pyfunc.load_model(logged_model_s3)
    return model

def save_results(df, y_pred, run_id, output_file):
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    df_result.to_parquet(output_file, index=False)

@task
def apply_model(input_file, run_id, output_file):
    logger = get_run_logger()
    logger.info(f"Loading data from {input_file}")

    logger.info(f"Loading model with run_id {run_id}")
    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    logger.info(f'loading the model with run_id {run_id}')
    model = load_model(run_id)

    logger.info(f'applying the model')
    y_pred = model.predict(dicts)

    logger.info(f'saving the results to {output_file}')
    save_results(df, y_pred, run_id, output_file)
    return output_file

def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month

    # https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet
    #input_file = f"s3://thoughtswork-co/mlflow/4/{run_id}/artifacts/input_data/{year}/{month:02d}/{taxi_type}.parquet"
    input_file = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
    output_file = f"s3://thoughtswork-co/mlflow/4/{run_id}/artifacts/output_data/{year}/{month:02d}/{taxi_type}.parquet"
    return input_file, output_file

@flow
def ride_duration_prediction(
    taxi_type: str = 'green',
    run_id: str = 'd95c3b4a3a01489cbbdc299ae879d98c',
    run_date: datetime = datetime.now()):
    if run_date is None:
        ctx = get_run_context()
        run_date = ctx.flow_run.expected_start_time

    input_file, output_file = get_paths(run_date, taxi_type, run_id)

    apply_model(input_file, run_id, output_file)

def run():
    taxi_type = sys.argv[1] if len(sys.argv) > 1 else 'green'
    year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
    month = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.now().month
    run_id = sys.argv[4] if len(sys.argv) > 4 else 'd95c3b4a3a01489cbbdc299ae879d98c'

    ride_duration_prediction(taxi_type, run_id, datetime(year, month, 1))

if __name__ == "__main__":
    run()