import os
import json
import boto3
import base64
import mlflow

# Run ID including model pipeline to use
RUN_ID = os.getenv('RUN_ID')
logged_model_s3 = f's3://thoughtswork-co/mlflow/4/{RUN_ID}/artifacts/model'
model = mlflow.pyfunc.load_model(logged_model_s3)

kinesis_client = boto3.client('kinesis', region_name=os.getenv('AWS_REGION', 'us-east-2'))

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')

TEST_RUN = os.getenv('TEST_RUN', 'false').lower() == 'true'


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

def predict(X):
    return float(model.predict(X)[0])

def lambda_handler(event, context):
    predictions = []

    for record in event['Records']:
        print("Seq:", record['kinesis']['sequenceNumber'])
        try:
            encoded_data = record['kinesis']['data']
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            ride_event = json.loads(decoded_data)
            ride = ride_event['ride']
            ride_id = ride_event['ride_id']

            features = prepare_features(ride)
            prediction = predict(features)

            prediction_event = {
                'model': 'ride_duration_prediction_model',
                'version': 123,
                'prediction' : {
                    'ride_duration': prediction,
                    'ride_id': ride_id
                }
            }

            if not TEST_RUN:
                print("Attempting to put record in Kinesis stream:", PREDICTIONS_STREAM_NAME)
                try:
                    print("Prediction event:", prediction_event)
                    response = kinesis_client.put_record(
                        StreamName=PREDICTIONS_STREAM_NAME,
                        Data=json.dumps(prediction_event),
                        PartitionKey=str(ride_id)
                    )
                    print("PutRecord response:", response)
                    print("Record successfully put in Kinesis stream.")
                except Exception as e:
                    print("Error putting record in Kinesis stream:", e)

            predictions.append(prediction_event)
  
        except Exception as e:
            print("Skipping malformed record:", e)

    print("Predictions:", predictions)
    return {
        'predictions': predictions
    }
