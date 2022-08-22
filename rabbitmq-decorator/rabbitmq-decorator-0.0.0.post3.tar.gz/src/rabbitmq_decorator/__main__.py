import asyncio
import os
from typing import Any, Dict

from src.rabbitmq_decorator.rabbitmq_producer import RabbitMQProducer

from . import Exchange, RabbitMQConnection, RabbitMQConsumer, RabbitMQHandler, RabbitMQMessage

PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
USERNAME = os.environ.get("RABBITMQ_USERNAME")
PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
HOST = os.environ.get("RABBITMQ_HOST", "localhost")

event_loop = asyncio.get_event_loop()


async def main():
    i = 0
    producer = RabbitMQProducer(RabbitMQConnection())
    producer.publish(RabbitMQMessage("1.2.3", {"test": i}), Exchange("test_exchange", durable=True))

    while i < 4:
        await asyncio.sleep(3)
        i += 1
    rabbit_handler.stop_consume()
    await asyncio.sleep(2)


rabbit_handler = RabbitMQHandler(event_loop=event_loop)


@rabbit_handler
class SomeClass:
    EXCHANGE = Exchange("test_exchange", durable=True)
    _producer: RabbitMQProducer = rabbit_handler.get_new_producer(EXCHANGE)

    @RabbitMQConsumer(EXCHANGE)
    async def consumer_1(self, body: Dict[str, Any], route="*.*.*"):
        print("I'm getting all the messages on test_exchange")
        self._producer.publish(RabbitMQMessage(routing_key="response.consumer1", body={"status": "Success"}))

    @RabbitMQConsumer(EXCHANGE, route="*.*.*")
    async def consumer_2(self, body: Dict[str, Any]):
        print("I'm getting only the messages on test_exchange with *.*.* as routing-key ")
        response_exchange = Exchange("response_exchanges", durable=True)
        self._producer.publish(
            exchange=response_exchange,
            message=RabbitMQMessage(routing_key="response.consumer2", body={"status": "Success"}),
        )


if __name__ == "__main__":
    pass
    cls = SomeClass()
    rabbit_handler.start(cls)
    event_loop.run_until_complete(main())

    asyncio.run(main())
