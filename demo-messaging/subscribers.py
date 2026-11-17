"""Subscribers and notification rules, shared by the RabbitMQ and Kafka notification services."""

from event import parse_event

# Demo data: subscribers and their interests (in memory, no database).
SUBSCRIBERS = {
    "Alice": ["figurines", "affiches"],
    "Bastien": ["jeux"],
    "Chloe": ["figurines", "livres"],
}


def categories(subscribers: dict[str, list[str]]) -> list[str]:
    """Every category at least one subscriber follows."""
    return sorted({c for interests in subscribers.values() for c in interests})


def recipients(event: dict, subscribers: dict[str, list[str]]) -> list[str]:
    return [name for name, interests in subscribers.items() if event["categorie"] in interests]


def handle(body: bytes, subscribers: dict[str, list[str]] = SUBSCRIBERS) -> list[str]:
    """Return the notifications to send; raise ValueError or TypeError if the message is invalid."""
    event = parse_event(body)
    return [
        f"Notification à {name} : « {event['titre']} » ({event['categorie']}, {event['type']})"
        for name in recipients(event, subscribers)
    ]
