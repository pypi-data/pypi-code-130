import json
import pika
from stix2 import Bundle, parse
from typing import Callable

credentials = pika.PlainCredentials("root", "root")

class ChannelProvider:
    _connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost", 5672, "/", credentials)
    )
    _stix_channel = None
    _enrichment_channel = None

    @staticmethod
    def get_enrichment_channel():
        if ChannelProvider._enrichment_channel is None:
            new_channel = ChannelProvider._connection.channel()

            new_channel.exchange_declare(
                exchange="enrichment", exchange_type="fanout"
            )

            new_channel.queue_declare(queue="enrichment-queue")

            new_channel.queue_bind(
                exchange="enrichment", queue="enrichment_queue"
            )

            ChannelProvider._enrichment_channel = new_channel

        return ChannelProvider._enrichment_channel

    @staticmethod
    def get_stix_channel():
        if ChannelProvider._stix_channel is None:
            new_channel = ChannelProvider._connection.channel()

            new_channel.queue_declare(queue="stix-queue")

            return new_channel

        return ChannelProvider._stix_channel


class Helper:
    def listen(callback: Callable) -> None:
        def consume_message(ch, method, properties, body):
            bundle = parse(str(body))
            return callback(bundle)

        channel = ChannelProvider.get_enrichment_channel()
        channel.basic_consume(
            queue="enrichment-queue",
            on_message_callback=consume_message,
            auto_ack=True,
        )
        channel.start_consuming()

    def send_stix_bundle(bundle: Bundle) -> None:
        channel = ChannelProvider.get_stix_channel()
        channel.basic_publish(
            exchange="", routing_key="stix-queue", body=bundle.serialize()
        )

    def consume_stix(callback: Callable) -> None:
        def consume_message(ch, method, properties, body):
            json_bundle = json.loads(body)
            bundle = parse(json_bundle)
            return callback(bundle)

        channel = ChannelProvider.get_stix_channel()
        channel.basic_consume(
            queue="stix-queue",
            on_message_callback=consume_message,
            auto_ack=True,
        )
        channel.start_consuming()
