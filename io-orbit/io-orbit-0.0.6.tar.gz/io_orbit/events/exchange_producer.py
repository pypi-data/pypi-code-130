import pika
import uuid
import requests
from io_orbit.logger.laccuna_logging import get_logger

laccuna_logger = get_logger(__name__)


class ExchangeProducer(object):
    def __init__(self, username, password, host, port, service_name, logger):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.service_name = service_name
        self.logger = logger

    def call(self, exchange, exchange_type, payload):
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host, port=self.port, credentials=credentials
            )
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

        corr_id = str(uuid.uuid4())

        if self.logger is not None:
            params = {
                "correlation_id": corr_id,
                "queue_name": exchange,
                "service_name": self.service_name,
                "task_type": "start",
            }
            try:
                requests.post(self.logger, json=params)
            except requests.exceptions.RequestException as e:
                laccuna_logger.info(
                    "Logger service is not available. Exception is: {e}"
                )

        channel.basic_publish(exchange=exchange, routing_key="", body=payload)
        connection.close()

        if self.logger is not None:
            params = {
                "correlation_id": corr_id,
                "queue_name": exchange,
                "service_name": self.service_name,
                "task_type": "end",
            }
            try:
                requests.post(self.logger, json=params)
            except requests.exceptions.RequestException as e:
                laccuna_logger.info(
                    "Logger service is not available. Exception is: {e}"
                )
