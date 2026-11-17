# RabbitMQ vs Kafka — forces, faiblesses, limites

Comparaison qualitative, établie sur le scénario troc de la démo (même événement, mêmes abonnés, même code de
filtrage dans `subscribers.py`). Les mesures de débit et de latence sont dans [resultats.md](resultats.md),
produites par le test comparatif (`python -m benchmark`).

## Ce que la démo montre

| Critère | RabbitMQ | Kafka |
| --- | --- | --- |
| Modèle | File de messages : un message est livré, acquitté, puis **supprimé** | Journal : les messages sont **conservés** et chaque groupe de lecteurs garde sa position |
| Filtrage | Fait par le courtier : la file n'est liée qu'aux catégories suivies (exchange `topic`) | Aucun routage : le service lit tout le topic et filtre lui-même |
| Consommateur arrêté | Les messages attendent dans la file durable, livrés au redémarrage | Les messages restent dans le journal, le groupe reprend à sa dernière position |
| Consommateur qui plante | Connexion coupée → message non acquitté redistribué tout de suite | Partitions bloquées jusqu'à la fin de la session (45 s par défaut, 10 s dans la démo) |
| Message illisible | File d'échec intégrée (dead-letter exchange), il suffit de le rejeter | Pas de file d'échec intégrée : le service doit le recopier lui-même dans un topic d'échec |
| Rejeu de l'historique | Impossible : un message acquitté est supprimé | Natif : un nouveau groupe relit tout depuis le début |
| Ordre des messages | Ordre de la file, pour un seul consommateur | Garanti par partition seulement (ici, par catégorie grâce à la clé) |
| Supervision | Interface d'administration web incluse (files, messages en attente) | Outils en ligne de commande dans l'image ; interface web à ajouter à part |

## Avantages

| RabbitMQ | Kafka |
| --- | --- |
| Routage riche dans le courtier (topic, fanout, en-têtes) : chaque service ne reçoit que ce qui le concerne | Historique conservé : rejeu, ajout tardif d'un nouveau service, audit |
| File d'échec, accusés de réception et redistribution intégrés | Plusieurs groupes lisent le même flux indépendamment, sans se gêner |
| Interface d'administration prête à l'emploi, prise en main rapide | Conçu pour de gros volumes, répartis sur des partitions |
| Adapté aux tâches à exécuter une fois (envoyer un e-mail, traiter une commande) | Adapté aux flux d'événements (statistiques, recommandations, suivi d'activité) |

## Inconvénients

| RabbitMQ | Kafka |
| --- | --- |
| Pas de rejeu : une fois traité, un message a disparu | Pas de routage : chaque consommateur lit tout et filtre |
| Une file très remplie dégrade le courtier : il est fait pour des files qui se vident | Pas de file d'échec ni de redistribution message par message intégrées |
| Ordre global perdu dès qu'il y a plusieurs consommateurs sur une file | Notions plus nombreuses à maîtriser (partitions, clés, groupes, positions) |
| | Reprise après plantage d'un consommateur plus lente (délai de session) |

## Limites de la démo

- Un seul nœud pour chaque bus, sans réplication : la tolérance aux pannes d'un courtier n'est pas démontrée.
- Aucun volume Docker : tout est perdu à l'arrêt des conteneurs (choix volontaire pour repartir d'un état propre).
- Pas d'authentification ni de chiffrement entre services et courtiers (identifiants par défaut, réseau local).
- Les abonnés sont en mémoire : pas de base de données, pas de vrais e-mails.
- Débit et latence mesurés sur un poste de travail, un nœud par bus, avec des clients Python différents (pika écrit
  en Python, confluent-kafka en C) : seuls les ordres de grandeur sont significatifs (voir [resultats.md](resultats.md)).

## Pour La Petite Maison de l'Épouvante

Le besoin du troc (« prévenir les inscrits intéressés par un nouvel article ») est une tâche à faire une fois par
message, avec un filtrage par catégorie : c'est le cas d'usage naturel de RabbitMQ. Kafka devient intéressant si la
plateforme veut garder l'historique des propositions pour le rejouer (nouveau service de recommandation,
statistiques) ou si le volume d'événements devient très important.

Le test comparatif le confirme : Kafka écoule de l'ordre de 36 fois plus de messages par seconde, mais RabbitMQ
livre chaque message en quelques millisecondes contre plusieurs dizaines pour Kafka en rafale. Au volume du troc
(quelques propositions par minute), le débit n'est pas un critère ; la rapidité de notification et le routage par
catégorie le sont, ce qui fait pencher vers RabbitMQ.
