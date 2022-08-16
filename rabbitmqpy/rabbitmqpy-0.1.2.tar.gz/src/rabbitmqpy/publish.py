#coding:utf-8

import json
import pika
from pika.exchange_type import ExchangeType

RETRY_COUNT = 5


class Puber(object):

    def __init__(self, amqp_url, exchange, exchange_type, queue=None, routing_key=None, **kwargs):
        self._connection = None
        self._channel = None
        self._url = amqp_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._routing_key = routing_key
        self._passive = kwargs.get("passive", False)
        self._durable = kwargs.get("durable", False)
        self._auto_delete = kwargs.get("auto_delete", True)

        self.connect()

    def connect(self):
        print('Connecting to %s', self._url)
        self._connection = pika.BlockingConnection(
            pika.URLParameters(self._url))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type=self._exchange_type,
            passive=self._passive,
            durable=self._durable,
            auto_delete=self._auto_delete
        )

    def send(self, data):
        for i in range(RETRY_COUNT):
            try:
                content_type = None
                if not isinstance(data, str):
                    data = json.dumps(data)
                    content_type = 'application/json'

                self._channel.basic_publish(
                    exchange=self._exchange,
                    routing_key=self._routing_key,
                    body=data,
                    properties=pika.BasicProperties(content_type=content_type))
                return True
            except Exception as e:
                if i == RETRY_COUNT-1:
                    raise e
                else:
                    self.recreate_channel()
                    print(e)

    def recreate_channel(self):
        self.connect()
        print('reconnect to %s', self._url)

    def __enter__(self):
        return self

    def __exit__(self):
        self.__del__()

    def __del__(self):
        if self._connection is not None:
            self._connection.close()


if __name__=='__main__':
    # logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    puber = Puber(
        'amqp://10.12.3.162:31911',
        'imlf-1',
        ExchangeType.direct,
        'predict',
        'predict'
    )

