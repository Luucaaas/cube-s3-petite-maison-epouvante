import json

from event import make_event
from kafka.common import GROUP, consumer_config, message_key
from kafka.notifications import group_name
from subscribers import SUBSCRIBERS, categories, handle


def test_message_key_is_the_category():
    assert message_key("figurines") == b"figurines"


def test_consumer_commits_by_hand_from_the_oldest_message():
    config = consumer_config("g")
    assert config["enable.auto.commit"] is False
    assert config["auto.offset.reset"] == "earliest"


def test_normal_service_keeps_its_group():
    assert group_name(replay=False) == GROUP


def test_replay_uses_a_new_group():
    assert group_name(replay=True, now=1000) == f"{GROUP}-rejeu-1000"
    assert group_name(replay=True, now=1000) != group_name(replay=True, now=1001)


def test_service_filters_categories_nobody_follows():
    body = json.dumps(make_event("Vase ancien", "deco", "don")).encode()
    assert "deco" not in categories(SUBSCRIBERS)
    assert handle(body) == []
