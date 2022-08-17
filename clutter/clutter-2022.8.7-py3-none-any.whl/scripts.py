import logging
import os
import subprocess

import boto3
import click
from click_loglevel import LogLevel
from tabulate import tabulate

from . import aws, docker
from .aws.common import session_maker
from .logging import logger


@click.group()
def clutter():
    pass


################################################################
# AWS S3
################################################################
@clutter.group()
def s3():
    pass


# list objects
@s3.command()
@click.option("-b", "--bucket", type=str, required=True, help="S3 Bucket Name.")
@click.option("--prefix", type=str, default=None, help="Object Prefix. Example: 'dataset_a/daily'")
@click.option("--pattern", type=str, default=None, help="Pattern. Example: '2022-*-*-file.csv'")
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="AWS Profile Name.")
def list_objects(bucket, prefix, pattern, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get results
    contents = aws.s3.list_objects(bucket, prefix, pattern, session=session)

    # print results
    path = "/".join([x for x in [bucket, prefix, pattern] if x is not None])
    print(f"ls {path}\n" + tabulate(contents))


# delete objects
@s3.command()
@click.option("-b", "--bucket", type=str, required=True, help="S3 Bucket Name.")
@click.option("--prefix", type=str, default=None, help="Object Prefix. Example: 'dataset_a/daily'")
@click.option("--pattern", type=str, default=None, help="Pattern. Example: '2022-*-*-file.csv'")
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="AWS Profile Name.")
def delete_objects(bucket, prefix, pattern, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get results
    response = aws.s3.delete_objects(bucket, prefix, pattern, session=session)
    if response is None:
        return

    # print results
    path = "/".join([x for x in [bucket, prefix, pattern] if x is not None])

    # logging
    print(f"total {len(response)} objects are deleted from {path}!")


################################################################
# AWS SQS
################################################################
@clutter.group()
def sqs():
    pass


@sqs.command()
@click.option("--prefix", type=str, default=None)
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="Log Level.")
def list_queues(prefix, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get queue urls
    queue_urls = aws.sqs.list_queues(prefix=prefix, session=session)
    print(f"List of Queues.\n" + tabulate([(q.rsplit("/", 1)[-1], q) for q in sorted(queue_urls)]))


@sqs.command()
@click.argument("queue-name", type=str, default=None)
@click.option("--delete-dlq", type=bool, default=True)
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="Log Level.")
def delete_queue(queue_name, delete_dlq, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get queue urls
    try:
        _ = aws.sqs.delete_queue(queue_name=queue_name, delete_dlq=delete_dlq, session=session)
    except KeyError:
        print(f"No Queue '{queue_name}' was Found. exit!")
        return
    except Exception as ex:
        logger.error(ex)
        return

    print(f"Queue '{queue_name}' is Deleted.")


@sqs.command()
@click.argument("queue-name", type=str, default=None)
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="Log Level.")
def purge_queue(queue_name, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get queue urls
    try:
        _ = aws.sqs.purge_queue(queue_name=queue_name, session=session)
    except KeyError:
        print(f"No Queue '{queue_name}' was Found. exit!")
        return
    except Exception as ex:
        logger.error(ex)
        return

    print(f"Queue '{queue_name}' is Purged.")


@sqs.command()
@click.argument("queue-name", type=str, default=None)
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="Log Level.")
def get_queue_url(queue_name, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get queue urls
    try:
        queue_url = aws.sqs.get_queue_url(queue_name=queue_name, session=session)
    except KeyError:
        print(f"No Queue '{queue_name}' was Found. exit!")
        return
    except Exception as ex:
        logger.error(ex)
        return

    print(f"QueueUrl: {queue_url}")


@sqs.command()
@click.argument("queue-name", type=str, default=None)
@click.option("--delay-seconds", type=int, default=0)
@click.option("--visibility-timeout", type=int, default=60)
@click.option("--dlq_after_received", type=int, default=10, help="Not Create DLQ if This Value is Minus")
@click.option("--profile", type=str, default=None, help="AWS Profile Name.")
@click.option("--log-level", type=LogLevel(), default=logging.INFO, help="Log Level.")
def create_queue(queue_name, delay_seconds, visibility_timeout, dlq_after_received, profile, log_level):
    # set log level
    logger.setLevel(level=log_level)

    # create session
    session_opts = {"profile_name": profile}
    session_opts = {k: v for k, v in session_opts.items() if v is not None}
    session = aws.common.session_maker(session_opts=session_opts)

    # get queue urls
    try:
        response = aws.sqs.create_queue(
            queue_name=queue_name,
            delay_seconds=delay_seconds,
            visibility_timeout=visibility_timeout,
            dlq_after_received=dlq_after_received,
            wait_for_queue_to_ready_sec=60,
            session=session,
        )
    except Exception as ex:
        print(f"Create Queue '{queue_name}' Failed. Exit!")
        logger.error(ex)
        return

    if response is None:
        return
    print(f"Queue '{queue_name}' Created. (QueueUrl: {response['QueueUrl']})")


################################################################
# AWS SecretsManager
################################################################
@clutter.group()
def secrets_manager():
    pass


@secrets_manager.command()
@click.argument("patterns", default="*")
@click.option("--profile", default=None)
def list_secrets(patterns, profile):
    aws.secrets.list_secrets(patterns=patterns, profile_name=profile)


# [TODO]
# 아직 동작 안 함
# @clutter.command()
# @click.argument("cmd", nargs=-1)
# def bash(cmd):
#     docker.load_secrets()
#     subprocess.Popen(cmd, shell=False, env=dict(os.environ)).wait()


# [NOTE]
# Child Process Cannot Load Parent's Environment Variables!
# @clutter.command()
# @click.option("--secrets-dir", type=click.Path(exists=True, file_okay=False), default=SECRETS_DIR, show_default=True)
# @click.option("--secrets-delim", type=str, default=SECRETS_DELIM, show_default=True)
# def load_envs_from_docker_secrets(secrets_dir, secrets_delim):
#     load_secrets(secrets_dir=secrets_dir, secrets_delim=secrets_delim)
