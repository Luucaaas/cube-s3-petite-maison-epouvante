"""Publish an "article.propose" event to the "troc" exchange.

Usage (from demo-messaging/):
    python -m rabbitmq.producer "Figurine Orc" figurines echange
    python -m rabbitmq.producer --invalide figurines   # broken message, goes to the failed queue
"""

import argparse
import json

import pika

from event import make_event
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
    parser = argparse.ArgumentParser(description="Propose an article on the troc exchange.")
    parser.add_argument("titre", nargs="?", default="Figurine Orc")
    parser.add_argument("categorie", nargs="?", default="figurines")
    parser.add_argument("type", nargs="?", default="echange", choices=["echange", "don"])
    parser.add_argument("--invalide", action="store_true", help="send a malformed message")
    args = parser.parse_args()

    if args.invalide:
        body = b"ceci n'est pas un evenement"
    else:
        event = make_event(args.titre, args.categorie, args.type)
        body = json.dumps(event, ensure_ascii=False).encode()

    connection = connect()
    channel = connection.channel()
    declare_exchange(channel)
    publish(channel, body, args.categorie)
    connection.close()
    print(f"[producteur] {routing_key(args.categorie)} -> {body.decode()}")


if __name__ == "__main__":
    main()
