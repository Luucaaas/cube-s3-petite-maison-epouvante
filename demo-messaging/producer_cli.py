"""Command line shared by the RabbitMQ and Kafka producers: same arguments, same message."""

import argparse
import json

from event import TYPES, make_event

INVALID_BODY = b"ceci n'est pas un evenement"


def message_body(titre: str, categorie: str, type_: str) -> bytes:
    """The JSON event to publish."""
    return json.dumps(make_event(titre, categorie, type_), ensure_ascii=False).encode()


def parse_args(description: str, argv: list[str] | None = None) -> tuple[str, bytes]:
    """Read the command line; return the category and the message body."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("titre", nargs="?", default="Figurine Orc")
    parser.add_argument("categorie", nargs="?", default="figurines")
    parser.add_argument("type", nargs="?", default="echange", choices=TYPES)
    parser.add_argument("--invalide", metavar="CATEGORIE", help="send a malformed message in this category")
    args = parser.parse_args(argv)
    if args.invalide:
        return args.invalide, INVALID_BODY
    return args.categorie, message_body(args.titre, args.categorie, args.type)
