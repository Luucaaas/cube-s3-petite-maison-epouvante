"""Publish an "article.propose" event to the "troc.articles" topic.

Usage (from demo-messaging/):
    python -m kafka.producer "Figurine Orc" figurines echange
    python -m kafka.producer --invalide figurines   # broken message, goes to the failed topic
"""

import argparse
import json

from confluent_kafka import Producer

from event import make_event
from kafka.common import TOPIC, ensure_topics, message_key, producer_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Propose an article on the troc.articles topic.")
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

    ensure_topics()
    producer = Producer(producer_config())
    producer.produce(TOPIC, key=message_key(args.categorie), value=body)
    producer.flush(10)
    print(f"[producteur] {TOPIC} (clé {args.categorie}) -> {body.decode()}")


if __name__ == "__main__":
    main()
