import json

def lambda_handler(event, context):
    request_context = event.get("requestContext", {})

    return {"statusCode": 200}