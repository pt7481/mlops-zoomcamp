from prefect.deployments import Deployment
from prefect.client.schemas.schedules import CronSchedule
from score import ride_duration_prediction

deployment = Deployment.build_from_flow(
    flow=ride_duration_prediction,
    name="ride_duration_prediction",
    work_queue_name="ml",
    schedule=CronSchedule(cron="0 3 2 * *"),
    parameters={
        "taxi_type": "green",
        "run_id": "d95c3b4a3a01489cbbdc299ae879d98c"    
    }
)

deployment.apply()