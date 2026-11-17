# Métiers et interactions — La Petite Maison de l'Épouvante

Issue #21 · Marie · schéma : `docs/schemas/marie-metiers-interactions.drawio` (export PNG à côté)

## Objet

La nouvelle plateforme (vente en ligne + espace communautaire) mobilise plusieurs métiers. Ce document décrit
les **rôles clés**, ce que chacun **produit**, et ce qu'il **transmet aux autres**. Un rôle n'est pas forcément
une personne : dans une petite équipe, une même personne peut tenir plusieurs rôles (voir la dernière section).

Les rôles sont regroupés en trois familles, comme sur le schéma :

- **Cadrer le besoin** : décider quoi construire et dans quelles limites (budget, données personnelles).
- **Concevoir et construire** : choisir comment le construire, le coder et le tester.
- **Livrer, protéger, exploiter** : mettre en production, sécuriser, faire tourner au quotidien.

## Les rôles

| Rôle | Mission | Produit | Travaille surtout avec |
| --- | --- | --- | --- |
| **Maîtrise d'ouvrage (MOA)** | La direction de La Petite Maison : porte la vision, arbitre le budget et les priorités | Objectifs, budget, validation de la recette finale | Product owner, chef de projet |
| **Product owner** | Représente les clients et la MOA dans l'équipe ; décide de l'ordre des fonctionnalités | Backlog priorisé, user stories, critères d'acceptation | MOA, UX, développeurs, QA |
| **UX designer** | Conçoit des parcours simples pour les clients (achat, troc, chat) | Recherche utilisateurs, maquettes testées, règles d'accessibilité | Product owner, développeurs |
| **DPO** | Délégué à la protection des données : garantit la conformité RGPD | Registre des traitements, exigences (consentement, durée de conservation, droit à l'effacement) | Product owner, architecte, expert sécurité |
| **Architecte** | Choisit les technologies et découpe le système en composants | Schéma d'architecture, choix techniques argumentés, attributs qualité visés | Développeurs, expert sécurité, DevOps |
| **Développeurs** | Écrivent le code front et back et ses tests automatisés | Code relu par pull request, tests unitaires | Product owner, architecte, QA, DevOps |
| **QA (testeur)** | Vérifie que le produit fait ce qui est attendu, sans régression | Stratégie de test, tests automatisés, rapport de recette | Développeurs, product owner |
| **Chef de projet / Scrum master** | Fait avancer l'équipe : rituels, planning, blocages | Planning, comptes rendus, suivi des risques | Tous les rôles |
| **Expert sécurité** | Réduit les risques : analyse, règles, suivi des failles | Analyse de risques, politique de sécurité, règles appliquées dans le pipeline | Architecte, développeurs, DevOps, DPO |
| **DevOps** | Automatise la construction, les tests et le déploiement ; maintient l'infrastructure | Pipeline CI/CD, environnements, déploiements | Développeurs, expert sécurité, support |
| **Support et exploitation** | Fait tourner la plateforme au quotidien et répond aux clients | Supervision, gestion des incidents, retours utilisateurs | DevOps, développeurs |

## Les interactions

Chaque flèche numérotée du schéma correspond à un échange :

| N° | De → vers | Ce qui est transmis |
| --- | --- | --- |
| 1 | MOA → product owner | Vision, budget et priorités |
| 2 | UX designer → product owner | Maquettes testées auprès des clients |
| 3 | DPO → product owner | Exigences RGPD : consentement, durée de conservation |
| 4 | Product owner → développeurs | User stories priorisées, critères d'acceptation |
| 5 | Architecte → développeurs | Choix techniques, découpage en services |
| 6 | Développeurs → QA | Version à tester (pull request) |
| 7 | QA → product owner | Résultats de recette |
| 8 | Architecte ↔ expert sécurité | Revue de sécurité de l'architecture |
| 9 | Expert sécurité → développeurs | Failles détectées à corriger |
| 10 | Développeurs → DevOps | Code fusionné, pris en charge par le pipeline |
| 11 | Expert sécurité → DevOps | Règles de sécurité appliquées par le pipeline |
| 12 | DevOps → support et exploitation | Mise en production, tableaux de bord |
| 13 | Support et exploitation → développeurs | Incidents et retours des clients |

Deux boucles se dégagent :

- **la boucle produit** (1 → 4 → 6 → 7) : le besoin devient du code, testé, puis accepté par le product owner ;
- **la boucle DevSecOps** (10 → 12 → 13, avec 9 et 11) : chaque livraison passe par le pipeline et ses contrôles de
  sécurité, et les incidents en production reviennent aux développeurs.

## Qui décide quoi (matrice RACI)

R = réalise · A = approuve (une seule personne) · C = consulté · I = informé

| Activité | MOA | PO | UX | DPO | Archi | Dev | QA | CdP | Sécu | DevOps | Support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Définir et prioriser le besoin | C | A/R | C | C | C | I | I | I | I | I | C |
| Concevoir les parcours clients | I | A | R | C | I | C | C | I | I | I | C |
| Choisir les technologies | I | C | I | C | A/R | C | I | I | C | C | I |
| Développer une fonctionnalité | I | C | C | I | C | R | C | I | I | I | I |
| Tester et recetter | I | A | C | I | I | C | R | I | I | I | I |
| Traiter les données personnelles | I | C | I | A | C | R | I | I | C | I | I |
| Définir les règles de sécurité | I | I | I | C | C | C | I | I | A/R | C | I |
| Maintenir le pipeline CI/CD | I | I | I | I | C | C | C | I | C | A/R | I |
| Mettre en production | A | C | I | I | I | C | C | I | C | R | I |
| Gérer un incident | I | I | I | C | I | R | I | I | C | C | A/R |

## Dans notre projet

L'équipe du cube est de trois personnes ; chacune tient plusieurs rôles :

| Membre | Rôles tenus dans le projet |
| --- | --- |
| Lucas | Expert sécurité (cycle DevSecOps, politique de sécurité), DevOps côté GitLab CI, harmonisation (rôle proche du chef de projet) |
| Maxime | DevOps côté GitHub Actions et Kubernetes, QA (attributs qualité, tests dans le pipeline) |
| Marie | Architecte (architecture physique, choix du bus de messages) et développeuse (scénarios RabbitMQ et Kafka) |

Côté La Petite Maison de l'Épouvante, la **direction** joue la MOA. Les rôles de **product owner**, **UX**,
**DPO** et **support** sont à confier en interne ou à recruter ; le DPO peut être mutualisé ou externe, ce qui est
fréquent pour une entreprise de cette taille.
