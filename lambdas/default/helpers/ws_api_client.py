# helper/ws_api_client.py
import boto3

def _create_ws_api_client(domain: str, stage: str):
    return boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}"
    )