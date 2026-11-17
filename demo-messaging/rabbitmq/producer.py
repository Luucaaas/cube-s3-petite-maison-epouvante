"""Publish an "article.propose" event to the "troc" exchange.

Usage (from demo-messaging/):
    python -m rabbitmq.producer "Figurine Orc" figurines echange
    python -m rabbitmq.producer --invalide figurines   # broken message, goes to the failed queue
"""

import pika

from producer_cli import parse_args
from rabbitmq.common import EXCHANGE, connect, declare_exchange, routing_key


def publish(channel, body: bytes, categorie: str) -> None:
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key(categorie),
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=pika.DeliveryMode.Persistent,  # survives a broker restart
        ),
    )


def main() -> None:
    categorie, body = parse_args("Propose an article on the troc exchange.")
    connection = connect()
    channel = connection.channel()
    declare_exchange(channel)
    publish(channel, body, categorie)
    connection.close()
    print(f"[producteur] {routing_key(categorie)} -> {body.decode()}")


if __name__ == "__main__":
    main()
