import boto3

from .secrets import *

SESSION_OPTS = {
    "aws_access_key_id": None,
    "aws_secret_access_key": None,
    "aws_session_token": None,
    "region_name": None,
    "botocore_session": None,
    "profile_name": None,
}

################################################################
# Helpers
################################################################
def session_maker(session_opts):
    session_opts = session_opts if session_opts else {}
    return boto3.Session(**session_opts)


def validate_response(response, success_codes=[200]):
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"] not in success_codes:
        raise ReferenceError(f"status code {meta['HTTPStatusCode']}, {str(meta)}")
