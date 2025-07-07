#!/bin/bash

STREAM_NAME="stg_ride_predictions_mlops-zoomcamp"
SHARD_ID=$(aws kinesis describe-stream \
  --stream-name "$STREAM_NAME" \
  --query "StreamDescription.Shards[0].ShardId" \
  --output text)

ITER=$(aws kinesis get-shard-iterator \
  --stream-name "$STREAM_NAME" \
  --shard-id "$SHARD_ID" \
  --shard-iterator-type TRIM_HORIZON \
  --query 'ShardIterator' --output text)

while [ "$ITER" != "null" ]; do
  OUT=$(aws kinesis get-records --shard-iterator "$ITER" --limit 100)
  
  echo "$OUT" | jq -r '.Records[].Data' | while read -r encoded; do
    echo "$encoded" | base64 --decode
    echo    # new line for readability
  done
  
  ITER=$(echo "$OUT" | jq -r '.NextShardIterator')
  sleep 1
done

