from prefect import flow
from score import ride_duration_prediction
from datetime import datetime

@flow
def main():
    ride_duration_prediction(
        taxi_type="green",
        run_id="d95c3b4a3a01489cbbdc299ae879d98c",
        run_date=datetime(2025, 1, 1)
    )

if __name__ == "__main__":
    main.serve(
        name="ride-duration-prediction",
        cron="0 3 2 * *"
    )