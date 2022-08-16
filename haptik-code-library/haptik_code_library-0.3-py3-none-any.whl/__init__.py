import json


def get_bot_response(final_response: dict) -> dict:
    """
    Get Bot Response in Haptik's format
    Args:
          final_response(dict): final bot response from integration
          E.g - {"response": ["hello world"], "status": True}
    Returns:
          dict: formatted dict response, with keys = statusCode, body, headers and respective values
    """
    response = {
        'statusCode': 200,
        'body': json.dumps(final_response),
        'headers': {'Content-Type': 'application/json'}
    }
    return response
