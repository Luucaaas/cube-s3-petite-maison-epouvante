# Politique de sécurité — La Petite Maison de l'Épouvante

Issue #7 · Lucas · schéma : `docs/schemas/lucas-politique-securite.drawio` · slide : `presentation/lucas-slide-politique-securite.png`

## Périmètre et principes

La politique couvre **tout le système d'information**, pas seulement la nouvelle plateforme :

- **la nouvelle plateforme** : vente en ligne, fanzine numérique, espace communautaire de troc, chat ;
- **le SI existant** : site vitrine (CMS), site d'Evil Ed, gestion de stock, fournisseurs, CRM, caisses des 4 magasins (dont Londres), messagerie Gmail, serveur de fichiers de Paris (VPN, sauvegardes Veeam), infrastructure média d'Evil Ed, postes Ubuntu et station Mac ;
- **les évolutions prévues** : enchères (v2), diffusion des productions d'Evil Ed (v2) et des films du festival (v3).

Cinq principes s'appliquent partout :

1. **Sécurité dès la conception** (*shift left*) : un contrôle automatique à chaque étape du pipeline, une faille détectée tôt coûte moins cher.
2. **Moindre privilège** : chaque personne, service et conteneur n'a que les droits nécessaires (conteneurs non root, comptes nominatifs).
3. **Défense en profondeur** : plusieurs barrières indépendantes (code, image, réseau, authentification, supervision).
4. **Données en Europe** : hébergement OVHcloud en France, conformité RGPD (UK GDPR pour Londres), aucune donnée de carte chez nous (paiement délégué à un prestataire PCI-DSS).
5. **Aucun secret dans le code** : variables d'environnement et secrets CI uniquement, contrôlés par Gitleaks.

## Axe 1 — Inventaire du parc applicatif

On ne protège bien que ce que l'on connaît. Un **registre des applications** est tenu à jour (fichier versionné au départ, outil dédié ensuite).

| Application | Hébergement | Données sensibles | Criticité |
| --- | --- | --- | --- |
| Nouvelle plateforme (vente, troc, chat) | OVHcloud, Kubernetes | comptes clients, commandes, messages | critique |
| Messagerie Gmail | Google | échanges internes, comptes d'administration | critique |
| Caisses des magasins | magasins | transactions | élevée |
| Stock, fournisseurs, CRM | cloud français | clients, fournisseurs, prix | élevée |
| Serveur de fichiers (Paris) | local, accès VPN | documents internes | élevée |
| Infrastructure média Evil Ed | local, 2 nœuds | productions non publiées (propriété intellectuelle) | élevée |
| Sites vitrines (CMS) | cloud | abonnés à la newsletter | moyenne |
| Postes Ubuntu, station Mac | magasins, bureaux | données locales | moyenne |

Pour chaque application : **propriétaire**, données traitées, criticité, versions, date de dernière mise à jour. Côté plateforme, chaque image Docker a sa liste de composants (SBOM générée par Trivy).

Règles : une application n'est mise en production qu'une fois inscrite au registre ; revue complète chaque trimestre. Les échanges manuels par fichiers CSV sont recensés puis remplacés par des flux automatisés et chiffrés.

## Axe 2 — Scans de sécurité

**Dans le pipeline CI/CD** (démontré sur GitLab CI et GitHub Actions) :

| Étape | Outil | Ce qui est détecté | Effet |
| --- | --- | --- | --- |
| `secrets` | Gitleaks | mot de passe ou clé commité | bloque |
| `sast` | Semgrep | failles dans le code source | bloque |
| `deps` | Trivy | dépendance vulnérable | bloque si CRITICAL |
| `scan-image` | Trivy | faille dans l'image (système + paquets) | bloque si CRITICAL |
| `dast` | OWASP ZAP | faille sur l'application en marche | rapport |

**En dehors du pipeline** : les images déjà en production sont rescannées chaque semaine (de nouvelles failles sont publiées tous les jours) ; les serveurs, le CMS et les postes sont scannés chaque mois ; les mises à jour de sécurité sont suivies.

**Délais de correction** selon la gravité : CRITICAL immédiatement (bloquant), HIGH sous 30 jours, MEDIUM dans le backlog. Exemple mesuré sur notre image : 48 HIGH, 0 CRITICAL, toutes dans la base Debian — traitées en mettant à jour l'image de base.

## Axe 3 — Supervision des applications et des infrastructures

