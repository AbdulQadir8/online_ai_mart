import json


def load_error_json(error_message: str) -> str:
    details = json.loads(error_message.text)
    error_details = details.get("detail")
    return error_details