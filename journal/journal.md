# Journal de bord

Une ligne par issue terminée ou par difficulté : `AAAA-MM-JJ · Prénom · #issue · ce qui a été fait / difficulté`.


2026-11-17 · Lucas · #1 · Micro-service FastAPI troc (4 routes, données en mémoire), 6 tests pytest, Dockerfile non root, chart Helm minimal `troc` ; vérifié en local (docker build, kind + helm, /health OK) / RAS : avertissement de dépréciation httpx dans Starlette, sans effet sur les tests
2026-11-17 · Lucas · #2 · Workflow mirror-gitlab.yml : push de main et develop vers GitLab à chaque push / test réel impossible avant fusion (le workflow doit être sur develop) ; projet GitLab et secrets à créer à la main
2026-11-17 · Lucas · #3 · .gitlab-ci.yml étapes 1 à 5 (lint, test, secrets, sast, deps), mêmes versions d'outils que le pipeline GitHub de Maxime ; chaque job vérifié en local dans son image / Gitleaks : ajout de safe.directory pour lire le dépôt cloné par le runner
