"""Comparative test: the same burst of "article.propose" events sent to RabbitMQ and to Kafka.

For each broker, a consumer is started first, then the producer sends N messages as fast as it can.
Each message carries its send time in a header (the body stays the contract event), so the consumer
measures the latency of every message. Results are written to resultats.md: no number is typed by hand.

Usage (from demo-messaging/, both brokers running):
    python -m benchmark                       # 3 runs of 10 000 messages per broker
    python -m benchmark --messages 2000 --runs 1 --resultats ""   # quick try, nothing written
"""

import argparse
import json
import os
import platform
import statistics
import threading
import time
import uuid
from datetime import datetime

from event import make_event

CATEGORY = "bench"  # nobody follows it: the demo notification services never see these messages
TIMEOUT_S = 120


# ---------- measures (pure functions, unit tested) ----------

def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile of a non-empty list."""
    ordered = sorted(values)
    rank = max(1, round(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def summarize(n: int, t_first_send: int, t_last_send: int, t_last_recv: int, latencies_ns: list[int]) -> dict:
    """Throughputs in messages/s and latencies in ms, from perf_counter_ns timestamps."""
    lat_ms = [x / 1e6 for x in latencies_ns]
    return {
        "messages": n,
        "recus": len(latencies_ns),
        "debit_envoi": n / ((t_last_send - t_first_send) / 1e9),
        "debit_bout_en_bout": len(latencies_ns) / ((t_last_recv - t_first_send) / 1e9),
        "latence_mediane": statistics.median(lat_ms),
        "latence_p95": percentile(lat_ms, 95),
        "latence_max": max(lat_ms),
    }


def median_of_runs(runs: list[dict]) -> dict:
    keys = ("debit_envoi", "debit_bout_en_bout", "latence_mediane", "latence_p95", "latence_max")
    return {k: statistics.median(r[k] for r in runs) for k in keys}


def bodies(n: int) -> list[bytes]:
    """The burst: n contract events, prepared before timing starts."""
    return [
        json.dumps(make_event(f"Article {i}", CATEGORY, "echange"), ensure_ascii=False).encode()
        for i in range(n)
    ]


# ---------- RabbitMQ ----------

def run_rabbitmq(payloads: list[bytes]) -> dict:
    import pika

    from rabbitmq.common import EXCHANGE, connect, declare_exchange, routing_key

    n = len(payloads)
    queue = f"bench.{uuid.uuid4().hex[:8]}"
    latencies, last_recv, ready = [], [0], threading.Event()

    setup = connect()
    channel = setup.channel()
    declare_exchange(channel)
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(queue=queue, exchange=EXCHANGE, routing_key=routing_key(CATEGORY))

    def consume():
        conn = connect()
        ch = conn.channel()
        ch.basic_qos(prefetch_count=100)

        def on_message(c, method, properties, body):
            now = time.perf_counter_ns()
            latencies.append(now - properties.headers["sent_ns"])
            last_recv[0] = now
            c.basic_ack(delivery_tag=method.delivery_tag)
            if len(latencies) == n:
                c.stop_consuming()

        ch.basic_consume(queue=queue, on_message_callback=on_message)
        ready.set()
        ch.start_consuming()
        conn.close()

    consumer = threading.Thread(target=consume, daemon=True)
    consumer.start()
    ready.wait(10)

    producer = connect()
    pch = producer.channel()
    t_first = time.perf_counter_ns()
    for body in payloads:
        pch.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key(CATEGORY),
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                headers={"sent_ns": time.perf_counter_ns()},
            ),
        )
    t_last_send = time.perf_counter_ns()
    consumer.join(TIMEOUT_S)
    producer.close()
    channel.queue_delete(queue=queue)
    setup.close()
    return summarize(n, t_first, t_last_send, last_recv[0], latencies)


# ---------- Kafka ----------

def run_kafka(payloads: list[bytes]) -> dict:
    from confluent_kafka import Consumer, Producer
    from confluent_kafka.admin import AdminClient, NewTopic

    from kafka.common import (
        PARTITIONS,
        bootstrap,
        consumer_config,
        message_key,
        producer_config,
    )

    n = len(payloads)
    topic = f"troc.bench.{uuid.uuid4().hex[:8]}"
    admin = AdminClient({"bootstrap.servers": bootstrap()})
    admin.create_topics([NewTopic(topic, num_partitions=PARTITIONS, replication_factor=1)])[topic].result()
    latencies, last_recv, ready, stop = [], [0], threading.Event(), threading.Event()

    def consume():
        consumer = Consumer({**consumer_config(f"bench-{topic}"), "enable.auto.commit": True})
        consumer.subscribe([topic], on_assign=lambda c, parts: ready.set())
        while len(latencies) < n and not stop.is_set():
            msg = consumer.poll(0.1)
            if msg is None or msg.error():
                continue
            now = time.perf_counter_ns()
            latencies.append(now - int(dict(msg.headers())["sent_ns"]))
            last_recv[0] = now
        consumer.close()

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    ready.wait(30)
    time.sleep(1)  # let the consumer fetch its starting offsets

    producer = Producer(producer_config())
    key = message_key(CATEGORY)
    t_first = time.perf_counter_ns()
    for body in payloads:
        while True:
            try:
                producer.produce(topic, key=key, value=body, headers=[("sent_ns", str(time.perf_counter_ns()))])
                break
            except BufferError:  # local queue full: let it drain
                producer.poll(0.01)
        producer.poll(0)
    producer.flush(TIMEOUT_S)
    t_last_send = time.perf_counter_ns()
    thread.join(TIMEOUT_S)
    stop.set()
    admin.delete_topics([topic])
    return summarize(n, t_first, t_last_send, last_recv[0], latencies)


# ---------- report ----------

def fmt(value: float, unit: str) -> str:
    return f"{value:,.0f} {unit}".replace(",", " ") if unit == "msg/s" else f"{value:.1f} {unit}"


def markdown(results: dict[str, list[dict]], n: int, runs: int) -> str:
    rows = [
        "| Mesure | " + " | ".join(results) + " |",
        "| --- | " + " | ".join("---" for _ in results) + " |",
    ]
    medians = {name: median_of_runs(r) for name, r in results.items()}
    labels = [
        ("debit_envoi", "Débit d'envoi", "msg/s"),
        ("debit_bout_en_bout", "Débit de bout en bout", "msg/s"),
        ("latence_mediane", "Latence médiane", "ms"),
        ("latence_p95", "Latence 95e centile", "ms"),
        ("latence_max", "Latence maximale", "ms"),
    ]
    for key, label, unit in labels:
        rows.append(f"| {label} | " + " | ".join(fmt(medians[b][key], unit) for b in results) + " |")
    lost = {b: sum(r["messages"] - r["recus"] for r in rs) for b, rs in results.items()}
    rows.append("| Messages perdus | " + " | ".join(str(lost[b]) for b in results) + " |")

    detail = ["| Bus | Essai | Débit d'envoi | Débit bout en bout | Médiane | 95e centile | Max |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for b, rs in results.items():
        for i, r in enumerate(rs, 1):
            detail.append(
                f"| {b} | {i} | {fmt(r['debit_envoi'], 'msg/s')} | {fmt(r['debit_bout_en_bout'], 'msg/s')} | "
                f"{fmt(r['latence_mediane'], 'ms')} | {fmt(r['latence_p95'], 'ms')} | {fmt(r['latence_max'], 'ms')} |"
            )
    return (
        f"Médiane de {runs} essais de {n:,} messages par bus.".replace(",", " ") + "\n\n"
        + "\n".join(rows) + "\n\n### Détail des essais\n\n" + "\n".join(detail) + "\n"
    )


def write_report(path: str, table: str, n: int, runs: int) -> None:
    text = f"""# Résultats du test comparatif RabbitMQ vs Kafka

