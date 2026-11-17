"""Event "article.propose", shared by the RabbitMQ and Kafka demos."""

import json
import uuid
from datetime import UTC, datetime

EVENT_NAME = "article.propose"
TYPES = ("echange", "don")
FIELDS = ("event", "id", "titre", "categorie", "type", "date")


def make_event(titre: str, categorie: str, type_: str) -> dict:
    """Build a new event for an article proposed by a user."""
    if type_ not in TYPES:
        raise ValueError(f"type must be one of {TYPES}, got {type_!r}")
    return {
        "event": EVENT_NAME,
        "id": str(uuid.uuid4()),
        "titre": titre,
        "categorie": categorie,
        "type": type_,
        "date": datetime.now(UTC).isoformat(),
    }


def parse_event(body: bytes | str) -> dict:
    """Decode a message body; raise ValueError or TypeError if it is not a valid event."""
    try:
        event = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"not JSON: {exc}") from exc
    if not isinstance(event, dict):
        raise TypeError("event must be a JSON object")
    missing = [field for field in FIELDS if field not in event]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if event["event"] != EVENT_NAME:
        raise ValueError(f"unexpected event {event['event']!r}")
    return event
