#coding:utf-8

import pika
import functools
from pika.exceptions import StreamLostError, ConnectionWrongStateError


class Subscriber(object):

    def __init__(self, amqp_url, exchange, exchange_type, queue, routing_key=None, **kwargs):
        self._connection = None
        self._channel = None
        self._url = amqp_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._routing_key = routing_key
        self._queue = queue

        # 通用配置
        self._passive = kwargs.get("passive", False)
        self._durable = kwargs.get("durable", False)
        self._auto_delete = kwargs.get("auto_delete", True)
        self._auto_ack = kwargs.get("auto_ack", True)

        # 交换机配置
        self._exchange_passive = kwargs.get("exchange_passive")
        self._exchange_durable = kwargs.get("exchange_durable")
        self._exchange_auto_delete = kwargs.get("exchange_auto_delete")
        self._exchange_auto_ack = kwargs.get("exchange_auto_ack")

        # 队列配置
        self._queue_durable = kwargs.get("queue_durable")
        self._queue_auto_delete = kwargs.get("queue_auto_delete")
        self._queue_auto_ack = kwargs.get("queue_auto_ack")

        self.connect()

    def _get_params(self, param, _type):
        prop = f"_{_type}" + param
        if hasattr(self, prop) and getattr(self, prop) is not None:
            return getattr(self, prop)
        else:
            return getattr(self, param, None)

    def connect(self):
        print('Connecting to %s', self._url)
        self._connection = pika.BlockingConnection(
            pika.URLParameters(self._url))
        self._channel = self._connection.channel()

        # 匹配交换机
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type=self._exchange_type,
            passive=self._get_params("_passive", "exchange"),
            durable=self._get_params("_durable", "exchange"),
            auto_delete=self._get_params("_auto_delete", "exchange")
        )

        # 声明队列
        self._channel.queue_declare(
                queue=self._queue,
                durable=self._get_params("_durable", "queue"),
                auto_delete=self._get_params("_auto_delete", "queue"))

        # 绑定队列
        self._channel.queue_bind(
            queue=self._queue, exchange=self._exchange, routing_key=self._routing_key)
        self._channel.basic_qos(prefetch_count=1)

        on_message_callback = functools.partial(
            self.on_message, userdata='on_message_userdata')

        self._channel.basic_consume(
                self._queue,
                on_message_callback,
                auto_ack=self._get_params("_auto_ack", "queue")
                )

    def reconnect(self):
        self.connect()
        print('reconnect to %s', self._url)


    def on_message(self, chan, method_frame, header_frame, body, userdata=None):
        print('Delivery properties: %s, message metadata: %s', method_frame, header_frame)
        print('Userdata: %s, message body: %s', userdata, body)
        # chan.basic_ack(delivery_tag=method_frame.delivery_tag)


    def start(self):
        while True:
            try:
                self._channel.start_consuming()
            except KeyboardInterrupt:
                self._channel.stop_consuming()
                break
            except (StreamLostError,
                    ConnectionWrongStateError,
                    ConnectionResetError):
                self.reconnect()
            except:
                raise e


    def __del__(self):
        if self._connection is not None:
            self._connection.close()


if __name__=='__main__':

    subs = Subscriber(
        'amqp://10.12.3.162:31911',
        'imlf-1',
        'direct',
        'predict',
        'predict'
    )
    subs.start()
