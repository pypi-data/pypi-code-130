import json
from time import time

from kafka import KafkaConsumer

from hrthy_core.events.events.base_event import BaseEvent
from hrthy_core.events.topic import Topic, TopicGroup
from hrthy_core.repository.event.repository_abstract import BaseEventRepositoryAbstract


class BaseConsumer:
    TOPICS: list = []
    RETRY_TOPIC: Topic = None
    TOPIC_GROUP: TopicGroup = None
    REPOSITORY: BaseEventRepositoryAbstract = None

    def _get_topics(self) -> list:
        if not self.RETRY_TOPIC:
            raise Exception('Invalid Retry TOPIC. Please make sure you have it set')
        if type(self.TOPICS) is not list:
            raise Exception('Invalid TOPICS. Please make sure you have it set')
        for topic in self.TOPICS:
            if type(topic) is not Topic:
                raise Exception('Invalid TOPIC in the list. Please make sure to use one of the available topics')
        return [t.value for t in self.TOPICS]

    def _get_topics_group(self) -> str:
        if type(self.TOPIC_GROUP) is not TopicGroup:
            raise Exception('Invalid TOPIC_GROUP. Please make sure you have it set')
        return self.TOPIC_GROUP.value

    def _get_brokers(self) -> list:
        return []

    def _callback(self, message) -> None:
        pass

    def _negative_ack(self, event: BaseEvent):
        self.REPOSITORY.negative_ack(topic=self.RETRY_TOPIC.value, event_to_send=event)

    def start(self) -> None:
        consumer = KafkaConsumer(
            *self._get_topics(),
            group_id=self._get_topics_group(),
            value_deserializer=lambda v: json.loads(v),
            bootstrap_servers=self._get_brokers(),
            enable_auto_commit=True
        )
        for message in consumer:
            self._callback(message)
