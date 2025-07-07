#!/bin/bash

aws kinesis put-record \
    --stream-name prod_ride_events_mlops-zoomcamp \
    --partition-key "1" \
    --cli-binary-format raw-in-base64-out \
    --data '{"ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    },
    "ride_id": 156}'