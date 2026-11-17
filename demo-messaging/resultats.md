# Résultats du test comparatif RabbitMQ vs Kafka

Fichier généré par `python -m benchmark` le 17/11/2026 à 16:12 : les chiffres viennent
des mesures, aucun n'est saisi à la main. Relancer la commande pour les mettre à jour.

## Conditions de mesure

- Machine : Windows 11, 8 cœurs logiques, Python 3.12.0.
- Courtiers : ceux de `docker-compose.yml` (RabbitMQ 3.13, Kafka 3.8 en mode KRaft), un nœud chacun, sur la même
  machine que le script (Docker Desktop).
- Rafale : 10 000 événements `article.propose` au format du contrat (catégorie `bench`), préparés avant le
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

Médiane de 3 essais de 10 000 messages par bus.

| Mesure | RabbitMQ | Kafka |
| --- | --- | --- |
| Débit d'envoi | 1 807 msg/s | 80 759 msg/s |
| Débit de bout en bout | 1 806 msg/s | 65 655 msg/s |
| Latence médiane | 2.7 ms | 68.7 ms |
| Latence 95e centile | 11.4 ms | 77.3 ms |
| Latence maximale | 62.0 ms | 78.3 ms |
| Messages perdus | 0 | 0 |

### Détail des essais

| Bus | Essai | Débit d'envoi | Débit bout en bout | Médiane | 95e centile | Max |
| --- | --- | --- | --- | --- | --- | --- |
| RabbitMQ | 1 | 1 807 msg/s | 1 806 msg/s | 2.3 ms | 9.7 ms | 62.0 ms |
| RabbitMQ | 2 | 1 742 msg/s | 1 742 msg/s | 2.7 ms | 11.4 ms | 55.2 ms |
| RabbitMQ | 3 | 1 874 msg/s | 1 874 msg/s | 3.0 ms | 26.7 ms | 75.3 ms |
| Kafka | 1 | 52 849 msg/s | 51 856 msg/s | 27.8 ms | 56.1 ms | 57.7 ms |
| Kafka | 2 | 81 035 msg/s | 65 655 msg/s | 105.0 ms | 110.0 ms | 110.5 ms |
| Kafka | 3 | 80 759 msg/s | 76 765 msg/s | 68.7 ms | 77.3 ms | 78.3 ms |

## Lecture

Analyse rédigée à partir de la mesure du 17/11/2026 ; elle est conservée si l'on relance la commande, mais ses
chiffres se rapportent à cette mesure-là.

**Débit : Kafka nettement devant.** Kafka a reçu de 51 856 à 76 765 messages par seconde selon l'essai,
RabbitMQ environ 1 800 (de 1 742 à 1 874), soit environ 36 fois plus en médiane (65 655 contre 1 806). Kafka regroupe les
messages en lots, côté envoi comme côté lecture ; RabbitMQ traite les messages un par un.

**Latence : RabbitMQ nettement devant.** La moitié des messages RabbitMQ arrivent en moins de 3 ms
(médiane de 2,3 à 3,0 ms) ; côté Kafka, la médiane varie de 27,8 à 105,0 ms selon l'essai. Dans une rafale,
Kafka attend de remplir un lot avant d'envoyer, et le consommateur lit un journal qui se remplit plus vite qu'il
ne le vide : les messages attendent leur tour. RabbitMQ, plus lent à l'envoi, ne laisse jamais la file
s'allonger, donc chaque message est livré presque aussitôt.

**Fiabilité : égalité.** Aucun message perdu sur les 30 000 envoyés à chaque bus (3 essais de 10 000).

**Précautions de lecture.**

- Le client Python compte beaucoup : pika est écrit en Python et envoie chaque message séparément, alors que
  confluent-kafka s'appuie sur une bibliothèque en C qui travaille par lots. Avec un autre client (Java, ou pika
  en mode asynchrone), l'écart de débit serait différent. Le test compare donc les deux chaînes complètes
  telles qu'utilisées dans la démo, pas les seuls courtiers.
- Un seul nœud par bus, sur un poste de travail sous Docker Desktop, avec le script sur la même machine :
  les valeurs absolues ne disent rien d'un déploiement en production, seuls les ordres de grandeur comptent.
- La latence Kafka varie beaucoup d'un essai à l'autre (de 27,8 à 105,0 ms en médiane) : elle dépend du moment
  où chaque lot part. Trois essais suffisent pour l'ordre de grandeur, pas pour une valeur précise.

**Pour La Petite Maison de l'Épouvante.** Le troc produit quelques propositions par minute, très loin des milliers
par seconde mesurés ici : les deux bus suffisent largement. Ce qui compte pour prévenir un inscrit, c'est une
notification rapide et le routage par catégorie, deux points forts de RabbitMQ. Le débit de Kafka et son
historique rejouable deviendraient utiles pour de gros flux d'événements (suivi d'activité, statistiques,
recommandations).
