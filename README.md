# Cube S3 — La Petite Maison de l'Épouvante

Projet collaboratif CESI MAALSI, bloc *Superviser et assurer le développement des applications logicielles*.
Équipe : Lucas, Maxime, Marie.

Objectif : présenter à la direction la démarche de développement et les choix techniques de la future plateforme
(vente en ligne + espace communautaire), avec 4 démonstrations live : 2 solutions CI/CD et 2 technologies applicatives.

## Répartition

| Qui | Développe | Rédige |
| --- | --- | --- |
| Lucas | Pipeline GitLab CI + scans de sécurité | Cycle DevSecOps, politique de sécurité, organisation et bilan |
| Maxime | Pipeline GitHub Actions + déploiement Kubernetes local (kind) | Attributs qualité, tests dans le pipeline, schéma Kubernetes |
| Marie | Scénario troc avec RabbitMQ puis Kafka + test comparatif | Architecture physique, métiers et interactions |

## Organisation du dépôt

| Dossier | Contenu | Responsable |
| --- | --- | --- |
| `demo-cicd/` | Micro-service Python (FastAPI) + tests, utilisé par les deux pipelines | Les 3 (J1), puis Lucas et Maxime |
| `.gitlab-ci.yml` | Pipeline GitLab CI | Lucas |
| `.github/workflows/` | Pipeline GitHub Actions | Maxime |
| `demo-messaging/` | Scénario « article proposé → notification » avec RabbitMQ et Kafka | Marie |
| `docs/contrats/` | Décisions figées au J1 (choix techniques, attributs qualité, étapes du pipeline, plan du PPT) | Les 3 |
| `docs/schemas/` | Sources draw.io des schémas (faits maison) | Chacun ses schémas |
| `presentation/` | Support de soutenance | Lucas (harmonisation) |
| `journal/` | Journal de bord : difficultés, décisions (pour le bilan) | Les 3 |

## Règles de travail

- Chacun travaille sur une branche `prenom/sujet` et ouvre une pull request ; relecture sous 24 h, sans bloquer.
- Lucas et Maxime ne modifient que leur propre fichier de pipeline : pas de conflit.
- Avant chaque journée en séance (la veille, 20 h) : tout est poussé et le Kanban est à jour.
- Une question bloquante : on la note sur la carte Kanban, on prend une hypothèse et on continue.
- Les contrats de `docs/contrats/` ne se modifient qu'à trois.
