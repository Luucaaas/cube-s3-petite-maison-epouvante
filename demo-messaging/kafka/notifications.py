"""Notification service on Kafka: same rules as the RabbitMQ version, different mechanics.

- Kafka has no routing: the service reads every article of the topic and filters itself.
- Messages stay in the log after being read. The consumer group remembers its position
  (offset): if the service stops, it resumes where it was.
- --rejouer starts a brand-new group, which re-reads the whole history from the beginning,
  without moving the position of the normal service.
- Kafka has no dead-letter queue: an unreadable message is copied by the service
  to the "troc.articles.echec" topic, then skipped.

Usage (from demo-messaging/):
    python -m kafka.notifications
    python -m kafka.notifications --rejouer
"""

import argparse
import time

from confluent_kafka import Consumer, Producer

from kafka.common import (
    FAILED_TOPIC,
    GROUP,
    TOPIC,
    consumer_config,
    ensure_topics,
    producer_config,
)
from subscribers import handle


def group_name(replay: bool, now: float | None = None) -> str:
    """The normal group, or a new one (so it starts from the oldest message) for a replay."""
    if not replay:
        return GROUP
    return f"{GROUP}-rejeu-{int(now if now is not None else time.time())}"


def process(msg, failed_producer) -> None:
    """Print the notifications; copy an unreadable message to the failed topic (unless replaying)."""
    where = f"p{msg.partition()} #{msg.offset()}"
    try:
        notifications = handle(msg.value())
    except (ValueError, TypeError) as exc:
        if failed_producer is None:
            print(f"[notifications] {where} message rejeté ({exc}), déjà copié lors de la 1re lecture")
            return
        failed_producer.produce(FAILED_TOPIC, key=msg.key(), value=msg.value())
        failed_producer.flush(10)
        print(f"[notifications] {where} message rejeté ({exc}) -> {FAILED_TOPIC}")
        return
    if not notifications:
        print(f"[notifications] {where} personne n'est intéressé, ignoré")
    for line in notifications:
        print(f"[notifications] {where} {line}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Kafka notification service.")
    parser.add_argument("--rejouer", action="store_true", help="re-read the whole topic history")
    args = parser.parse_args()

    ensure_topics()
    group = group_name(args.rejouer)
    consumer = Consumer(consumer_config(group))
    # A replay re-reads old messages: unreadable ones are already in the failed topic.
    failed_producer = None if args.rejouer else Producer(producer_config())
    consumer.subscribe([TOPIC])
    print(f"[notifications] groupe {group}, en écoute sur {TOPIC}, Ctrl+C pour arrêter")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"[notifications] erreur Kafka : {msg.error()}")
                continue
            process(msg, failed_producer)
            # Commit only after processing: if the service crashes before, the message is read again.
            consumer.commit(message=msg, asynchronous=False)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
