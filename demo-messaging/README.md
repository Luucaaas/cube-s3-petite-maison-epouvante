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

## Scénario RabbitMQ

Installer les dépendances Python (Python 3.12), une fois, depuis `demo-messaging/` :

```bash
pip install -r requirements-dev.txt
```

| Fichier | Rôle |
| --- | --- |
| `event.py` | Construit et vérifie l'événement `article.propose` (partagé avec Kafka) |
| `rabbitmq/producer.py` | Publie un article sur l'exchange `troc`, clé `article.propose.<categorie>`, message persistant |
| `rabbitmq/notifications.py` | Service de notifications : file durable `notifications`, abonnés et centres d'intérêt en mémoire |

Abonnés de démo : Alice (figurines, affiches), Bastien (jeux), Chloe (figurines, livres). La file `notifications` n'est
liée qu'aux catégories suivies : un article `deco` n'arrive jamais au service, c'est RabbitMQ qui filtre.

### 1. Filtrage par centre d'intérêt

Terminal 1 (le service, à laisser ouvert) :

```bash
python -m rabbitmq.notifications
```

Terminal 2 :

```bash
python -m rabbitmq.producer "Figurine Orc" figurines echange
```

```bash
python -m rabbitmq.producer "Vase ancien" deco don
```

Résultat attendu : Alice et Chloe sont notifiées pour la figurine, personne pour le vase.

### 2. Le consommateur tombe : les messages attendent

1. Arrêter le service (Ctrl+C dans le terminal 1).
2. Publier deux articles depuis le terminal 2 :

```bash
python -m rabbitmq.producer "Affiche Alien" affiches don
```

```bash
python -m rabbitmq.producer "Dracula" livres echange
```

3. Montrer l'interface d'admin (<http://localhost:15672>, onglet *Queues*) : la file `notifications` contient
   2 messages *Ready*, aucun n'est perdu.
4. Relancer le service : il rattrape les 2 messages dans l'ordre.

Le service n'acquitte un message qu'après l'avoir traité : s'il plante en plein traitement, RabbitMQ le redistribue.

### 3. Message en échec : la file `notifications.echec`

```bash
python -m rabbitmq.producer --invalide figurines
```

Le service rejette le message illisible au lieu de bloquer ou de le perdre : il part dans la file
`notifications.echec` (dead-letter exchange `troc.echec`), visible dans l'interface d'admin pour analyse.

## Scénario Kafka

Même scénario, mêmes abonnés (`subscribers.py`), même format d'événement, mais sur le topic `troc.articles`
(clé du message = catégorie). Les dépendances sont celles de `requirements-dev.txt` (bibliothèque `confluent-kafka`).

| Fichier | Rôle |
| --- | --- |
| `kafka/producer.py` | Publie un article sur `troc.articles`, clé = catégorie |
| `kafka/notifications.py` | Service de notifications, groupe de consommateurs `notifications` ; `--rejouer` relit tout l'historique |

Différence visible : Kafka ne route pas. Le service reçoit **toutes** les catégories et filtre lui-même (« personne
n'est intéressé, ignoré » pour un article `deco`). Chaque ligne affiche la partition et la position du message
(`p0 #2`) : l'ordre n'est garanti qu'à l'intérieur d'une partition, donc d'une catégorie.

### 1. Filtrage par centre d'intérêt

Terminal 1 :

```bash
python -m kafka.notifications
```

Terminal 2 :

```bash
python -m kafka.producer "Figurine Orc" figurines echange
```

```bash
python -m kafka.producer "Vase ancien" deco don
```

### 2. Le consommateur tombe : il reprend là où il s'était arrêté

1. Ctrl+C dans le terminal 1.
2. Publier deux articles et un message invalide depuis le terminal 2 :

```bash
python -m kafka.producer "Affiche Alien" affiches don
```

```bash
python -m kafka.producer "Dracula" livres echange
```

```bash
python -m kafka.producer --invalide figurines
```

3. Montrer les 3 messages non lus (colonne `LAG`) :

```bash
docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group notifications
```

4. Relancer le service : il lit les 3 messages, notifie Alice et Chloe, et copie le message invalide dans le topic
   `troc.articles.echec` (Kafka n'a pas de file d'échec intégrée : c'est le service qui s'en charge).

Si le service a planté au lieu d'être arrêté par Ctrl+C, Kafka attend la fin de sa session (10 s dans la démo,
45 s par défaut) avant de redonner ses partitions : le service relancé reste muet pendant ce délai.

### 3. Rejeu de l'historique

```bash
python -m kafka.notifications --rejouer
```

Un nouveau groupe de consommateurs relit **tous** les messages depuis le début, déjà lus ou non, sans changer la
position du service normal. Avec RabbitMQ, c'est impossible : un message acquitté est supprimé de la file.

Le tableau des forces et faiblesses des deux bus est dans [comparatif.md](comparatif.md).

## Test comparatif (débit et latence)

`benchmark.py` envoie la **même rafale** d'événements `article.propose` à RabbitMQ puis à Kafka, avec un
consommateur démarré avant l'envoi, et mesure le débit et la latence de chaque message. Les messages de test ont
la catégorie `bench` et passent par une file et un topic dédiés, supprimés à la fin : ils ne gênent pas les
scénarios de démo.

Les deux conteneurs doivent tourner. Depuis `demo-messaging/` (environ 1 minute) :

```bash
python -m benchmark
```

Par défaut : 500 messages d'échauffement non comptés, puis 3 essais de 10 000 messages par bus. Le script écrit
[resultats.md](resultats.md) (conditions de mesure, tableau, détail des essais) et conserve la partie « Lecture »
déjà rédigée. Essai rapide sans écrire de fichier :

```bash
python -m benchmark --messages 2000 --runs 1 --resultats ""
```

## Arrêter

```bash
docker compose down
```

Aucun volume n'est déclaré : les messages et topics sont perdus à l'arrêt, ce qui donne un état propre à chaque démo.
