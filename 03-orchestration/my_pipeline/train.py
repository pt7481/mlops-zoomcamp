import boto3
import io
import mlflow
import scipy.sparse as sparse
import numpy as np
from sklearn.metrics import root_mean_squared_error
import xgboost as xgb

S3_BUCKET = "thoughtswork-co"
PREPROCESS_DATA_TRAIN_TASK_ID = 'preprocess_data_train'
PREPROCESS_DATA_VAL_TASK_ID = 'preprocess_data_val'
PROCESSED_DATA_S3_KEY = 'processed_data_s3_key'

MLFLOW_TRACKING_URI = "http://ec2-13-58-148-173.us-east-2.compute.amazonaws.com:5000/"
MLFLOW_EXPERIMENT_NAME = "nyc-taxi-experiment"

def train_model(**context):
    s3_client = boto3.client("s3")

    # Load the processed training and validation data from S3
    def load_processed_data(processed_data_key):
        resp = s3_client.get_object(Bucket=S3_BUCKET, Key=processed_data_key)
        buf  = io.BytesIO(resp['Body'].read())
        arrs = np.load(buf)

        X_loaded = sparse.csr_matrix(
            (arrs["X_data"], arrs["X_indices"], arrs["X_indptr"]),
            shape=tuple(arrs["X_shape"])
        )
        y_loaded = arrs["y"]

        return X_loaded, y_loaded
    
    ti = context['ti']
    processed_train_key = ti.xcom_pull(task_ids=PREPROCESS_DATA_TRAIN_TASK_ID, key=PROCESSED_DATA_S3_KEY)
    processed_val_key = ti.xcom_pull(task_ids=PREPROCESS_DATA_VAL_TASK_ID, key=PROCESSED_DATA_S3_KEY)
    X_train, y_train = load_processed_data(processed_train_key)
    X_val, y_val = load_processed_data(processed_val_key)

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        
        train = xgb.DMatrix(X_train, label=y_train)
        valid = xgb.DMatrix(X_val, label=y_val)

        best_params = {
            'learning_rate': 0.09585355369315604,
            'max_depth': 30,
            'min_child_weight': 1.060597050922164,
            'objective': 'reg:linear',
            'reg_alpha': 0.018060244040060163,
            'reg_lambda': 0.011658731377413597,
            'seed': 42
        }

        mlflow.log_params(best_params)

        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=30,
            evals=[(valid, 'validation')],
            early_stopping_rounds=50
        )

        y_pred = booster.predict(valid)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        # Save the model to S3
        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")

    return run.info.run_id