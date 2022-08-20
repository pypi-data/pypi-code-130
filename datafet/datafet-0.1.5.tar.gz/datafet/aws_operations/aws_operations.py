import base64
import json
import logging
from enum import Enum
from typing import Union

import ecdsa
from ecdsa import SigningKey, VerifyingKey
from mypy_boto3_s3 import S3Client
from mypy_boto3_secretsmanager import SecretsManagerClient
from mypy_boto3_sqs import SQSClient

LOG = logging.getLogger(__name__)


#
# SecretsManager
#


class SecretKind(Enum):
    SecretString = 1
    SecretBinary = 2


def get_secret(
    secrets_manager_client: SecretsManagerClient,
    secret_id: str,
    secret_kind: SecretKind,
) -> Union[str, bytes, None]:
    try:
        secret_response = secrets_manager_client.get_secret_value(SecretId=secret_id)
        return secret_response.get(secret_kind.name)
    except Exception as ex:
        LOG.error(f"Could not read secret {secret_id} becasue of {ex}")
        return None


def get_secret_string(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Union[str, None]:
    return get_secret(secrets_manager_client, secret_id, SecretKind.SecretString)


def get_secret_binary(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Union[bytes, None]:
    return get_secret(secrets_manager_client, secret_id, SecretKind.SecretBinary)


def get_signing_key(secret_id: str) -> Union[SigningKey, None]:
    try:
        signing_key_b64 = get_secret_binary(secret_id=secret_id)
        signing_key_der = base64.b64decode(signing_key_b64)
        return ecdsa.SigningKey.generate().from_der(signing_key_der)
    except Exception as ex:
        LOG.error(f"Could not get signing key because of {ex}")
        return None


def get_verifying_key(secret_id: str) -> Union[VerifyingKey, None]:
    try:
        signing_key = get_signing_key(secret_id=secret_id)
        return signing_key.get_verifying_key()
    except Exception as ex:
        LOG.error(f"Could not get verifying key because of {ex}")
        return None


#
# S3
#


def get_s3_object(s3_client: S3Client, bucket: str, key: str):
    try:
        return s3_client.get_object(Bucket=bucket, Key=key)
    except Exception as ex:
        LOG.error(f"Could not read object bucket: {bucket} key: {key} becasue of {ex}")
        return None


def delete_s3_object(s3_client: S3Client, bucket: str, key: str) -> bool:
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as ex:
        LOG.error(
            f"Could not delete object bucket: {bucket} key: {key} becasue of {ex}"
        )
        return False


def save_to_s3(s3_client: S3Client, json: str, bucket: str, key: str) -> bool:
    try:
        s3_client.put_object(Body=json, Bucket=bucket, Key=key)
        return True
    except Exception as ex:
        LOG.error(f"Could not put object bucket: {bucket} key: {key} becasue of {ex}")
        return False


def put_empty_to_s3(s3_client: S3Client, bucket: str, key: str) -> bool:
    try:
        s3_client.put_object(Bucket=bucket, Key=key)
        return True
    except Exception as ex:
        LOG.error(f"Could not put object bucket: {bucket} key: {key} becasue of {ex}")
        return False


#
# SQS
#


def send_sqs_message(sqs_client: SQSClient, queue_url: str, message: str) -> bool:
    try:
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
        return True
    except Exception as ex:
        LOG.error(
            f"Could not send SQS message queue_url: {queue_url} message: {message} becasue of {ex}"
        )
        return False
