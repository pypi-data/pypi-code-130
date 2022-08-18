from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


DEFAULT_BOOTSTRAP_SERVERS = 'b-1.data-platform-kakfka-d.v1t3kw.c8.kafka.us-east-1.amazonaws.com:9094,b-2.data-platform-kakfka-d.v1t3kw.c8.kafka.us-east-1.amazonaws.com:9094'


def get_kafka_client(bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS, security_protocol='SSL', version=(2, 5, 0)):
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        client_id='app',
        security_protocol=security_protocol,
        api_version=version
    )

    return admin_client


def create_topics(topics, bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS, security_protocol='SSL', num_partitions=2, replication_factor=2):
    client = get_kafka_client(bootstrap_servers=bootstrap_servers, security_protocol=security_protocol)

    client.list_topics()
    topic_list = []
    for topic in topics:
        topic_list.append(NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor))
    response = client.create_topics(new_topics=topic_list, validate_only=False)

    return response


def create_topics_if_not_exists(topics, bootstrap_servers=DEFAULT_BOOTSTRAP_SERVERS, security_protocol='SSL', num_partitions=2, replication_factor=2):
    try:
        response = create_topics(bootstrap_servers=bootstrap_servers, topics=topics, security_protocol=security_protocol, num_partitions=num_partitions, replication_factor=replication_factor)
    except TopicAlreadyExistsError:
        response = None
    return response
