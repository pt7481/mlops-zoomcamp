from datetime import datetime
from dateutil.relativedelta import relativedelta

from prefect import flow

import score

@flow
def ride_duration_prediction_backfill():
    start_date = datetime(year=2021, month=3, day=1)
    end_date = datetime(year=2021, month=4, day=1)

    d = start_date
    while d <= end_date:
        score.ride_duration_prediction(
            taxi_type='green',
            run_id='d95c3b4a3a01489cbbdc299ae879d98c',
            run_date=d
        )
        d += relativedelta(months=1)

if __name__ == '__main__':
    ride_duration_prediction_backfill()