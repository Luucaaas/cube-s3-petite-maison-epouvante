# Démo bus de messages — RabbitMQ vs Kafka

Scénario : un utilisateur propose un goodie → l'événement `article.propose` est publié → le service de notifications
prévient les inscrits dont un centre d'intérêt correspond. Le même scénario tourne sur RabbitMQ puis sur Kafka.

Ce dossier contient l'environnement des deux bus en conteneurs (un nœud chacun, pour une démo locale).

## Prérequis

- Docker Desktop (ou Docker Engine) avec Docker Compose v2 : `docker compose version`.
- Ports libres sur la machine : `5672`, `15672` (RabbitMQ), `9092` (Kafka).

## Lancer

Depuis le dossier `demo-messaging/` :

```bash
docker compose up -d
docker compose ps
```

Attendre que les deux services soient `healthy` (environ 20 à 30 s au premier lancement, le temps de télécharger les images).

| Service | Image | Accès |
| --- | --- | --- |
| RabbitMQ | `rabbitmq:3.13-management` | AMQP : `localhost:5672` · admin web : <http://localhost:15672> (`guest` / `guest`) |
| Kafka | `apache/kafka:3.8.0` (mode KRaft, sans ZooKeeper) | bootstrap : `localhost:9092` |

Les identifiants RabbitMQ `guest` / `guest` ne servent qu'en local. Pour les changer, définir `RABBITMQ_USER` et
`RABBITMQ_PASSWORD` dans l'environnement (ou dans un fichier `.env`, ignoré par Git) avant `docker compose up`.

## Vérifier que tout répond

RabbitMQ :

```bash
docker compose exec rabbitmq rabbitmq-diagnostics -q ping
```

Kafka : créer le topic de la démo puis le lister.

```bash
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic troc.articles --partitions 3 --replication-factor 1
```

```bash
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

(Le topic est aussi créé automatiquement au premier message envoyé. Kafka affiche un avertissement sur le point dans
le nom du topic : sans effet ici.)

> Windows + Git Bash : Git Bash réécrit `/opt/kafka/...` en chemin Windows et la commande échoue
> (`no such file or directory`). Lancer d'abord `export MSYS_NO_PATHCONV=1`, ou utiliser PowerShell.

## Conventions de la démo

Format de l'événement (identique pour les deux bus) :

```json
{"event": "article.propose", "id": "uuid", "titre": "Figurine Orc", "categorie": "figurines", "type": "echange", "date": "ISO 8601"}
```

- RabbitMQ : exchange `troc` de type `topic`, clé de routage `article.propose.<categorie>`.
- Kafka : topic `troc.articles`, clé du message = `categorie`.

## Arrêter

```bash
docker compose down
```

Aucun volume n'est déclaré : les messages et topics sont perdus à l'arrêt, ce qui donne un état propre à chaque démo.
