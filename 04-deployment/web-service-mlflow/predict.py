import os
from flask import Flask, request, jsonify
import mlflow

# Run ID including model pipeline to use
RUN_ID = os.getenv('RUN_ID')
logged_model_s3 = f's3://thoughtswork-co/mlflow/4/{RUN_ID}/artifacts/model'
model = mlflow.pyfunc.load_model(logged_model_s3)

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features

def predict(X):
    preds = model.predict(X)
    return preds[0]

app = Flask('duration-prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)
    
    result = {
        'duration': pred,
        'model_version': RUN_ID,
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)