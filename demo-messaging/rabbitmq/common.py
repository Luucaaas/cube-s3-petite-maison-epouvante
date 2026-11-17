"""RabbitMQ settings shared by the producer and the notification service."""

import os

import pika

EXCHANGE = "troc"  # topic exchange
ROUTING_PREFIX = "article.propose"


def routing_key(categorie: str) -> str:
    return f"{ROUTING_PREFIX}.{categorie}"


def connect() -> pika.BlockingConnection:
    """Open a connection using environment variables (local demo defaults)."""
    credentials = pika.PlainCredentials(
        os.environ.get("RABBITMQ_USER", "guest"),
        os.environ.get("RABBITMQ_PASSWORD", "guest"),
    )
    params = pika.ConnectionParameters(
        host=os.environ.get("RABBITMQ_HOST", "localhost"),
        port=int(os.environ.get("RABBITMQ_PORT", "5672")),
        credentials=credentials,
    )
    return pika.BlockingConnection(params)


def declare_exchange(channel) -> None:
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
