# Journal de bord

Une ligne par issue terminée ou par difficulté : `AAAA-MM-JJ · Prénom · #issue · ce qui a été fait / difficulté`.


2026-11-17 · Lucas · #1 · Micro-service FastAPI troc (4 routes, données en mémoire), 6 tests pytest, Dockerfile non root, chart Helm minimal `troc` ; vérifié en local (docker build, kind + helm, /health OK) / RAS : avertissement de dépréciation httpx dans Starlette, sans effet sur les tests
2026-11-17 · Maxime · #9 · Workflow GitHub Actions `ci.yml`, étapes 1 à 5 (`lint` ruff, `test` pytest, `secrets` Gitleaks, `sast` Semgrep p/python, `deps` Trivy sur requirements.txt, échec si CRITICAL), jobs enchaînés dans l'ordre du contrat ; outils vérifiés en local / pipeline GitLab (#3) pas encore écrit : versions des outils à aligner avec Lucas ; Semgrep installé par pip cassait (dépendance `pkg_resources` absente), remplacé par l'image Docker officielle
2026-11-17 · Lucas · #2 · Workflow mirror-gitlab.yml : push de main et develop vers GitLab à chaque push / test réel impossible avant fusion (le workflow doit être sur develop) ; projet GitLab et secrets à créer à la main
