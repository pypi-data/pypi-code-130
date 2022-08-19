import json
import os

from boto3.dynamodb.types import TypeDeserializer


def disable_on_staging(stage: str) -> bool:
    """
    Disable the lambda if it is called on staging
    """
    if stage == "staging":
        return {
            "statusCode": 200,
            "body": json.dumps("Staging environment, lambda not executed"),
        }
    else:
        return None


def deserialize_dynamo_item(item: dict) -> dict:
    """
    Deserialize DynamoDB item from dynamo stream
    """
    if item is not None:
        for record in item:
            data = {
                key: TypeDeserializer().deserialize(value)
                for key, value in item.items()
            }
        data["stage"] = os.environ["STAGE"]
    else:
        data = None

    return data


def censor(text: str) -> str:
    """
    Given a string, censor it letting the first letter shown
    """
    word_list = text.split()
    index = 0
    for word in word_list:
        word_list[index] = "*" * len(word_list[index])
        index += 1
    # join the words, except first letter, and return
    censored_text = " ".join(word_list)
    censored_text = text[0] + censored_text[1:] if len(text) > 0 else censored_text
    return censored_text
