# Comparatif GitHub Actions vs GitLab CI

Issue #22 · Lucas + Maxime · slide : `presentation/slide-comparatif-cicd.png`

## Méthode

Pour comparer les **plateformes** et pas les pipelines, les deux pipelines sont identiques :

- les mêmes 10 jobs, dans le même ordre : `lint`, `test`, `secrets`, `sast`, `deps`, `build`, `scan-image`, `deploy`, `smoke`, `dast` ;
- les mêmes outils aux mêmes versions (ruff, pytest, Gitleaks 8.21.2, Semgrep 1.95.0, Trivy 0.57.1, kind 0.27.0, Helm 3.17.1) ;
- le même code : GitHub est la référence, un workflow pousse `develop` et `main` vers GitLab ;
- les runners partagés gratuits de chaque plateforme.

Tout ce qui suit vient de nos mesures et de ce que nous avons vécu en construisant les pipelines (voir `journal/journal.md`).

## Mesures sur le même commit

Commit `594e851a` sur `develop`, les deux pipelines au vert. GitHub Actions : run 44087790518. GitLab CI : pipeline 3078971167.

| Job | GitHub Actions | GitLab CI |
| --- | ---: | ---: |
| `lint` | 11 s | 25 s |
| `test` | 12 s | 29 s |
| `secrets` | 6 s | 17 s |
| `sast` | 20 s | 33 s |
| `deps` | 33 s | 36 s |
| `build` | 17 s | 41 s |
| `scan-image` | 35 s | 29 s |
| `deploy` | 57 s | 99 s |
| `smoke` | 68 s | 98 s |
| **Total, du déclenchement à la fin** | **4 min 55** | **7 min 03** |

Sur nos derniers pipelines complets au vert : GitLab CI entre 7 min 03 et 7 min 32 (3 pipelines), GitHub Actions entre 4 min 36 et 4 min 55 (2 runs).

Pourquoi GitLab est plus lent ici : chaque job démarre dans un conteneur dont l'image doit être téléchargée, et kind tourne dans un service docker-in-docker qu'il faut lancer à chaque job. GitHub fournit une machine virtuelle où Docker est déjà prêt. `dast` (ZAP) n'est pas compté : il est manuel côté GitLab et n'est pas encore écrit côté GitHub.

## Comparaison point par point

| Critère | GitHub Actions | GitLab CI |
| --- | --- | --- |
| Configuration | un fichier par workflow ; ordre des jobs par `needs` | un fichier `.gitlab-ci.yml` ; ordre par `stages` explicites |
| Réutilisation | ancres YAML, actions composites, Marketplace | `extends`, modèles cachés (`.kind`), `include` |
| Environnement d'un job | VM Ubuntu avec Docker, kind, kubectl et Helm déjà installés | conteneur choisi par job (`image:`) ; Docker via un service docker-in-docker privilégié |
| Registre d'images | ghcr.io : permission `packages: write` à déclarer, nom en minuscules obligatoire | registre intégré : identifiants fournis à chaque job, rien à configurer |
| Règles de déclenchement | `on:` push / pull_request, `if:` par job | `workflow:rules`, `rules:` par job, `when: manual` |
| Lancement à la main | tout le workflow (`workflow_dispatch`) | un seul job (`when: manual`, utilisé pour `dast`) |
| Outils de mise au point | journaux par étape | éditeur de pipeline, CI Lint, simulation d'un pipeline |
| Sécurité fournie par la plateforme | Dependabot, détection de secrets, code scanning (gratuits pour un dépôt public) | modèles SAST / détection de secrets ; DAST et tableaux de bord réservés à l'offre Ultimate |
| Coût (offres gratuites) | minutes illimitées pour un dépôt public ; 2 000 min/mois en privé | 400 min de calcul par mois, partagées par tout le groupe |
| Auto-hébergement | runners auto-hébergés ; serveur GitHub Enterprise payant | runners auto-hébergés ; GitLab complet auto-hébergeable (édition gratuite) |

## Ce que nous avons vécu

**GitHub Actions (Maxime)**

- Semgrep installé par `pip` cassait (dépendance `pkg_resources` absente) : remplacé par l'image Docker officielle.
- ghcr.io refuse les majuscules du propriétaire (`Luucaaas`) : nom d'image forcé en minuscules.
- Premier `deploy` rouge (`chmod: Operation not permitted`) : kind, kubectl et Helm déjà présents sur la VM, appartenant à root, entraient en conflit avec nos versions figées. Corrigé en les installant dans un dossier à nous.
- `deploy` ne tourne que sur `develop` et `main` : impossible à tester dans une pull request.

**GitLab CI (Lucas)**

- Gitleaks refusait de lire le dépôt cloné par le runner (propriétaire différent) : ajout de `safe.directory`.
- kind dans docker-in-docker : l'API Kubernetes n'est joignable que par le nom `docker`, d'où un certificat à étendre (`certSANs`) et une adresse à réécrire.
- **Un stage nommé `dast` fait refuser tout le pipeline** sur l'offre gratuite (« Insufficient permissions for dast_configuration keyword ») : GitLab le prend pour sa fonction DAST payante. Message peu explicite ; cause trouvée dans le code source de GitLab. Stage renommé `dast-zap`, job `dast` conservé.
- Le code vit sur GitHub : il a fallu un miroir (jeton GitLab, secrets GitHub, URL sans `https://`).
- Quota de minutes partagé par le groupe : à surveiller avant la soutenance.

## Forces, faiblesses, limites

| | GitHub Actions | GitLab CI |
| --- | --- | --- |
| **Forces** | plus rapide (environ 30 % sur notre pipeline) ; VM prête avec Docker ; intégré au code et aux pull requests ; gratuit et illimité pour un dépôt public | plateforme tout-en-un (code, CI, registre, environnements) ; registre sans configuration ; règles très fines (`rules`, `extends`, job manuel) ; outils de validation avant de lancer |
| **Faiblesses** | factorisation limitée (ancres YAML, actions composites) ; outils préinstallés qui peuvent entrer en conflit ; registre à configurer (permissions, minuscules) | plus lent (un conteneur par job, docker-in-docker) ; docker-in-docker plus complexe et privilégié ; messages d'erreur parfois obscurs |
| **Limites** | 2 000 min/mois en privé sur l'offre gratuite ; fonctions de sécurité avancées payantes pour un dépôt privé | 400 min/mois sur l'offre gratuite ; DAST et tableaux de bord de sécurité en Ultimate ; certains noms réservés (`dast`) |

## Recommandation pour La Petite Maison de l'Épouvante

- **Code sur GitHub et dépôts publics ou petit budget** → GitHub Actions : plus rapide, plus simple à démarrer, gratuit.
- **Besoin d'une plateforme unique hébergée en Europe** (exigence du contexte) → GitLab, qui peut être entièrement auto-hébergé chez OVHcloud avec son édition gratuite, runners compris.

Notre choix pour la cible : **GitLab auto-hébergé**, pour garder code, pipelines, images et journaux en France, dans le même outil. *(À valider avec Maxime.)*

*À compléter par Maxime : son ressenti sur la lisibilité de l'interface GitHub et sur l'écriture de `ci.yml`.*
