export MODEL_BUCKET_PROD="tw-stg-mlflow-models-mlops-zoomcamp"
export PREDICTIONS_STREAM_NAME="stg_ride_predictions_mlops-zoomcamp"
export LAMBDA_FUNCTION="stg_prediction_lambda_mlops-zoomcamp"

export MODEL_BUCKET_DEV="thoughtswork-co"
export MLFLOW_EXPERIMENT_ID="4"

export RUN_ID=$(aws s3api list-objects-v2 --bucket ${MODEL_BUCKET_DEV} \
--query "sort_by(Contents, &LastModified)[-1].Key" --output text | cut -f3 -d/)

aws s3 sync s3://${MODEL_BUCKET_DEV}/mlflow s3://${MODEL_BUCKET_PROD}/mlflow

variables="{MLFLOW_EXPERIMENT_ID=${MLFLOW_EXPERIMENT_ID}, PREDICTIONS_STREAM_NAME=${PREDICTIONS_STREAM_NAME}, MODEL_BUCKET=${MODEL_BUCKET_PROD}, RUN_ID=${RUN_ID}}"

aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} \
--environment "Variables=${variables}"