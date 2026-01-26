# helper/response.py

def _response(status_code: int, message: str):
    return {
        "statusCode": status_code,
        "body": message
    }