# Journal de bord

Une ligne par issue terminée ou par difficulté : `AAAA-MM-JJ · Prénom · #issue · ce qui a été fait / difficulté`.


2026-11-17 · Lucas · #1 · Micro-service FastAPI troc (4 routes, données en mémoire), 6 tests pytest, Dockerfile non root, chart Helm minimal `troc` ; vérifié en local (docker build, kind + helm, /health OK) / RAS : avertissement de dépréciation httpx dans Starlette, sans effet sur les tests
2026-11-17 · Maxime · #9 · Workflow GitHub Actions `ci.yml`, étapes 1 à 5 (`lint` ruff, `test` pytest, `secrets` Gitleaks, `sast` Semgrep p/python, `deps` Trivy sur requirements.txt, échec si CRITICAL), jobs enchaînés dans l'ordre du contrat ; outils vérifiés en local / pipeline GitLab (#3) pas encore écrit : versions des outils à aligner avec Lucas ; Semgrep installé par pip cassait (dépendance `pkg_resources` absente), remplacé par l'image Docker officielle
2026-11-17 · Lucas · #2 · Workflow mirror-gitlab.yml : push de main et develop vers GitLab à chaque push / test réel impossible avant fusion (le workflow doit être sur develop) ; projet GitLab et secrets à créer à la main
2026-11-17 · Marie · #16 · `demo-messaging/docker-compose.yml` (RabbitMQ 3.13 + interface d'admin, Kafka 3.8 en mode KRaft sans ZooKeeper) et README de lancement ; vérifié en local (deux services healthy, admin web OK, topic `troc.articles` créé, message envoyé et relu) / sous Git Bash, les chemins `/opt/kafka/...` sont réécrits : `MSYS_NO_PATHCONV=1` (noté dans le README)
2026-11-17 · Lucas · #3 · .gitlab-ci.yml étapes 1 à 5 (lint, test, secrets, sast, deps), mêmes versions d'outils que le pipeline GitHub de Maxime ; chaque job vérifié en local dans son image / Gitleaks : ajout de safe.directory pour lire le dépôt cloné par le runner
2026-11-17 · Lucas · #6 · Schéma du cycle DevSecOps (8 phases, sécurité et job du pipeline par phase) en draw.io + PNG, slide d'explication ; maquette faite dans Claude Design / draw.io non installé : .drawio écrit en XML, PNG rendu depuis la maquette
2026-11-17 · Lucas · #4 · Jobs build (docker-in-docker, push dans le registre GitLab, tag = SHA du commit) et scan-image (Trivy, échec si CRITICAL) ; simulé en local avec un registre Docker / image : 48 vulnérabilités HIGH, 0 CRITICAL, toutes dans la base Debian de python:3.12-slim
