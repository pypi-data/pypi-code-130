import pika
import requests
from io_orbit.logger.laccuna_logging import get_logger

laccuna_logger = get_logger(__name__)


class ExchangeReceiver(object):
    def __init__(
        self,
        username,
        password,
        host,
        port,
        exchange,
        exchange_type,
        service,
        service_name,
        logger,
    ):
        self.service_worker = service
        self.service_name = service_name
        self.exchange = exchange
        self.logger = logger

        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        )

        channel = connection.channel()
        channel.exchange_declare(exchange=self.exchange, exchange_type=exchange_type)

        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=self.exchange, queue=queue_name)
        channel.basic_consume(
            queue=queue_name, on_message_callback=self.on_request, auto_ack=True
        )

        laccuna_logger.info("Awaiting requests from [x] " + self.exchange + " [x]")
        channel.start_consuming()

    def on_request(self, ch, method, props, body):
        service_instance = self.service_worker()

        if self.logger is not None:
            params = {
                "correlation_id": "-",
                "queue_name": self.exchange,
                "service_name": self.service_name,
                "task_type": "start",
            }
            try:
                requests.post(self.logger, json=params)
            except requests.exceptions.RequestException as e:
                laccuna_logger.info(
                    "Logger service is not available. Exception is: {e}"
                )

        response, task_type = service_instance.call(body)

        if self.logger is not None:
            params = {
                "correlation_id": "-",
                "queue_name": self.exchange,
                "service_name": self.service_name,
                "task_type": "end",
            }
            try:
                requests.post(self.logger, json=params)
            except requests.exceptions.RequestException as e:
                laccuna_logger.info(
                    "Logger service is not available. Exception is: {e}"
                )

        laccuna_logger.info("Processed request:", task_type)
