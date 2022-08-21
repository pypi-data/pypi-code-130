import base64
import json
import logging
from enum import Enum
from typing import Optional, Union

import ecdsa
from ecdsa import SigningKey, VerifyingKey
from mypy_boto3_s3 import S3Client
from mypy_boto3_secretsmanager import SecretsManagerClient
from mypy_boto3_secretsmanager.type_defs import GetSecretValueResponseTypeDef
from mypy_boto3_sqs import SQSClient

LOG = logging.getLogger(__name__)


#
# SecretsManager
#


def get_secret_string(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Optional[str]:
    try:
        secret_response: GetSecretValueResponseTypeDef = (
            secrets_manager_client.get_secret_value(SecretId=secret_id)
        )
        return secret_response.get("SecretString", None)
    except Exception as ex:
        LOG.error(f"Could not read secret {secret_id} becasue of {ex}")
        return None


def get_secret_binary(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Optional[bytes]:
    try:
        secret_response: GetSecretValueResponseTypeDef = (
            secrets_manager_client.get_secret_value(SecretId=secret_id)
        )
        return secret_response.get("SecretBinary", None)
    except Exception as ex:
        LOG.error(f"Could not read secret {secret_id} becasue of {ex}")
        return None


def get_signing_key(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Optional[SigningKey]:
    try:
        signing_key_b64 = get_secret_binary(
            secrets_manager_client=secrets_manager_client, secret_id=secret_id
        )
        if signing_key_b64:
            signing_key_der = base64.b64decode(signing_key_b64)
            return ecdsa.SigningKey.generate().from_der(signing_key_der)
        else:
            return None
    except Exception as ex:
        LOG.error(f"Could not get signing key because of {ex}")
        return None


def get_verifying_key(
    secrets_manager_client: SecretsManagerClient, secret_id: str
) -> Optional[VerifyingKey]:
    try:
        signing_key = get_signing_key(
            secrets_manager_client=secrets_manager_client, secret_id=secret_id
        )
        if signing_key:
            return signing_key.get_verifying_key()
        else:
            return None
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
