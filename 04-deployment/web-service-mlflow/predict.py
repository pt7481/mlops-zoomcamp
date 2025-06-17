import pickle
from flask import Flask, request, jsonify
import mlflow

# Run ID including model to use
mlflow.set_tracking_uri("http://ec2-18-223-16-40.us-east-2.compute.amazonaws.com:5000")
RUN_ID = "d95c3b4a3a01489cbbdc299ae879d98c"
logged_model = f"runs:/{RUN_ID}/model"
model = mlflow.pyfunc.load_model(logged_model)

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
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)