# services/base_service.py
from botocore.exceptions import ClientError

class ServiceError(Exception):
    pass


def aws_call(action: callable, error_msg: str):
    try:
        return action()
    except ClientError as e:
        msg = e.response.get("Error", {}).get("Message")
        raise ServiceError(f"{error_msg}: {msg}")