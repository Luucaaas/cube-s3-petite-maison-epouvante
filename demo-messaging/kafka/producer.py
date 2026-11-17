"""Publish an "article.propose" event to the "troc.articles" topic.

Usage (from demo-messaging/):
    python -m kafka.producer "Figurine Orc" figurines echange
    python -m kafka.producer --invalide figurines   # broken message, goes to the failed topic
"""

from confluent_kafka import Producer

from kafka.common import TOPIC, ensure_topics, message_key, producer_config
from producer_cli import parse_args


def main() -> None:
    categorie, body = parse_args("Propose an article on the troc.articles topic.")
    ensure_topics()
    producer = Producer(producer_config())
    producer.produce(TOPIC, key=message_key(categorie), value=body)
    producer.flush(10)
    print(f"[producteur] {TOPIC} (clé {categorie}) -> {body.decode()}")


if __name__ == "__main__":
    main()
