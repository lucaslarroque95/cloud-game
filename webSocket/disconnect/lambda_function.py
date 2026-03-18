import json

def lambda_handler(event, context):
    connection_id = event.get("requestContext",{}).get("connectionId")
    # borrar de DynamoDB
    return {
        'statusCode': 200
    }