import requests

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49664326198011288931922744030451009108019446635804229634",
                "data": "ewogICJyaWRlIiA6IHsKICAgICJQVUxvY2F0aW9uSUQiOiAxMzAsCiAgICAiRE9Mb2NhdGlvbklEIjogMjA1LAogICAgInRyaXBfZGlzdGFuY2UiOiAzLjY2CiAgfSwKICAicmlkZV9pZCIgOiAxMjMKfQ==",
                "approximateArrivalTimestamp": 1750138787.071
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49664326198011288931922744030451009108019446635804229634",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::183631314800:role/lambda-kinesis-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-2:183631314800:stream/ride_events"
        }
    ]
}

url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
response = requests.post(url, json=event)
print(response.json())