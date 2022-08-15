import boto3

################################################################
# Helpers
################################################################
def _session_maker(session_opts):
    session_opts = session_opts if session_opts else {}
    return boto3.Session(**session_opts)


def _validate_response(response, success_codes=[200]):
    meta = response["ResponseMetadata"]
    if meta["HTTPStatusCode"] not in success_codes:
        raise ReferenceError(f"status code {meta['HTTPStatusCode']}, {str(meta)}")
