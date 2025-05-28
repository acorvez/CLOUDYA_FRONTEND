# Cloudya

Cloudya est une CLI DevOps intelligente qui automatise le déploiement, la supervision et le diagnostic d'infrastructures cloud via une interface en ligne de commande simple et un assistant IA (premium).

## Installation

### Depuis pip (recommandé)

```bash
pip install cloudya
```

### Depuis les sources

```bash
git clone https://github.com/votre-repo/cloudya.git
cd cloudya
pip install -e .
```

## Structure du projet

```
cloudya/
├── cli.py                  # Point d'entrée principal
├── commands/               # Commandes de la CLI
│   ├── deploy.py           # Déploiement avec Terraform
│   ├── app.py              # Gestion des applications
│   ├── diagnose.py         # Diagnostic des problèmes
│   ├── monitor.py          # Supervision des ressources
│   └── chat.py             # Assistant IA (premium)
├── utils/                  # Utilitaires
│   ├── config.py           # Gestion de la configuration
│   ├── terraform.py        # Wrapper Terraform
│   ├── ansible.py          # Wrapper Ansible
│   └── system.py           # Utilitaires système
└── templates/              # Templates par défaut
    ├── terraform/          # Templates Terraform
    ├── ansible/            # Playbooks Ansible
    └── apps/               # Applications préconfigurées
```

## Configuration

Cloudya stocke sa configuration dans `~/.cloudya/config.yaml`. Ce fichier est créé automatiquement au premier lancement.

### Structure de la configuration

```yaml
auth:
  token: your_token_here
  email: your_email@example.com
preferences:
  default_provider: aws
  default_region: eu-west-3
  terraform_path: terraform
  ansible_path: ansible-playbook
  docker_path: docker
paths:
  templates: ~/.cloudya/templates
  deployments: ~/.cloudya/deployments
  logs: ~/.cloudya/logs
```

## Utilisation

### Authentification

```bash
# Enregistrement local (sans IA)
cloudya register --email user@example.com

# Connexion (nécessaire pour les fonctionnalités IA premium)
cloudya login --token your_token_here
```

### Déploiement d'infrastructures

```bash
# Lister les templates disponibles
cloudya deploy list

# Afficher les détails d'un template
cloudya deploy show aws/vpc

# Déployer une infrastructure
cloudya deploy --template aws/vpc --params vpc_cidr=10.0.0.0/16,region=eu-west-3
```

### Gestion des applications

```bash
# Lister les applications disponibles
cloudya app list

# Afficher les détails d'une application
cloudya app show nextcloud

# Installer une application
cloudya app install nextcloud --platform aws --params domain=cloud.example.com

# Désinstaller une application
cloudya app uninstall app_id
```

### Diagnostic

```bash
# Diagnostiquer un service
cloudya diagnose --service nginx

# Diagnostiquer un service localement (sans IA)
cloudya diagnose local --service nginx
```

### Supervision

```bash
# Surveiller les ressources système
cloudya monitor

# Surveiller un service spécifique
cloudya monitor --service nginx

# Générer un rapport de performance
cloudya monitor report --days 7 --output report.html
```

### Assistant IA (premium)

```bash
# Démarrer une conversation avec l'assistant IA
cloudya chat

# Diagnostiquer un service avec l'IA
cloudya chat diagnose --service nginx

# Analyser l'infrastructure
cloudya chat analyze

# Générer un template personnalisé avec l'IA
cloudya chat generate --name custom-eks --provider aws
```

## Templates

### Structure d'un template Terraform

Chaque template contient un fichier `manifest.yaml` qui décrit les métadonnées et paramètres du template.

```yaml
name: "VPC AWS"
description: "Crée un VPC AWS avec des sous-réseaux publics et privés"
provider: "aws"
parameters:
  - name: "vpc_cidr"
    description: "Bloc CIDR pour le VPC"
    default: "10.0.0.0/16"
    required: true
  - name: "region"
    description: "Région AWS"
    default: "eu-west-3"
    required: false
platforms:
  - aws
```

### Structure d'une application

```yaml
name: "NextCloud"
description: "Cloud privé pour le stockage et la collaboration"
type: "docker"  # "docker" ou "ansible"
platforms:
  - aws
  - gcp
  - azure
  - proxmox
  - vmware
  - openstack
parameters:
  - name: "domain"
    description: "Nom de domaine pour NextCloud"
    required: true
  - name: "admin_user"
    description: "Nom d'utilisateur administrateur"
    default: "admin"
    required: false
```

## Licence

MIT
