from datetime import datetime
from homework import batch
import pandas as pd

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def test_prepare_data():
    data = [
        (None, None, dt(1, 1), dt(1, 10)),      # Duration 9 minutes
        (1, 1, dt(1, 2), dt(1, 10)),            # Duration 8 minutes
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),   # Duration 59 seconds               (should be filtered out)
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),       # Duration 60 minutes and 1 second  (should be filtered out)
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)

    predicted_durations_df = batch.prepare_data(df, ['PULocationID', 'DOLocationID'])
    assert predicted_durations_df.shape[0] == 2
    
    return predicted_durations_df