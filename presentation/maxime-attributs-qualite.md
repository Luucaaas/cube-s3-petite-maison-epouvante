# Attributs qualité — La Petite Maison de l'Épouvante

Issue #12 · Maxime · slide : `presentation/maxime-slide-attributs-qualite.png` (source : `presentation/maxime-slide-attributs-qualite.html`)

## Référentiel et méthode

Le référentiel est la norme **ISO/IEC 25010:2023**, qui définit 9 caractéristiques de qualité d'un produit logiciel. Nous en retenons **6**, choisies à partir de ce que la plateforme doit tenir face à ses utilisateurs et au SI existant :

- **la nouvelle plateforme** : vente en ligne, fanzine numérique, espace communautaire de troc, chat ;
- **ses contraintes** : pics de trafic pendant le festival et les lancements de goodies, 4 magasins dont Londres, comptes clients et paiements, raccordement au stock, au CRM et aux caisses ;
- **ses évolutions** : enchères (v2), diffusion des productions d'Evil Ed (v2) et des films du festival (v3).

Pour chaque attribut, on donne : pourquoi il compte **ici**, les sous-caractéristiques visées, comment la démarche le garantit (en reliant si possible aux démonstrations), et un **indicateur cible** qui le rend vérifiable. Les cibles sont des objectifs à valider avec la direction. Les seuls chiffres mesurés sont signalés comme tels.

## Les 6 attributs retenus

### 1. Sécurité

- **Pourquoi ici** : la plateforme stocke des comptes clients, des commandes et des messages privés (chat, troc). Une fuite toucherait à la fois la confiance des fans et la conformité RGPD (et UK GDPR pour Londres).
- **Sous-caractéristiques** : confidentialité, intégrité, authenticité, traçabilité.
- **Comment** :
  - contrôles automatiques dans le pipeline : Gitleaks (secrets), Semgrep (code), Trivy (dépendances et image), qui bloquent en cas de faille CRITICAL ;
  - authentification centralisée Keycloak avec MFA ;
  - paiement délégué à un prestataire PCI-DSS, sans aucune donnée de carte chez nous ;
  - conteneurs non root.
- **Indicateur cible** : 0 vulnérabilité CRITICAL en production, HIGH corrigées sous 30 jours.
- **Mesuré dans la démo** : image du micro-service à 0 CRITICAL et 48 HIGH, toutes dans la base Debian.

