import os
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic

from mobio.libs.kafka_lib import KAFKA_BOOTSTRAP, MobioEnvironment


def create_kafka_topics(lst_topic):
    admin_client = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    existing_topics = list(admin_client.list_topics().topics.keys())
    new_topics = []
    for required_topic in lst_topic:
        if required_topic not in existing_topics:
            new_topics.append(
                NewTopic(
                    required_topic,
                    num_partitions=4,
                    replication_factor=int(os.getenv(MobioEnvironment.KAFKA_REPLICATION_FACTOR)),
                )
            )
        else:
            print("Topic {} existed".format(required_topic))

    if new_topics:
        fs = admin_client.create_topics(new_topics)

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                print("New Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create new topic {}: {}".format(topic, e))


def create_kafka_topics_v2(lst_topic):
    admin_client = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    existing_topics = list(admin_client.list_topics().topics.keys())
    new_topics = []
    for required_topic in lst_topic:
        if (
            type(required_topic) != tuple
            or len(required_topic) < 2
            or type(required_topic[1]) != int
            or type(required_topic[0]) != str
            or required_topic[1] < 1
        ):
            raise Exception("{} is not valid".format(required_topic))
        if required_topic[0] not in existing_topics:
            new_topics.append(
                NewTopic(
                    required_topic[0],
                    num_partitions=required_topic[1] if required_topic[1] else 4,
                    replication_factor=int(
                        os.getenv(MobioEnvironment.KAFKA_REPLICATION_FACTOR)
                    ),
                    config=required_topic[2] if len(required_topic) == 3 and type(required_topic[2]) is dict else {}
                )
            )
        else:
            print("Topic {} existed".format(required_topic[0]))

    if new_topics:
        fs = admin_client.create_topics(new_topics)

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                print("New Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create new topic {}: {}".format(topic, e))


if __name__ == "__main__":
    create_kafka_topics_v2([("test3", 1, {"compression.type": "snappy"})])
