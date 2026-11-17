import pytest

from event import parse_event
from producer_cli import INVALID_BODY, parse_args


def test_defaults_build_a_valid_event():
    categorie, body = parse_args("test", [])
    assert categorie == "figurines"
    assert parse_event(body)["titre"] == "Figurine Orc"


def test_arguments_are_used():
    categorie, body = parse_args("test", ["Catan", "jeux", "don"])
    event = parse_event(body)
    assert (categorie, event["titre"], event["type"]) == ("jeux", "Catan", "don")


def test_invalid_option_sends_a_malformed_message():
    categorie, body = parse_args("test", ["--invalide", "jeux"])
    assert categorie == "jeux"
    assert body == INVALID_BODY
    with pytest.raises(ValueError):
        parse_event(body)
