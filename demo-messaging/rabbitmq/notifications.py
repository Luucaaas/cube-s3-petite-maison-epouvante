"""Notification service: warns subscribers when an article matches one of their interests.

Filtering happens twice:
- in RabbitMQ: the queue is only bound to the categories someone is interested in,
  so other categories never reach the service;
- in the service: each subscriber is notified only for their own interests.

Messages that cannot be processed are rejected and land in the failed queue
(dead-letter exchange), instead of being lost or blocking the queue.

Usage (from demo-messaging/):
    python -m rabbitmq.notifications
"""

from event import parse_event
from rabbitmq.common import EXCHANGE, connect, declare_exchange, routing_key

QUEUE = "notifications"
FAILED_EXCHANGE = "troc.echec"
FAILED_QUEUE = "notifications.echec"

# Demo data: subscribers and their interests (in memory, no database).
SUBSCRIBERS = {
    "Alice": ["figurines", "affiches"],
    "Bastien": ["jeux"],
    "Chloe": ["figurines", "livres"],
}


def binding_keys(subscribers: dict[str, list[str]]) -> list[str]:
    """One routing key per category at least one subscriber follows."""
    categories = {c for interests in subscribers.values() for c in interests}
    return sorted(routing_key(c) for c in categories)


def recipients(event: dict, subscribers: dict[str, list[str]]) -> list[str]:
    return [name for name, interests in subscribers.items() if event["categorie"] in interests]


def handle(body: bytes, subscribers: dict[str, list[str]] = SUBSCRIBERS) -> list[str]:
    """Return the notifications to send; raise ValueError or TypeError if the message is invalid."""
    event = parse_event(body)
    return [
        f"Notification à {name} : « {event['titre']} » ({event['categorie']}, {event['type']})"
        for name in recipients(event, subscribers)
    ]


def setup(channel) -> None:
    declare_exchange(channel)
    # Failed messages go to a fanout exchange and wait in their own queue.
    channel.exchange_declare(exchange=FAILED_EXCHANGE, exchange_type="fanout", durable=True)
    channel.queue_declare(queue=FAILED_QUEUE, durable=True)
    channel.queue_bind(queue=FAILED_QUEUE, exchange=FAILED_EXCHANGE)
    # Durable queue: messages wait here while the service is down.
    channel.queue_declare(
        queue=QUEUE,
        durable=True,
        arguments={"x-dead-letter-exchange": FAILED_EXCHANGE},
    )
    for key in binding_keys(SUBSCRIBERS):
        channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=key)


def on_message(channel, method, properties, body) -> None:
    try:
        notifications = handle(body)
    except (ValueError, TypeError) as exc:
        print(f"[notifications] message rejeté ({exc}) -> {FAILED_QUEUE}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    for line in notifications:
        print(f"[notifications] {line}")
    # Ack only after processing: if the service crashes before, the message is redelivered.
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    connection = connect()
    channel = connection.channel()
    setup(channel)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
    print(f"[notifications] en écoute sur {QUEUE} ({', '.join(binding_keys(SUBSCRIBERS))}), Ctrl+C pour arrêter")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == "__main__":
    main()
