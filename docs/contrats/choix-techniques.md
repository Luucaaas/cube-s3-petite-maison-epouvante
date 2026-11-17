# Choix techniques — contrat d'équipe

Validé par Lucas, Maxime et Marie le 17/11/2026. Ce fichier ne se modifie qu'à trois (pull request approuvée par les deux autres).

## A. Démonstrations notées

| # | Choix | Décision | Responsable |
| --- | --- | --- | --- |
| A1 | 2 solutions CI/CD comparées | GitHub Actions vs GitLab CI | Maxime (GitHub), Lucas (GitLab) |
| A2 | Type de technologie comparée | Bus de messages | Marie |
| A3 | 2 technologies comparées | RabbitMQ vs Kafka | Marie |

## B. Plateforme des démos

| # | Choix | Décision | Remarque |
| --- | --- | --- | --- |
| B1 | Kubernetes local | kind | |
| B2 | Déploiement | Helm (chart dans `demo-cicd/helm/`) | |
| B3 | Registre d'images | Registre intégré : ghcr.io côté GitHub, registry GitLab côté GitLab | Point de comparaison |
| B4 | Accès au cluster depuis le pipeline | Cluster kind créé dans le job de déploiement | Aucun runner local nécessaire |
| B5 | Supervision | Prometheus + Grafana | Bonus, seulement si le déploiement marche au J4 |

## C. Pile applicative

| # | Choix | Décision | Usage |
| --- | --- | --- | --- |
| C1 | Backend | Python 3.12 + FastAPI | Développé (démos) |
| C2 | Front | Angular | Cible, cité uniquement |
| C3 | Base de données | PostgreSQL | Cible, cité uniquement |
| C4 | Authentification | Keycloak (auto-hébergé) | Cible, cité uniquement |
| C5 | Hébergement | OVHcloud (Kubernetes et PostgreSQL managés, région France) | Cible, cité uniquement |
| C6 | Paiement | Prestataire externe certifié PCI-DSS | Cible, aucune donnée de carte chez nous |

## D. Qualité et sécurité dans les pipelines

Les mêmes outils sur les deux plateformes, pour comparer à outil égal.

| # | Rôle | Outil |
| --- | --- | --- |
| D1 | Tests + lint | pytest + ruff |
| D2 | Analyse statique de sécurité (SAST) | Semgrep |
| D3 | Détection de secrets | Gitleaks |
| D4 | Dépendances + image | Trivy |
| D5 | Test dynamique (DAST) | OWASP ZAP baseline — optionnel |

## Étapes du pipeline (identiques sur les deux plateformes)

1. `lint` — ruff
2. `test` — pytest
3. `secrets` — Gitleaks
4. `sast` — Semgrep
5. `deps` — Trivy sur `requirements.txt`
6. `build` — image Docker, poussée dans le registre intégré
7. `scan-image` — Trivy sur l'image (échec si vulnérabilité CRITICAL)
8. `deploy` — cluster kind créé dans le job, `helm upgrade --install`
9. `smoke` — appel de `/health` sur le service déployé
10. `dast` — ZAP baseline (optionnel)

Déclencheurs : push et merge request / pull request sur `develop` et `main`. Le déploiement (étapes 8 à 10) ne tourne que sur `develop` et `main`.

## E. Travail en commun

| # | Choix | Décision |
| --- | --- | --- |
| E1 | Branches | `main` (version présentable) + `develop` (intégration) + branches de travail `prenom/sujet` partant de `develop` |
| E2 | Code sur GitLab | GitHub est la référence ; une GitHub Action pousse `main` et `develop` vers GitLab à chaque push (Lucas) |
| E3 | Environnement Python | Python 3.12 + `requirements.txt` |
| E4 | Suivi | GitHub Issues + GitHub Projects |

Fusion `develop` → `main` : seulement quand les deux pipelines sont verts (J4 soir, puis J5).
