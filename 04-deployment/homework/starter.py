#!/usr/bin/env python
# coding: utf-8

import pickle
import pandas as pd
import sys

with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)


categorical = ['PULocationID', 'DOLocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df

def save_predictions(year, month):
    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet')
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str') # Make an artificial Ride ID for the ride data

    df_results = pd.DataFrame()
    df_results['ride_id'] = df['ride_id']
    df_results['prediction'] = y_pred
    df_results.to_parquet(f'output/yellow_tripdata_{year:04d}-{month:02d}.parquet', engine='pyarrow', compression=None, index=False)
    return df_results

if __name__ == '__main__':
    year = int(sys.argv[1]) 
    month = int(sys.argv[2])

    df_results = save_predictions(year, month)
    print(f'Mean prediction: {df_results["prediction"].mean()}')




