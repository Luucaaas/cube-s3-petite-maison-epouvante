from benchmark import (
    CATEGORY,
    bodies,
    markdown,
    median_of_runs,
    percentile,
    reading_section,
    summarize,
)
from event import parse_event


def test_percentile_nearest_rank():
    values = list(range(1, 101))
    assert percentile(values, 50) == 50
    assert percentile(values, 95) == 95
    assert percentile([7.0], 95) == 7.0


def test_summarize_computes_throughput_and_latency():
    # 4 messages sent over 1 s, last one received 2 s after the first send.
    r = summarize(4, 0, 1_000_000_000, 2_000_000_000, [1_000_000, 2_000_000, 3_000_000, 10_000_000])
    assert r["debit_envoi"] == 4
    assert r["debit_bout_en_bout"] == 2
    assert r["latence_mediane"] == 2.5
    assert r["latence_max"] == 10


def test_median_of_runs():
    runs = [{"debit_envoi": v, "debit_bout_en_bout": v, "latence_mediane": v, "latence_p95": v,
             "latence_max": v} for v in (1, 5, 3)]
    assert median_of_runs(runs)["debit_envoi"] == 3


def test_burst_uses_the_contract_event():
    payloads = bodies(3)
    assert len(payloads) == 3
    assert all(parse_event(p)["categorie"] == CATEGORY for p in payloads)


def test_markdown_reports_both_brokers_and_losses():
    r = summarize(2, 0, 1_000_000_000, 1_000_000_000, [1_000_000])
    table = markdown({"RabbitMQ": [r], "Kafka": [r]}, 2, 1)
    assert "| Mesure | RabbitMQ | Kafka |" in table
    assert "| Messages perdus | 1 | 1 |" in table


def test_new_report_keeps_the_hand_written_reading(tmp_path):
    report = tmp_path / "resultats.md"
    assert "À compléter" in reading_section(str(report))
    report.write_text("# Titre\n\n## Résultats\n\nvieux chiffres\n\n## Lecture\n\nMon analyse.\n", encoding="utf-8")
    assert reading_section(str(report)) == "## Lecture\n\nMon analyse.\n"