Fichier généré par `python -m benchmark` le {datetime.now():%d/%m/%Y à %H:%M} : les chiffres viennent
des mesures, aucun n'est saisi à la main. Relancer la commande pour les mettre à jour.

## Conditions de mesure

- Machine : {platform.system()} {platform.release()}, {os.cpu_count()} cœurs logiques, Python {platform.python_version()}.
- Courtiers : ceux de `docker-compose.yml` (RabbitMQ 3.13, Kafka 3.8 en mode KRaft), un nœud chacun, sur la même
  machine que le script (Docker Desktop).
- Rafale : {n:,} événements `article.propose` au format du contrat (catégorie `bench`), préparés avant le
  chronomètre, envoyés le plus vite possible par un seul producteur ; un seul consommateur, démarré avant l'envoi.
- RabbitMQ : exchange `troc`, clé `article.propose.bench`, file durable dédiée, messages persistants, acquittement
  manuel de chaque message (100 messages en vol au plus), pas de confirmation de publication.
- Kafka : topic dédié de 3 partitions, clé = catégorie, `acks=all`, réglages par défaut de la bibliothèque
  (envoi par lots).
- Clients Python : pika 1.4.4 (écrit en Python) pour RabbitMQ, confluent-kafka 2.16.1 (sur librdkafka, écrit
  en C) pour Kafka ; producteur et consommateur dans le même processus, chacun dans son fil d'exécution.
- Latence : heure d'envoi placée dans un en-tête de chaque message, comparée à l'heure de réception
  (même processus, même horloge).
- Débit d'envoi : messages envoyés par seconde côté producteur. Débit de bout en bout : messages reçus par seconde,
  du premier envoi à la dernière réception.

## Résultats

{table}
""".replace(f"{n:,}", f"{n:,}".replace(",", " "))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + reading_section(path))


def reading_section(path: str) -> str:
    """Keep the hand-written "Lecture" section of an existing report, so a new run does not erase it."""
    default = "## Lecture\n\nÀ compléter après la mesure (voir `comparatif.md`).\n"
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        old = f.read()
    start = old.find("## Lecture")
    return old[start:] if start >= 0 else default


def main() -> None:
    parser = argparse.ArgumentParser(description="Same burst sent to RabbitMQ and Kafka.")
    parser.add_argument("--messages", type=int, default=10_000)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--resultats", default="resultats.md", help='output file ("" = print only)')
    args = parser.parse_args()

    payloads = bodies(args.messages)
    print("[bench] échauffement (500 messages par bus, non compté)")
    run_rabbitmq(payloads[:500])
    run_kafka(payloads[:500])

    results = {"RabbitMQ": [], "Kafka": []}
    for i in range(1, args.runs + 1):
        for name, run in (("RabbitMQ", run_rabbitmq), ("Kafka", run_kafka)):
            r = run(payloads)
            results[name].append(r)
            print(f"[bench] essai {i} {name}: {r['recus']}/{r['messages']} reçus, "
                  f"{r['debit_bout_en_bout']:.0f} msg/s, médiane {r['latence_mediane']:.1f} ms")
    table = markdown(results, args.messages, args.runs)
    print(table)
    if args.resultats:
        write_report(args.resultats, table, args.messages, args.runs)
        print(f"[bench] résultats écrits dans {args.resultats}")


if __name__ == "__main__":
    main()
