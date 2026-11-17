# CLAUDE.md — Projet Cube S3 « La Petite Maison de l'Épouvante »

Ce dépôt sert un projet d'école (CESI MAALSI) : une soutenance de 20 min devant un jury, avec 4 démos live.
Le code est une **démo**, pas le produit. Il doit être minimal, lisible, et fonctionner à coup sûr devant le jury.

## Avant toute chose

1. Lire `docs/contrats/choix-techniques.md` : technologies et étapes du pipeline **figées**. Ne pas proposer d'autres outils.
2. Demander à l'utilisateur sur quelle issue GitHub il travaille. Travailler uniquement dans le périmètre de cette issue.
3. Vérifier qui est l'utilisateur (Lucas, Maxime ou Marie) et ne modifier que ses fichiers (tableau ci-dessous).

## Qui possède quoi

Ne jamais modifier les fichiers d'un autre membre. Si un changement chez un autre est nécessaire, l'écrire dans l'issue et continuer avec une hypothèse raisonnable.

| Chemin | Propriétaire |
| --- | --- |
| `demo-cicd/app/`, `demo-cicd/tests/`, `demo-cicd/Dockerfile`, `demo-cicd/requirements*.txt` | Commun (issue #1) ; ensuite modifications par PR approuvée par Lucas **et** Maxime |
| `demo-cicd/helm/` | Version minimale commune (issue #1) ; ensuite Maxime, sans changer le nom de release `troc`, le port ni la route `/health` |
| `.gitlab-ci.yml`, `.github/workflows/mirror-gitlab.yml` | Lucas |
| `.github/workflows/ci.yml`, `demo-cicd/monitoring/` | Maxime |
| `demo-messaging/` | Marie |
| `docs/contrats/` | Les 3 (PR approuvée par les deux autres) |
| `docs/schemas/` | Chacun ses schémas (préfixe du nom de fichier = prénom) |
| `presentation/`, `journal/` | Lucas (harmonisation) ; chacun peut ajouter |

## Les deux démos

### Démo CI/CD — `demo-cicd/`

Micro-service FastAPI de l'espace troc, données en mémoire (pas de base de données).

| Route | Rôle |
| --- | --- |
| `GET /health` | `{"status": "ok"}` — utilisé par le test de fumée |
| `GET /articles` | Liste des articles proposés à l'échange |
| `POST /articles` | Propose un article : `{"titre": str, "categorie": str, "type": "echange" \| "don"}` → 201 + article avec `id` |
| `GET /articles/{id}` | Détail, 404 si inconnu |

Les deux pipelines (GitLab CI et GitHub Actions) implémentent **les mêmes étapes, dans le même ordre**, avec les mêmes noms de jobs (voir le contrat). Le but est de comparer les plateformes, pas les pipelines.

### Démo bus de messages — `demo-messaging/`

Scénario : un utilisateur propose un goodie → événement publié → le service de notifications prévient les inscrits dont un centre d'intérêt correspond.

Format de l'événement (identique pour RabbitMQ et Kafka) :

```json
{"event": "article.propose", "id": "uuid", "titre": "Figurine Orc", "categorie": "figurines", "type": "echange", "date": "ISO 8601"}
```

- RabbitMQ : exchange `troc` de type topic, clé de routage `article.propose.<categorie>`.
- Kafka : topic `troc.articles`, clé du message = `categorie`.
- Le test comparatif envoie la même rafale de messages aux deux et mesure débit et latence. Les chiffres viennent des mesures, jamais inventés.

## Ordre de travail et dépendances

- L'issue **#1** (micro-service + tests + Dockerfile + chart Helm minimal) est la seule dont dépendent les autres. Tant qu'elle n'est pas fusionnée, Lucas et Maxime écrivent leur pipeline contre l'arborescence décrite ici (`demo-cicd/app/main.py`, `demo-cicd/tests/`, `demo-cicd/Dockerfile`, `demo-cicd/helm/`).
- Chart Helm : release `troc`, service sur le port 8000, sonde sur `/health`. Commande de déploiement commune : `helm upgrade --install troc demo-cicd/helm --set image.repository=<registre>/<image> --set image.tag=<sha> --wait`.
- Noms de jobs identiques dans les deux pipelines : `lint`, `test`, `secrets`, `sast`, `deps`, `build`, `scan-image`, `deploy`, `smoke`, `dast`.
- Marie ne dépend de personne.

## Définition de « fini » pour une issue

- PR fusionnée dans `develop`, pipeline(s) vert(s), `ruff check . && pytest` OK.
- Pour un schéma : fichier `.drawio` dans `docs/schemas/` + export PNG à côté.
- Une ligne ajoutée dans `journal/journal.md` : date, issue, ce qui a été fait, difficulté éventuelle (sert au bilan de la soutenance).

## Conventions

- Python 3.12, dépendances dans `requirements.txt` (versions épinglées), `ruff` et `pytest` doivent passer avant chaque commit : `ruff check . && pytest`.
- Code et commentaires simples, en anglais pour le code, en français pour la documentation.
- Aucun secret dans le dépôt : variables d'environnement ou secrets CI uniquement (Gitleaks bloque le pipeline).
- Images Docker : base `python:3.12-slim`, utilisateur non root.

## Git

- Partir de `develop` : `git switch develop && git pull && git switch -c prenom/sujet`.
- Commits courts en français, une PR par issue vers `develop`, `Closes #<issue>` dans la description.
- Ne jamais pousser directement sur `main` ni `develop`. Ne jamais faire de `push --force` sur une branche partagée.
- `develop` → `main` uniquement quand les deux pipelines sont verts (décision à trois).

## Si quelque chose bloque

Ne pas attendre : noter le blocage en commentaire de l'issue, prendre l'hypothèse la plus simple, continuer.
