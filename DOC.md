# Cloudya CLI

Une CLI DevOps intelligente avec assistant IA pour l'automatisation du déploiement, de la supervision et du diagnostic d'infrastructures cloud.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

## 🚀 Présentation

Cloudya est une interface en ligne de commande (CLI) DevOps intelligente qui permet de déployer, superviser et diagnostiquer des infrastructures cloud. Cloudya supporte les principaux clouds publics (AWS, GCP, Azure) ainsi que les infrastructures privées (VMware, Nutanix, Proxmox, OpenStack).

L'objectif de Cloudya est de rendre l'automatisation DevOps accessible à tous en combinant une CLI classique (gratuite) avec un assistant IA avancé (modèle freemium).

## ✨ Fonctionnalités

### CLI Classique (Gratuite)

- **Déploiement d'infrastructure** via Terraform
  - Support multi-cloud (AWS, GCP, Azure, OpenStack)
  - Support des infrastructures virtualisées (VMware, Nutanix, Proxmox)
  - Templates modulaires et extensibles

- **Déploiement d'applications** via Ansible ou Docker Compose
  - Applications préconfigurées (Nextcloud, WordPress, etc.)
  - Personnalisation des déploiements

- **Supervision basique**
  - Vérification des ressources (CPU, mémoire, stockage)
  - Intégration avec Prometheus, Node Exporter, etc.

- **Diagnostics basiques**
  - Vérification de l'état des services
  - Collecte de logs

### Assistant IA (Freemium)

- **Chat interactif CLI**
  - Compréhension du langage naturel
  - Exécution d'actions complexes à partir de prompts
  - Support multi-langues

- **Diagnostic intelligent**
  - Analyse automatique des logs et des erreurs
  - Suggestions de résolution
  - Détection proactive des problèmes

- **Génération et adaptation de templates**
  - Création de templates personnalisés
  - Adaptation de templates existants aux besoins spécifiques

## 💻 Installation

### Prérequis

- Python 3.8+
- pip
- Terraform (optionnel, pour le déploiement d'infrastructure)
- Ansible (optionnel, pour le déploiement d'applications)
- Docker (optionnel, pour les déploiements via Docker Compose)

### Installation via script (recommandé)

```bash
curl -s https://raw.githubusercontent.com/votre-repo/cloudya/main/install.sh | bash
```

### Installation via pip

```bash
pip install cloudya
```

### Installation depuis les sources

```bash
git clone https://github.com/votre-repo/cloudya.git
cd cloudya
pip install -e .
```

### Vérification de l'installation

```bash
cloudya --version
```

## 🔧 Utilisation

### Authentification

```bash
# Inscription (30 crédits IA gratuits)
cloudya register --email user@example.com

# Connexion
cloudya login --token sk_free_12345
```

### Déploiement d'infrastructure

```bash
# Lister les templates disponibles
cloudya deploy list

# Afficher les détails d'un template
cloudya deploy show aws/vpc

# Déployer une infrastructure
cloudya deploy --template aws/vpc --params vpc_cidr=10.0.0.0/16,region=eu-west-3

# Déployer sur OpenStack
cloudya deploy --template openstack/instance --params flavor=m1.medium,image=ubuntu-20.04
```

### Déploiement d'applications

```bash
# Lister les applications disponibles
cloudya app list

# Installer une application
cloudya app install nextcloud --platform aws

# Installer sur VMware
cloudya app install wordpress --platform vmware --params vcpu=2,ram=4GB
```

### Supervision

```bash
# Vérifier l'état des ressources
cloudya monitor

# Vérifier un service spécifique
cloudya monitor --service nginx
```

### Diagnostic

```bash
# Diagnostic basique (CLI gratuite)
cloudya diagnose --service nginx

# Diagnostic avancé avec IA (utilise des crédits)
cloudya diagnose --service nginx --ai
```

### Assistant IA

```bash
# Démarrer le chat interactif
cloudya chat

# Exemples de prompts:
# > Déploie un cluster Kubernetes avec Grafana et Prometheus
# > Analyse ces logs de pod et identifie le problème
# > Comment optimiser ma configuration Terraform pour AWS?
```

### Gestion des crédits

```bash
# Vérifier les crédits restants
cloudya credits

# Acheter des crédits supplémentaires
cloudya upgrade
```

## 🏗 Architecture

Cloudya est organisé autour d'une architecture modulaire qui sépare clairement les fonctionnalités gratuites des fonctionnalités premium:

```
cloudya/
├── cli.py                  # Point d'entrée principal (Typer CLI)
├── commands/               # Commandes CLI
│   ├── deploy.py           # Déploiement (Terraform/Ansible)
│   ├── diagnose.py         # Diagnostic
│   ├── monitor.py          # Supervision
│   └── chat.py             # Chat interactif IA
├── utils/                  # Utilitaires
│   ├── config.py           # Gestion de configuration
│   ├── terraform.py        # Wrapper Terraform
│   ├── ansible.py          # Wrapper Ansible
│   └── system.py           # Utilitaires système
├── templates/              # Templates par défaut
│   ├── terraform/          # Templates Terraform
│   ├── ansible/            # Playbooks Ansible
│   └── apps/               # Applications préconfigurées
```

## 📚 Templates

Cloudya utilise un système de templates modulaire et extensible pour les déploiements d'infrastructures et d'applications.

### Structure d'un template

Chaque template contient:

- `manifest.yaml`: Métadonnées et paramètres du template
- Fichiers Terraform/Ansible/Docker selon le type de template

```yaml
# Exemple de manifest.yaml
name: "VPC AWS"
description: "Module Terraform pour créer un VPC AWS avec subnets publics et privés"
provider: "aws"
parameters:
  - name: "vpc_cidr"
    description: "CIDR block pour le VPC"
    default: "10.0.0.0/16"
    required: true
  - name: "region"
    description: "Région AWS"
    default: "eu-west-3"
    required: false
platforms:
  - aws
```

### Ajout de templates personnalisés

Les utilisateurs peuvent ajouter leurs propres templates:

```bash
# Créer un template personnalisé
cloudya templates create --name my-template

# Importer un template externe
cloudya templates import https://github.com/user/terraform-template
```

Les templates personnalisés sont stockés dans `~/.cloudya/templates/`.

## 💰 Modèle Freemium

Cloudya utilise un modèle freemium:

### Offres disponibles

| Offre         | Prix    | Crédits IA |
|---------------|---------|------------|
| Free          | 0 €     | 30/mois    |
| Pro Pack      | 9 €     | 300/mois   |
| Expert Pack   | 19 €    | 1000/mois  |

### Utilisation des crédits

Chaque interaction avec l'assistant IA consomme des crédits:

- Utilisation du chat interactif: 1 crédit par requête
- Diagnostic IA avancé: 2-5 crédits selon la complexité
- Génération/adaptation de templates: 3-10 crédits selon la complexité

## 🤝 Contribuer

Les contributions sont les bienvenues! Voici comment contribuer:

1. Forker le dépôt
2. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commiter vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

## 🗓 Roadmap

- [x] Déploiement cloud automatisé (AWS, GCP, Azure)
- [x] Support des infrastructures privées (VMware, Proxmox, Nutanix, OpenStack)
- [x] Intégration IA via API LLM
- [x] Authentification et système de crédits
- [ ] Streaming des diagnostics et logs en temps réel
- [ ] Gestion de flotte multi-cloud
- [ ] Interface Web optionnelle
- [ ] Fine-tuning du modèle IA pour des diagnostics plus précis
- [ ] Support multi-utilisateurs et équipes

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

Développé avec ❤️ par [Votre Nom/Organisation]
