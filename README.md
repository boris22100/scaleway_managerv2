# 🚀 Scaleway Cloud Manager V2

Une architecture d'administration multi-utilisateurs, modulaire et souveraine pour piloter vos infrastructures ****Scaleway****. Conçu pour la portabilité, la rapidité d'exécution et le respect des critères de durabilité (Green IT).

## 🏗 Structure de l'Architecture

Le projet est découpé en services distincts pour isoler les responsabilités et faciliter la maintenance :

    scaleway_managerv2/
    ├── scw-core/           # Logique métier et interconnexions API Scaleway
    ├── scw-ui/             # Interface réactive développée avec Streamlit
    ├── data/               # Volume persistant pour la base de données SQLite (manager.db)
    └── docker-compose.yml  # Orchestration et liaison des conteneurs applicatifs
    └── Dockerfile

## 🛠 Spécifications Techniques

-   ****Core Application :**** Python 3.9+ (Thème Dark Cloud optimisé)
-   ****Base de données :**** SQLite3 (Isolation stricte par utilisateur, chiffrement des empreintes de mots de passe, gestion locale et souveraine)
-   ****Déploiement global :**** Docker Multi-Containers (via Docker Compose)
-   ****Infrastructure cible :**** API REST Scaleway (Instances Compute, Zones DNS, VPC & Adresses IP Flexibles)
-   ****Provisioning automatisé :**** Mécanisme Cloud-init optimisé (Installation native du moteur Docker CE et injection directe du binaire stable de Docker Compose v2 comme CLI-plugin, sans dépendance obsolète)

## ✨ Fonctionnalités Clés

### 📊 Tableau de Bord & Synthèse Réseau

-   ****Monitoring temps réel :**** Synthèse d'état des instances actives et configurées sur les zones de disponibilité `fr-par-1` et `fr-par-2`.
-   ****Réseau & Routage :**** Cartographie de vos infrastructures (VPC, Passerelles privées, segments de sous-réseaux et statut des adresses IP Flexibles/Failover).

### 🌐 Gestionnaire DNS de Précision

-   ****Opérations CRUD :**** Administration complète des enregistrements (`A`, `AAAA`, `CNAME`, `TXT`, `MX`) avec ajustement fin du TTL.
-   ****Import Bulk :**** Alignement et injection en masse de zones DNS par simple copier-coller de lignes au format brut.

### 🌱 Suivi d'Éco-conception (Green IT)

-   ****Indicateurs environnementaux :**** Extraction des métriques d'émissions Carbone ($gCO\_2e$) et de consommation d'eau ($ml$) directement depuis l'API environnementale de Scaleway.
-   ****Modèle prédictif local :**** Intégration d'un fallback algorithmique basé sur les spécifications BoWiz pour continuer l'analyse si l'API cloud s'avère momentanément indisponible.

### 💰 Suivi Comptable & Budgétaire

-   ****Analyse financière :**** Centralisation et listing des factures mensuelles de votre projet (Montants HT et TTC).
-   ****Normalisation des prix :**** Interprétation et parsing des structures d'objets complexes (nanos/units) de l'API Scaleway pour un affichage limpide des encours financiers.

## 🚀 Guide d'Installation Rapide

### 1\. Pré-requis

-   ****Git**** et ****Docker / Docker Compose**** (via Docker Desktop sur Windows).
-   Vos identifiants d'API Scaleway (****Access Key****, ****Secret Key**** et ****Project ID****).

### 2\. Clonage du dépôt

    git clone https://github.com/boris22100/scaleway_managerv2.git
    cd scaleway_managerv2
    

### 3\. Lancement de la stack modulaire

Exécutez la commande suivante pour compiler et démarrer l'ensemble des modules (`scw-core`, `scw-ui`) en tâche de fond :

    docker compose up --build -d
    

L'interface de gestion devient instantanément disponible sur l'adresse : ****http://localhost:8501****

## ⚙️ Configuration Initiale (Pas à pas)

### Étape 1 : Initialisation de la Gouvernance

1.  À la première connexion, rendez-vous sur l'onglet ****"Création de compte"****.
2.  Par sécurité, ****le tout premier utilisateur**** enregistré sur la plateforme se voit attribuer le statut exclusif d'****Administrateur**** (`admin`).
3.  Les utilisateurs suivants sont placés en quarantaine (accès bloqué) et doivent être revus et approuvés manuellement par l'admin dans l'onglet dédié ****👑 Gouvernance****.

### Étape 2 : Activation d'un profil Cloud

1.  Rendez-vous dans l'onglet ****⚙️ Profils****.
2.  Configurez votre environnement (ex: __Production__, __BoWiz Lab__) en fournissant vos clés d'API et l'identifiant de projet Scaleway.
3.  Sélectionnez le profil actif dans le menu déroulant situé dans la barre latérale gauche pour lier la plateforme à vos ressources distantes.

## 🔐 Souveraineté & Maintenance

L'application respecte les principes de la ****souveraineté des données**** : aucune clé d'API, mot de passe ou métrique d'infrastructure ne quitte votre environnement d'hébergement.

-   ****Sauvegardes :**** La base SQLite étant isolée, il vous suffit de copier le fichier contenu dans le dossier `data/manager.db`.
-   ****Mises à jour :**** Récupérez la dernière version du code via `git pull` et rafraîchissez vos conteneurs avec `docker-compose up --build -d`.
