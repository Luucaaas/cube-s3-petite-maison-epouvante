import json

import pytest

from event import FIELDS, make_event, parse_event
from rabbitmq.common import routing_key
from rabbitmq.notifications import binding_keys, handle, recipients

SUBSCRIBERS = {"Alice": ["figurines", "affiches"], "Bastien": ["jeux"], "Chloe": ["figurines"]}


def test_make_event_has_contract_fields():
    event = make_event("Figurine Orc", "figurines", "echange")
    assert tuple(event) == FIELDS
    assert event["event"] == "article.propose"


def test_make_event_rejects_unknown_type():
    with pytest.raises(ValueError):
        make_event("Figurine Orc", "figurines", "vente")


def test_routing_key_contains_category():
    assert routing_key("figurines") == "article.propose.figurines"


def test_binding_keys_cover_each_interest_once():
    assert binding_keys(SUBSCRIBERS) == [
        "article.propose.affiches",
        "article.propose.figurines",
        "article.propose.jeux",
    ]


def test_recipients_filter_by_interest():
    assert recipients({"categorie": "figurines"}, SUBSCRIBERS) == ["Alice", "Chloe"]
    assert recipients({"categorie": "livres"}, SUBSCRIBERS) == []


def test_handle_builds_one_notification_per_recipient():
    body = json.dumps(make_event("Figurine Orc", "jeux", "don")).encode()
    assert handle(body, SUBSCRIBERS) == ["Notification à Bastien : « Figurine Orc » (jeux, don)"]


@pytest.mark.parametrize("body", [b"pas du json", b"[]", b'{"event": "article.propose"}'])
def test_invalid_messages_are_rejected(body):
    with pytest.raises((ValueError, TypeError)):
        parse_event(body)
