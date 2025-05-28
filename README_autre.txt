# Cloudya CLI

    Interface en ligne de commande DevOps pour l'automatisation du déploiement, de la supervision et du diagnostic d'infrastructures cloud.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

## 📋 Table des matières

    [Présentation](#-présentation)
    [Installation](#-installation)
    [Architecture](#-architecture)
    [Fonctionnalités](#-fonctionnalités)
    [Utilisation](#-utilisation)
    [Templates](#-templates)
    [Configuration](#-configuration)
    [Exemples d'utilisation](#-exemples-dutilisation)
    [Contribuer](#-contribuer)

## 🚀 Présentation

Cloudya est une interface en ligne de commande (CLI) DevOps qui permet de déployer, superviser et diagnostiquer des infrastructures cloud de manière unifiée. Elle supporte les principaux fournisseurs cloud (AWS, GCP, Azure) ainsi que les infrastructures privées (VMware, Nutanix, Proxmox, OpenStack).

### Fonctionnalités principales

    Déploiement d'infrastructure via Terraform
    Déploiement d'applications via Ansible
    Connexion multi-cloud unifiée
    Supervision des ressources système
    Diagnostic automatisé des problèmes
    Stacks complètes (infrastructure + applications)

## 💻 Installation

### Prérequis

    Python 3.8+
    pip
    Terraform (optionnel, pour le déploiement d'infrastructure)
    Ansible (optionnel, pour le déploiement d'applications)

### Installation depuis les sources

# Cloner le dépôt
git clone https://github.com/votre-repo/cloudya.git
cd cloudya

# Installer les dépendances
pip install typer rich pyyaml ansible

# Installer en mode développement
pip install -e .

### Vérification de l'installation

cloudya --version

## 🏗 Architecture

Cloudya utilise une architecture modulaire avec chargement dynamique des commandes :

cloudya/
├── cloudya/                    # Package principal
│   ├── __init__.py
│   ├── cli.py                  # Point d'entrée avec chargement dynamique
│   ├── commands/               # Commandes CLI (chargées dynamiquement)
│   │   ├── connect.py          # Connexion aux providers
│   │   ├── deploy.py           # Déploiement d'infrastructure
│   │   ├── app.py              # Gestion des applications
│   │   ├── stack.py            # Stacks complètes
│   │   ├── monitor.py          # Supervision
│   │   └── diagnose.py         # Diagnostic
│   └── utils/                  # Modules utilitaires
│       ├── terraform.py        # Wrapper Terraform
│       ├── config.py           # Gestion de configuration
│       ├── credentials.py      # Gestion des credentials
│       ├── ansible.py          # Module Ansible principal
│       ├── ansible_*.py        # Modules Ansible spécialisés
│       └── providers/          # Modules de connexion
│           ├── aws.py
│           ├── gcp.py
│           ├── azure.py
│           ├── openstack.py
│           ├── proxmox.py
│           ├── vmware.py
│           └── nutanix.py
└── ~/.cloudya/                 # Répertoire de configuration utilisateur
    ├── config.json             # Configuration générale
    ├── credentials.yaml        # Credentials des providers
    ├── templates/              # Templates personnalisés
    │   ├── terraform/          # Templates Terraform
    │   └── apps/               # Templates d'applications
    └── deployments/            # Historique des déploiements

## ✨ Fonctionnalités

### 1. Connexion aux Providers Cloud

Cloudya permet de se connecter de manière unifiée à différents fournisseurs :

# Connexion aux clouds publics
cloudya connect aws
cloudya connect gcp
cloudya connect azure

# Connexion aux infrastructures privées
cloudya connect proxmox
cloudya connect vmware
cloudya connect nutanix
cloudya connect openstack

### 2. Déploiement d'Infrastructure

Utilise Terraform pour déployer des infrastructures via des templates :

# Lister les templates disponibles
cloudya deploy list

# Déployer un template
cloudya deploy template aws/vpc --params region=eu-west-3,vpc_cidr=10.0.0.0/16

# Lister les déploiements
cloudya deploy list-deployments

# Détruire un déploiement
cloudya deploy destroy <deployment-id>

### 3. Gestion des Applications

Utilise Ansible pour déployer des applications sur l'infrastructure :

# Lister les applications disponibles
cloudya app list

# Voir les détails d'une application
cloudya app show wordpress

# Installer une application
cloudya app install wordpress --platform aws --params domain=monsite.com,admin_password=secret

# Voir le statut des applications
cloudya app status

# Désinstaller une application
cloudya app uninstall --id app-12345

### 4. Stacks Complètes

Combine infrastructure et applications en une seule commande :

# Lister les stacks préconfigurées
cloudya stack list

# Déployer une stack complète
cloudya stack deploy --template aws/ec2 --app wordpress \
  --infra-params region=eu-west-3,instance_type=t2.micro \
  --app-params domain=monsite.com,admin_password=secret

### 5. Supervision

Surveille les ressources système et les services :

# Surveiller le système
cloudya monitor

# Surveiller un service spécifique
cloudya monitor --service nginx --interval 10

# Générer un rapport
cloudya monitor report --days 7

### 6. Diagnostic

Diagnostique les problèmes système et des services :

# Diagnostiquer le système
cloudya diagnose system

# Diagnostiquer un service
cloudya diagnose service nginx

## 📚 Templates

### Structure d'un Template Terraform

~/.cloudya/templates/terraform/aws/vpc/
├── manifest.yaml        # Métadonnées et paramètres
├── main.tf             # Ressources Terraform principales
├── variables.tf        # Variables d'entrée
├── outputs.tf          # Sorties du template
└── README.md           # Documentation

Exemple de manifest.yaml :

name: "AWS VPC"
provider: "aws"
description: "VPC AWS avec sous-réseaux publics et privés"
parameters:
  - name: "region"
    description: "Région AWS"
    default: "us-east-1"
    required: true
  - name: "vpc_cidr"
    description: "CIDR block pour le VPC"
    default: "10.0.0.0/16"
    required: true
platforms:
  - aws

### Structure d'un Template d'Application

~/.cloudya/templates/apps/wordpress/
├── manifest.yaml        # Métadonnées et paramètres
├── playbook.yml         # Playbook Ansible principal
├── templates/           # Templates de configuration
│   ├── wp-config.php.j2
│   └── wordpress.conf.j2
└── README.md           # Documentation

Exemple de manifest.yaml :

name: "WordPress"
type: "ansible"
description: "Système de gestion de contenu"
platforms:
  - aws
  - gcp
  - azure
parameters:
  - name: "domain"
    description: "Nom de domaine"
    required: true
  - name: "admin_password"
    description: "Mot de passe administrateur"
    required: true

## ⚙️ Configuration

### Configuration Générale

Le fichier ~/.cloudya/config.json contient la configuration générale :

{
  "terraform_path": "terraform",
  "ansible_path": "ansible-playbook",
  "templates_dir": "~/.cloudya/templates",
  "log_level": "INFO"
}

### Credentials des Providers

Le fichier ~/.cloudya/credentials.yaml stocke les credentials :

aws:
  default_profile: "default"
  default_region: "us-east-1"

gcp:
  default_project: "mon-projet-gcp"

azure:
  default_subscription: "12345678-1234-1234-1234-123456789012"

## 📖 Exemples d'utilisation

### Déploiement complet d'un site WordPress

# 1. Se connecter à AWS
cloudya connect aws

# 2. Déployer une instance EC2
cloudya deploy template aws/ec2 --params region=eu-west-3,instance_type=t2.micro

# 3. Installer WordPress sur l'instance
cloudya app install wordpress --platform aws \
  --params domain=monsite.com,admin_password=MonMotDePasse123

# Ou tout en une seule commande avec stack :
cloudya stack deploy --template aws/ec2 --app wordpress \
  --infra-params region=eu-west-3,instance_type=t2.micro \
  --app-params domain=monsite.com,admin_password=MonMotDePasse123

### Surveillance d'un serveur web

# Surveiller le système en temps réel
cloudya monitor --interval 5

# Surveiller Apache spécifiquement
cloudya monitor --service apache2 --interval 10 --count 100

# Générer un rapport de performance
cloudya monitor report --days 30 --output rapport.html

### Diagnostic d'un problème

# Diagnostic général du système
cloudya diagnose system

# Diagnostic d'un service spécifique
cloudya diagnose service mysql

# Diagnostic d'un déploiement
cloudya diagnose deployment <deployment-id>

## 🛠 Ajout de Nouvelles Commandes

Cloudya utilise un système de chargement dynamique. Pour ajouter une nouvelle commande :

    Créez un fichier dans cloudya/commands/ (ex: nouvelle_commande.py)
    Utilisez Typer pour définir votre CLI :

#!/usr/bin/env python3
import typer

app = typer.Typer(help="Description de votre commande")

@app.command()
def action():
    """Action à exécuter"""
    print("Hello, World!")

if __name__ == "__main__":
    app()

    La commande sera automatiquement disponible : cloudya nouvelle_commande action

## 📋 Templates Disponibles

### Infrastructure (Terraform)

    aws/vpc : VPC AWS avec sous-réseaux publics et privés
    aws/ec2 : Instance EC2 avec VPC et groupe de sécurité
    gcp/vm : Machine virtuelle Google Cloud
    azure/vm : Machine virtuelle Azure

### Applications (Ansible)

    WordPress : CMS avec Apache, MySQL et PHP
    LAMP : Stack Linux, Apache, MySQL, PHP
    Nextcloud : Cloud privé avec Docker

## 🐛 Dépannage

### Problèmes courants

    Template non trouvé : Vérifiez que le template existe dans ~/.cloudya/templates/
    Terraform non trouvé : Installez Terraform ou configurez le chemin dans config.json
    Ansible non trouvé : Installez Ansible avec pip install ansible
    Connexion échouée : Vérifiez vos credentials dans ~/.cloudya/credentials.yaml

### Mode Debug

Activez le mode debug pour plus d'informations :

CLOUDYA_DEBUG=1 cloudya <commande>

## 🤝 Contribuer

    Fork le projet
    Créez une branche pour votre fonctionnalité
    Ajoutez vos modifications
    Testez avec pytest
    Soumettez une Pull Request

### Structure de développement

# Tests
pytest tests/

# Linting
flake8 cloudya/

# Formatage
black cloudya/

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

Développé avec ❤️ pour simplifier le DevOps multi-cloud.

Voici le deuxième readme. Je t'envoie le code ensuite. 

# Cloudya - Assistant d'Infrastructure Cloud basé sur l'IA

<div align="center">

![Cloudya Logo](https://via.placeholder.com/200x100/1E3A8A/FFFFFF?text=CLOUDYA)

Assistant d'infrastructure cloud intelligent en ligne de commande

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-red.svg)](https://github.com/votre-repo/cloudya)

</div>

## 📋 Table des matières

    [À propos](#à-propos)
    [Fonctionnalités](#fonctionnalités)
    [Architecture](#architecture)
    [Installation](#installation)
    [Configuration](#configuration)
    [Utilisation](#utilisation)
    [Interfaces de chat](#interfaces-de-chat)
    [API Backend](#api-backend)
    [Tests et développement](#tests-et-développement)
    [Sécurité](#sécurité)
    [Modèle économique](#modèle-économique)
    [Contribuer](#contribuer)
    [License](#license)

## 🎯 À propos

Cloudya est un assistant d'infrastructure cloud basé sur l'IA qui vous aide à gérer, déployer et optimiser vos ressources cloud. Il combine l'intelligence artificielle avancée avec une interface utilisateur intuitive pour simplifier les tâches DevOps complexes.

### Problèmes résolus

    Complexité des commandes cloud : Génère automatiquement les bonnes commandes AWS, Kubernetes, Terraform
    Courbe d'apprentissage : Explique chaque action et fournit des bonnes pratiques
    Erreurs de configuration : Valide et sécurise les commandes avant exécution
    Documentation dispersée : Centralise les connaissances d'infrastructure cloud

## ✨ Fonctionnalités

### 🤖 Intelligence Artificielle
- Agent IA spécialisé en DevOps, AWS, Kubernetes, Terraform, Docker
- Base de connaissances enrichie avec les meilleures pratiques
- Génération de code avec validation et sécurisation
- Explications détaillées pour chaque suggestion

### 💻 Interfaces utilisateur
- CLI classique : Commandes rapides et scriptables
- Chat TUI : Interface texte interactive et moderne
- Chat simple : Version légère sans dépendances graphiques
- Mode exécution : Exécution automatique des commandes générées

### 🔒 Sécurité
- Validation des commandes : Liste blanche/noire pour les opérations dangereuses
- Sandbox d'exécution : Isolation des commandes dans des conteneurs
- Authentification sécurisée : Gestion des tokens et sessions
- Audit complet : Logging de toutes les opérations

### 💰 Modèle économique
- Système de tokens : Paiement à l'usage avec plans flexibles
- Intégration Stripe : Paiements et abonnements automatisés
- Plans freemium : Version gratuite limitée + versions payantes
- Analytics d'usage : Suivi détaillé de la consommation

## 🏗️ Architecture

cloudya/
├── api/                    # Backend FastAPI
│   ├── main.py            # Point d'entrée de l'API
│   ├── routes/            # Endpoints API
│   │   ├── commands.py    # Traitement des commandes IA
│   │   ├── auth.py        # Authentification
│   │   ├── tokens.py      # Gestion des tokens
│   │   └── webhooks.py    # Webhooks Stripe
│   ├── models/            # Modèles Pydantic
│   ├── services/          # Services métier
│   │   ├── ai_service.py  # Interaction avec OpenAI
│   │   ├── command_validator.py # Validation sécurisée
│   │   └── sandbox.py     # Exécution isolée
│   └── db/               # Base de données
├── cli/                   # Interface ligne de commande
│   └── main.py           # Point d'entrée CLI
├── commands/             # Commandes disponibles
│   ├── ask.py           # Requêtes à l'IA
│   ├── chat.py          # Interface chat TUI/simple
│   ├── login.py         # Authentification
│   ├── logout.py        # Déconnexion
│   ├── configure.py     # Configuration
│   └── info.py          # Informations compte
├── knowledge/           # Base de connaissances
│   ├── aws.yaml        # Connaissances AWS
│   ├── kubernetes.yaml # Connaissances K8s
│   └── terraform.yaml  # Connaissances Terraform
├── tests/              # Tests et environnement de développement
└── docs/               # Documentation

### Flux de données

graph TD
    A[Utilisateur CLI] --> B[Interface Chat/Ask]
    B --> C[Validation Input]
    C --> D[API Backend]
    D --> E[Service IA]
    E --> F[OpenAI GPT-4]
    F --> G[Base de Connaissances]
    G --> H[Validation Sécurité]
    H --> I[Sandbox Exécution]
    I --> J[Retour Utilisateur]

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip ou conda
- Compte OpenAI (pour l'IA)
- Optionnel : Docker (pour l'exécution sécurisée)

### Installation rapide

# Depuis PyPI (quand disponible)
pip install cloudya

# Depuis le repository GitHub
git clone https://github.com/votre-repo/cloudya.git
cd cloudya
pip install -e .

### Installation des dépendances

# Dépendances de base
pip install -r requirements.txt

# Dépendances pour l'interface TUI
pip install textual rich

# Dépendances pour le backend de développement
pip install fastapi uvicorn

### Installation complète

# Cloner le repository
git clone https://github.com/votre-repo/cloudya.git
cd cloudya

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer en mode développement
pip install -e .

# Installer toutes les dépendances
pip install -r requirements.txt
pip install textual rich fastapi uvicorn

## ⚙️ Configuration

### Configuration initiale

# Configurer l'URL de l'API (serveur de production)
cloudya configure --api-url https://api.cloudya.ai

# Ou pour les tests en local
cloudya configure --api-url http://localhost:8000

### Variables d'environnement

# Token API (optionnel, sinon utiliser cloudya login)
export CLOUDYA_API_TOKEN="votre-token"

# Pour le backend de développement
export OPENAI_API_KEY="votre-clé-openai"
export DATABASE_URL="postgresql://user:pass@localhost/cloudya"
export STRIPE_API_KEY="votre-clé-stripe"

### Fichier de configuration

Le fichier de configuration est automatiquement créé dans ~/.cloudya/config.ini :

[api]
url = https://api.cloudya.ai

[auth]
token = votre-token-api

## 📖 Utilisation

### Authentification

# S'inscrire (première utilisation)
cloudya register
# Email: votre@email.com
# Nom: Votre Nom
# Mot de passe: ****

# Se connecter
cloudya login
# Email: votre@email.com
# Mot de passe: ****

# Vérifier les informations du compte
cloudya info

# Se déconnecter
cloudya logout

### Commandes de base

# Poser une question à l'IA (mode simulation)
cloudya ask "Créer un cluster Kubernetes sur AWS"

# Poser une question avec exécution automatique
cloudya ask -e "Créer un bucket S3 sécurisé"

# Afficher l'aide
cloudya --help

# Afficher la version
cloudya version

### Exemples d'utilisation

# Infrastructure AWS
cloudya ask "Déployer une application web sur AWS avec load balancer"
cloudya ask "Configurer un pipeline CI/CD avec CodePipeline"
cloudya ask "Créer un VPC avec sous-réseaux publics et privés"

# Kubernetes
cloudya ask "Déployer une application avec Kubernetes et Helm"
cloudya ask "Configurer l'auto-scaling horizontal pour mes pods"
cloudya ask "Créer un ingress controller avec certificats SSL"

# Terraform
cloudya ask "Créer une infrastructure multi-région avec Terraform"
cloudya ask "Configurer un state backend S3 pour Terraform"

# Docker
cloudya ask "Optimiser un Dockerfile pour la production"
cloudya ask "Créer un docker-compose pour développement"

# Sécurité
cloudya ask "Auditer la sécurité de mon cluster Kubernetes"
cloudya ask "Configurer AWS WAF pour protéger mon application"

## 💬 Interfaces de chat

Cloudya propose deux interfaces de chat pour différents besoins :

### Chat TUI (Interface Textuel Avancée)

Interface moderne avec coloration syntaxique, formatage Markdown et navigation intuitive.

# Lancer l'interface TUI
cloudya chat

# Avec mode exécution automatique
cloudya chat -e

Fonctionnalités TUI :
- ✨ Coloration syntaxique des commandes
- 📝 Formatage Markdown des réponses
- 🎨 Interface moderne et responsive
- ⌨️ Raccourcis clavier intuitifs
- 📜 Scroll automatique
- 🔄 Animation de frappe en temps réel

Raccourcis clavier :
- Ctrl+C : Quitter l'application
- Ctrl+L : Effacer le chat
- Escape : Retour au champ de saisie

### Chat Simple (Interface Textuel Basique)

Interface légère et compatible, idéale pour les environnements avec contraintes.

# Lancer l'interface simple
cloudya chat --no-graphics

# Avec mode exécution
cloudya chat --no-graphics -e

Fonctionnalités Chat Simple :
- 🚀 Démarrage rapide sans dépendances graphiques
- 💻 Compatible avec tous les terminaux
- 📊 Affichage formaté des réponses
- 💾 Sauvegarde automatique de l'historique
- 🔄 Commandes de contrôle intégrées

Commandes spéciales :
- quit, exit, q : Quitter le chat
- clear : Effacer l'écran
- Ctrl+C : Interruption d'urgence

### Comparaison des interfaces

| Fonctionnalité | Chat TUI | Chat Simple |
|----------------|----------|-------------|
| Coloration syntaxique | ✅ | ❌ |
| Formatage Markdown | ✅ | ✅ (basique) |
| Dépendances | textual, rich | Aucune |
| Performance | Moyenne | Élevée |
| Compatibilité | Moderne | Universelle |
| Navigation | Clavier/Souris | Clavier |
| Scroll | Automatique | Manuel |

## 🔧 API Backend

### Architecture du backend

Le backend Cloudya est construit avec FastAPI et offre une API REST complète :

# Endpoints principaux
POST /api/auth/login          # Authentification
POST /api/auth/register       # Inscription
POST /api/command             # Traitement des commandes IA
GET  /api/tokens/info         # Informations du token
POST /api/tokens/recharge     # Recharge de tokens
GET  /health                  # Santé du service

### Modèles de données

# Requête de commande
{
  "user_input": "Créer un cluster Kubernetes",
  "execution_mode": "dry_run"  # ou "supervised"
}

# Réponse de commande
{
  "action": "kubectl create cluster...",
  "explanation": "Pour créer un cluster...",
  "output": "Résultat d'exécution...",
  "execution_status": "dry_run",
  "token_usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350,
    "remaining_balance": 9650
  }
}

### Déploiement du backend

# Développement local
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production avec Docker
docker build -t cloudya-api .
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  -e DATABASE_URL="postgresql://..." \
  cloudya-api

# Production avec docker-compose
docker-compose up -d

### Configuration du backend

# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - STRIPE_API_KEY=${STRIPE_API_KEY}
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: cloudya
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
  
  redis:
    image: redis:alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}

## 🧪 Tests et développement

### Environnement de développement local

Cloudya inclut un serveur de test complet pour le développement local :

# Démarrer l'environnement de développement
cd tests/
./start_dev_simple.sh

Ou manuellement :

# Terminal 1: Serveur de test
cd tests/
python simple_test_server.py

# Terminal 2: Configuration
python ../setup_test.py

# Terminal 3: Tests
python test_simple.py

### Serveur de test

Le serveur de test simule toutes les fonctionnalités de l'API de production :

    ✅ Authentification simulée
    🤖 Réponses IA mockées par domaine (AWS, Kubernetes, etc.)
    💰 Gestion des tokens simulée
    🔄 Délais de réponse réalistes
    📊 Métriques d'usage

### Tests automatisés

# Lancer tous les tests
python tests/test_simple.py

# Tests spécifiques
python tests/test_api.py
python tests/test_cli.py
python tests/test_security.py

### Mode debug

# Activer le mode debug
export CLOUDYA_DEBUG=1
cloudya ask "test"  # Affiche des informations de debug

# Monitoring en temps réel
python tests/monitor_test.py

## 🔒 Sécurité

### Validation des commandes

Cloudya implémente plusieurs couches de sécurité :

# Liste blanche des commandes autorisées
ALLOWED_COMMANDS = [
    r"^aws\s+([a-zA-Z0-9\-]+\s+)+",      # Commandes AWS
    r"^terraform\s+(init|plan|apply)",    # Terraform sécurisé
    r"^kubectl\s+([a-zA-Z0-9\-]+\s+)+",  # Kubernetes
    r"^docker\s+(build|run|ps|images)"   # Docker de base
]

# Liste noire des motifs dangereux
FORBIDDEN_PATTERNS = [
    r"rm\s+(\-rf?\s+)?(\/|\~|\.\.)",     # Suppression dangereuse
    r">(\/etc\/|\~\/\.ssh\/)",           # Écriture système
    r"curl\s+.*\s+\|\s+bash",            # Exécution depuis internet
    r"sudo\s+",                          # Élévation de privilèges
]

### Sandbox d'exécution

# Exécution isolée avec Docker
def execute_in_sandbox(command):
    container = docker_client.containers.run(
        "cloudya-sandbox:latest",
        command,
        remove=True,
        network_mode="none",          # Isolation réseau
        cap_drop=["ALL"],            # Suppression privilèges
        security_opt=["no-new-privileges:true"],
        read_only=True,              # Système fichiers RO
        mem_limit="256m",            # Limite mémoire
        cpu_quota=50000,             # Limite CPU
        timeout=30                   # Timeout
    )

### Authentification et autorisation

    🔐 Tokens JWT sécurisés avec expiration
    🔄 Rotation automatique des secrets
    📝 Audit logging complet
    🚨 Détection d'anomalies d'usage
    🛡️ Protection contre les attaques par déni de service

### Chiffrement

    🔒 HTTPS obligatoire en production
    🗃️ Chiffrement des données sensibles en base
    🔑 Gestion sécurisée des clés API
    📡 Chiffrement des communications inter-services

## 💰 Modèle économique

### Plans tarifaires

| Plan | Prix/mois | Tokens inclus | Fonctionnalités |
|------|-----------|---------------|-----------------|
| Free | 0€ | 1,000 | • Commandes de base<br>• Chat simple<br>• Support communautaire |
| Starter | 9.99€ | 10,000 | • Toutes les fonctionnalités<br>• Chat TUI<br>• Support email |
| Pro | 29.99€ | 50,000 | • Mode exécution<br>• API priority<br>• Intégrations avancées |
| Enterprise | 99.99€ | 200,000 | • Support 24/7<br>• SLA garantis<br>• Déploiement on-premise |

### Système de tokens

    1 token ≈ 1 mot généré par l'IA
    Recharge automatique mensuelle selon le plan
    Achat de tokens supplémentaires : 1000 tokens = 1€
    Rollover limité : maximum 20% du plan mensuel

### Intégration des paiements

# Créer un abonnement
cloudya subscribe --plan pro --payment-method pm_xxx

# Recharger des tokens
cloudya tokens recharge --amount 5000 --payment-method pm_xxx

# Gérer l'abonnement
cloudya subscription info
cloudya subscription cancel

### Webhooks et facturation

Le système gère automatiquement :
- ✅ Renouvellements d'abonnements
- 📧 Notifications de facturation
- ⚠️ Alertes de quota
- 🔄 Échecs de paiement et retry
- 📊 Analytics de revenus

## 🤝 Contribuer

### Guide de contribution

    Fork le repository
    Créer une branche feature (git checkout -b feature/AmazingFeature)
    Commiter vos changements (git commit -m 'Add AmazingFeature')
    Pusher vers la branche (git push origin feature/AmazingFeature)
    Ouvrir une Pull Request

### Standards de développement

# Installation de l'environnement de développement
pip install -e ".[dev]"
pre-commit install

# Tests avant commit
pytest tests/
black cloudya/
flake8 cloudya/
mypy cloudya/

### Structure des commits

type(scope): description courte

Description plus détaillée si nécessaire.

- Changement 1
- Changement 2

Fixes #123

Types : feat, fix, docs, style, refactor, test, chore

### Roadmap

#### Version 1.1 (Q3 2024)
- [ ] Support de Azure et GCP
- [ ] Interface web complète
- [ ] Intégrations GitLab/GitHub
- [ ] Templates de déploiement

#### Version 1.2 (Q4 2024)
- [ ] Mode collaboratif en équipe
- [ ] Monitoring et alertes intégrés
- [ ] Support Ansible et Pulumi
- [ ] Modèles IA personnalisés

#### Version 2.0 (Q1 2025)
- [ ] Déploiement on-premise
- [ ] Support multi-cloud orchestré
- [ ] Intelligence prédictive
- [ ] Compliance automatisée

## 📞 Support et communauté

### Support

    📧 Email : support@cloudya.ai
    💬 Discord : [discord.gg/cloudya](https://discord.gg/cloudya)
    📖 Documentation : [docs.cloudya.ai](https://docs.cloudya.ai)
    🐛 Issues : [GitHub Issues](https://github.com/votre-repo/cloudya/issues)

### Communauté

    🌟 Donnez une étoile sur GitHub si Cloudya vous aide
    🐦 Suivez-nous sur Twitter [@CloudyaAI](https://twitter.com/CloudyaAI)
    📝 Partagez vos cas d'usage et retours
    🎯 Participez aux discussions et propositions d'améliorations

### FAQ

Q: Cloudya stocke-t-il mes données sensibles ?
R: Non, Cloudya ne stocke que les métadonnées d'usage. Vos données de production restent dans votre infrastructure.

Q: Puis-je utiliser Cloudya en mode hors-ligne ?
R: Une version hors-ligne est prévue pour la version Enterprise avec des modèles IA auto-hébergés.

Q: Cloudya supporte-t-il d'autres langues que l'anglais ?
R: Actuellement en français et anglais. Support multilingue étendu prévu pour v1.1.

Q: Comment puis-je intégrer Cloudya dans mes scripts existants ?
R: Utilisez l'API REST ou les commandes CLI avec output JSON (--output json).

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

MIT License

Copyright (c) 2024 Cloudya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

<div align="center">

Cloudya - Simplifiez votre infrastructure cloud avec l'IA

[🌐 Site Web](https://cloudya.ai) • [📚 Documentation](https://docs.cloudya.ai) • [💬 Discord](https://discord.gg/cloudya) • [🐦 Twitter](https://twitter.com/CloudyaAI)

Fait avec ❤️ pour la communauté DevOps

</div>