- **Applications et Kubernetes** : Prometheus + Grafana — disponibilité, taux d'erreurs, temps de réponse, redémarrages de pods.
- **Événements de sécurité** : échecs de connexion en série, créations de comptes en masse, pics de trafic (festival, attaque), connexions VPN inhabituelles.
- **Infrastructure** : réussite des sauvegardes Veeam **et tests de restauration**, espace disque, expiration des certificats TLS.
- **Journaux** centralisés et conservés 6 à 12 mois, accès restreint.
- **Alertes** envoyées à une astreinte définie (pas seulement par e-mail).

## Axe 4 — Analyse des risques et gestion des incidents

**Analyse des risques** : méthode EBIOS Risk Manager (ANSSI), en version allégée — chaque risque est noté en vraisemblance × impact, puis traité.

| Risque | V × I | Mesures principales |
| --- | --- | --- |
| Fuite des données clients | moyenne × élevé | SAST/DAST, authentification Keycloak, chiffrement, moindre privilège |
| Rançongiciel sur le serveur de fichiers ou l'infra Evil Ed | moyenne × élevé | sauvegardes 3-2-1 dont une hors ligne, segmentation, VPN avec MFA |
| Hameçonnage, vol d'un compte Gmail | élevée × élevé | MFA obligatoire, sensibilisation, comptes d'administration séparés |
| Dépendance vulnérable | élevée × moyen | Trivy dans le pipeline, versions épinglées, mises à jour régulières |
| Indisponibilité pendant le festival | moyenne × élevé | Kubernetes managé (montée en charge), tests de charge, protection anti-DDoS de l'hébergeur |
| Fraude au paiement | faible × élevé | paiement délégué PCI-DSS, aucune donnée de carte stockée |
| Abus de l'espace communautaire (arnaques, contenus illicites) | moyenne × moyen | modération, signalement, limitation des envois |

L'analyse est **refaite à chaque nouvelle fonctionnalité majeure** (enchères, diffusion vidéo).

**Gestion des incidents**, en six étapes :

1. **Préparer** : fiches réflexes, contacts, rôles (référent sécurité : l'architecte logiciel).
2. **Détecter** : alertes de supervision, signalements des utilisateurs ou des magasins.
3. **Contenir** : isoler le service ou le poste, révoquer les accès compromis.
4. **Corriger** : supprimer la cause (correctif, mise à jour, nouvelle règle).
5. **Restaurer** : remise en service depuis une sauvegarde saine, surveillance renforcée.
6. **Retour d'expérience** : analyse sans recherche de coupable, actions correctives suivies.

En cas de violation de données personnelles : **notification à la CNIL sous 72 h** (et à l'ICO pour Londres), information des personnes concernées si le risque est élevé.

## Mesures organisationnelles

- MFA sur Gmail, le VPN, les consoles cloud et les dépôts de code.
- Gestionnaire de mots de passe, comptes nominatifs, revue des accès chaque trimestre et à chaque départ.
- Sensibilisation annuelle (hameçonnage, mots de passe) du personnel des magasins et d'Evil Ed.
- Sauvegardes 3-2-1 (3 copies, 2 supports, 1 hors site) et test de restauration chaque semestre.

## Amélioration continue (PDCA)

| Phase | Ce que l'on fait |
| --- | --- |
| **Plan** | inventaire, analyse des risques, objectifs (0 CRITICAL en production, MFA pour 100 % des comptes) |
| **Do** | contrôles dans le pipeline et sur le SI, mesures organisationnelles |
| **Check** | indicateurs mensuels : vulnérabilités ouvertes par gravité, délai moyen de correction, % d'applications inventoriées, % de comptes avec MFA, incidents, résultats des tests de restauration |
| **Act** | chaque incident ou presque-incident devient une règle (nouvelle règle Semgrep, nouveau seuil, nouvelle alerte, procédure mise à jour) ; revue annuelle de la politique |

Exemple dans notre démo : une dépendance vulnérable (Django 2.2) est ajoutée sur une branche → le job `deps` bloque le pipeline avant toute construction ou tout déploiement.

## Feuille de route

| Horizon | Actions |
| --- | --- |
| 0 – 3 mois | MFA partout, registre des applications, sauvegardes testées, pipeline DevSecOps |
| 3 – 6 mois | supervision centralisée, Keycloak, analyse de risques complète, fin des échanges CSV manuels |
| 6 – 12 mois | scans réguliers de tout le SI, exercice de crise, analyse de risques des fonctions v2 |
