"""Kafka settings shared by the producer and the notification service."""

import os

from confluent_kafka.admin import AdminClient, NewTopic

TOPIC = "troc.articles"
FAILED_TOPIC = "troc.articles.echec"
GROUP = "notifications"
PARTITIONS = 3


def bootstrap() -> str:
    return os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")


def message_key(categorie: str) -> bytes:
    """The key is the category: all articles of one category go to the same partition, in order."""
    return categorie.encode()


def producer_config() -> dict:
    return {"bootstrap.servers": bootstrap(), "acks": "all"}


def consumer_config(group: str) -> dict:
    return {
        "bootstrap.servers": bootstrap(),
        "group.id": group,
        # A new group starts from the oldest message still in the log.
        "auto.offset.reset": "earliest",
        # Offsets are committed by hand, after processing (same idea as a RabbitMQ ack).
        "enable.auto.commit": False,
        # If the service crashes without leaving its group, Kafka waits this long before giving
        # its partitions to another consumer (45 s by default, shortened for the demo).
        "session.timeout.ms": 10000,
        "heartbeat.interval.ms": 3000,
    }


def ensure_topics() -> None:
    """Create the demo topics if they do not exist yet."""
    admin = AdminClient({"bootstrap.servers": bootstrap()})
    existing = admin.list_topics(timeout=10).topics
    missing = [
        NewTopic(name, num_partitions=PARTITIONS, replication_factor=1)
        for name in (TOPIC, FAILED_TOPIC)
        if name not in existing
    ]
    for future in admin.create_topics(missing).values() if missing else []:
        future.result()