Le détail est dans la politique de sécurité de Lucas (#7).

### 2. Fiabilité

- **Pourquoi ici** : la boutique vend 24 h/24, y compris pour Londres, et le festival concentre les ventes sur quelques jours. Une panne pendant le festival coûte du chiffre d'affaires et de l'image.
- **Sous-caractéristiques** : disponibilité, tolérance aux pannes, capacité de récupération.
- **Comment** :
  - Kubernetes managé (OVHcloud) qui redémarre automatiquement un conteneur en échec, grâce aux sondes sur `/health` ;
  - déploiement avec `helm --wait`, qui n'est validé que si l'application répond ;
  - test de fumée (`smoke`) après chaque déploiement ;
  - PostgreSQL managé avec sauvegardes et test de restauration ;
  - bus de messages : si le service de notifications tombe, les événements attendent dans la file au lieu d'être perdus.
- **Indicateur cible** : disponibilité ≥ 99,5 % par mois, retour en service ≤ 1 h après incident.

### 3. Efficacité de performance

- **Pourquoi ici** : le trafic n'est pas régulier. Il y a des pics au festival, aux sorties de goodies et aux enchères (v2), où beaucoup d'utilisateurs agissent en même temps sur un même article.
- **Sous-caractéristiques** : comportement temporel (temps de réponse), capacité (montée en charge), utilisation des ressources.
- **Comment** :
  - montée en charge horizontale sur Kubernetes (plusieurs instances du même service) ;
  - traitements lents (notifications, e-mails) sortis du parcours d'achat grâce au bus de messages : l'utilisateur n'attend pas ;
  - test de charge avant chaque festival ;
  - temps de réponse suivi dans Grafana.
- **Indicateur cible** : 95 % des pages et appels d'API en moins de 500 ms, y compris au pic du festival.

Le comparatif RabbitMQ / Kafka de Marie (#19) mesure le débit et la latence du bus.

### 4. Maintenabilité

- **Pourquoi ici** : l'équipe est petite et la plateforme va beaucoup évoluer (enchères, vidéo, films). Chaque évolution doit pouvoir être livrée sans casser l'existant ni dépendre d'une seule personne.
- **Sous-caractéristiques** : modularité, testabilité, modifiabilité, analysabilité.
- **Comment** :
  - services séparés (vente, troc, chat, notifications) reliés par API et événements ;
  - lint (ruff) et tests automatiques (pytest) qui bloquent toute pull request en échec ;
  - revue de code par pull request ;
  - versions de dépendances épinglées.
- **Indicateur cible** : 100 % des changements passent par le pipeline ; une correction simple livrée en production dans la journée.
- **Mesuré dans la démo** : retour lint + tests en 26 s, pipeline complet jusqu'au déploiement testé en 4 min 55 s.

### 5. Compatibilité

- **Pourquoi ici** : la plateforme n'arrive pas seule. Elle doit échanger avec le stock, les fournisseurs, le CRM, les caisses des 4 magasins et le prestataire de paiement. Aujourd'hui une partie de ces échanges se fait à la main par fichiers CSV.
- **Sous-caractéristiques** : interopérabilité, coexistence.
- **Comment** :
  - API REST documentées et versionnées ;
  - événements au format commun, le même pour RabbitMQ et Kafka dans notre démo : `article.propose` avec identifiant, catégorie et date ISO 8601 ;
  - remplacement progressif des échanges CSV par des flux automatisés.
- **Indicateur cible** : 0 échange manuel par fichier à 6 mois ; stock en ligne et en magasin cohérent en moins de 5 min.

### 6. Capacité d'interaction (ex-utilisabilité)

- **Pourquoi ici** : le public est composé de fans, souvent sur mobile, en France et à Londres. La vente et le troc doivent être faciles sans aide, et le site doit être accessible.
- **Sous-caractéristiques** : facilité d'apprentissage et d'utilisation, accessibilité, protection contre les erreurs de l'utilisateur.
- **Comment** :
  - front Angular responsive (mobile d'abord) ;
  - interface en français et en anglais ;
  - respect du RGAA (accessibilité) ;
  - parcours d'achat court ;
  - saisies contrôlées. Par exemple, l'API refuse un article mal formé (type autre que « echange » ou « don » → code 422), ce que vérifie un test du micro-service.
- **Indicateur cible** : score d'accessibilité Lighthouse ≥ 90 ; achat réalisable en moins de 5 étapes.

## Attributs non prioritaires

| Attribut ISO 25010 | Pourquoi il n'est pas dans les 6 |
| --- | --- |
| Adéquation fonctionnelle | Elle relève du recueil des besoins et des tests fonctionnels, pas d'un choix d'architecture : elle est vérifiée par les tests de chaque service. |
| Flexibilité (portabilité) | Elle est obtenue presque gratuitement par les conteneurs et Helm : le même chart tourne sur kind dans nos pipelines et sur le Kubernetes d'OVHcloud. |
| Sûreté (*safety*) | La plateforme ne pilote aucun équipement physique : pas de risque pour la vie ou la santé des personnes. |

## Lien avec la suite

Ces attributs servent d'entrée à la **stratégie de tests** (#13) : chaque attribut correspond à un type de test placé dans le pipeline.

| Attribut | Tests correspondants |
| --- | --- |
| Sécurité | SAST, secrets, dépendances, image, DAST |
| Maintenabilité | Lint et tests unitaires |
| Fiabilité | Test de fumée après déploiement |
| Performance | Test de charge |
| Compatibilité | Tests de contrat d'API |
| Capacité d'interaction | Tests d'accessibilité |
