# 🌩️ Cloudya CLI

<div align="center">

**Intelligent DevOps CLI for cloud infrastructure automation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)]()

*Automate your cloud infrastructure like a DevOps expert*

[Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

---

## ✨ Overview

Cloudya is a revolutionary command-line tool that transforms cloud infrastructure management into a simple and intelligent experience. With its integrated AI assistant and hierarchical template system, deploy, monitor, and diagnose your cloud environments with unprecedented efficiency.

### 🎯 **Why Cloudya?**

- 🚀 **One-command deployment** - From idea to production in minutes
- 🤖 **Integrated AI** - Intelligent assistant for all your DevOps needs
- 🎨 **Smart templates** - Extensible library of ready-to-use configurations
- 📊 **Built-in monitoring** - Automatic surveillance and diagnostics
- 🔧 **Multi-cloud** - Support for AWS, GCP, Azure, and more
- 🛡️ **Secure** - Security best practices built-in by default

---

## 🚀 Key Features

### 📦 **Infrastructure Deployment**
- Pre-configured Terraform templates (AWS, GCP, Azure)
- One-command deployment with intelligent parameters
- Multi-environment variable management
- Automatic rollback on errors
- Configuration validation before deployment

### 🤖 **Premium AI Assistant**
- Interactive chat for infrastructure management
- Custom template generation
- Automatic problem diagnosis
- Real-time optimization suggestions
- Predictive performance analysis

### 🎨 **Advanced Template System**
- **4 hierarchical levels** following XDG standards
- Integrated Terraform, Ansible, Docker templates
- Automatic installation and updates
- Community and official templates
- Complete customization

### 📱 **Application Management**
- Ready-to-deploy application catalog
- Docker, Kubernetes, virtual machine support
- Automated configuration via Ansible
- Simplified updates and rollbacks
- Applications: WordPress, NextCloud, GitLab, Monitoring...

### 🔍 **Diagnostics and Monitoring**
- Automatic infrastructure problem detection
- Real-time resource monitoring
- Customizable alerts and performance reports
- Centralized logs with intelligent analysis
- Automatic resolution suggestions

### 🔗 **Multi-Cloud Connectivity**
- Native support for AWS, Google Cloud, Microsoft Azure
- OpenStack, VMware, Proxmox, Nutanix integration
- Unified identity and access management
- Automatic failover between environments

---

## 🛠️ Installation

### Automatic installation (recommended)

```bash
# One-command installation
curl -fsSL https://raw.githubusercontent.com/acorvez/CLOUDYA_FRONTEND/main/install.sh | bash
```

### Manual installation

```bash
# Clone the repository
git clone https://github.com/acorvez/CLOUDYA_FRONTEND.git
cd CLOUDYA_FRONTEND

# Run the installation script
chmod +x install.sh
./install.sh
```

### Installation with pip

```bash
# From PyPI (when available)
pip install cloudya

# From sources
git clone https://github.com/acorvez/CLOUDYA_FRONTEND.git
cd CLOUDYA_FRONTEND
pip install .
```

### Installation verification

```bash
cloudya --version
cloudya --help
```

---

## ⚡ Quick Start

### 1. Initial configuration

```bash
# Free registration
cloudya register --email your@email.com --name "Your Name"

# Login (for premium AI features)
cloudya login --email your@email.com
```

### 2. Explore templates

```bash
# List all available templates
cloudya template list

# View templates by category
cloudya template list terraform/aws
cloudya template list apps

# Examine a specific template
cloudya template show vpc --category=terraform/aws
```

### 3. First deployment

```bash
# Deploy a simple AWS VPC
cloudya deploy --template aws/vpc \
  --params vpc_cidr=10.0.0.0/16,region=eu-west-3

# Or deploy a complete stack (infrastructure + application)
cloudya stack deploy \
  --template aws/ec2 \
  --app wordpress \
  --params domain=mysite.com,instance_type=t3.medium
```

### 4. Use the AI assistant

```bash
# Interactive chat interface
cloudya chat

# Ask a direct question
cloudya ask "How to optimize costs on my AWS infrastructure?"

# Automatic diagnosis
cloudya diagnose --service nginx
```

---

## 📖 Detailed Usage Guide

### 🏗️ **Template Management**

#### List and explore templates
```bash
# All templates
cloudya template list

# By category
cloudya template list terraform/aws
cloudya template list apps
cloudya template list config

# Detailed information
cloudya template info wordpress --category=apps
cloudya template show vpc --category=terraform/aws
```

#### Install custom templates
```bash
# From URL
cloudya template install my-vpc \
  https://raw.githubusercontent.com/user/repo/vpc.tf \
  --category=terraform/aws

# From Git repository
cloudya template install monitoring-stack \
  git+https://github.com/user/monitoring-templates.git
```

#### Manage templates
```bash
# Remove a user template
cloudya template remove my-vpc --category=terraform/aws

# View search paths
cloudya template paths

# Update templates
cloudya template update --all
```

### 🚀 **Infrastructure Deployment**

#### Available Terraform templates

**AWS**
```bash
# VPC with public/private subnets
cloudya deploy --template aws/vpc --params vpc_cidr=10.0.0.0/16

# EKS Kubernetes cluster
cloudya deploy --template aws/eks --params cluster_name=my-cluster,node_count=3

# RDS database
cloudya deploy --template aws/rds --params db_name=myapp,engine=mysql

# S3 static website
cloudya deploy --template aws/s3-website --params domain=mysite.com
```

**Google Cloud**
```bash
# GKE cluster
cloudya deploy --template gcp/gke --params cluster_name=my-gke,zone=us-central1-a

# Cloud SQL database
cloudya deploy --template gcp/cloud-sql --params db_name=myapp

# App Engine application
cloudya deploy --template gcp/app-engine --params runtime=python39
```

**Azure**
```bash
# AKS cluster
cloudya deploy --template azure/aks --params cluster_name=my-aks,location=westeurope

# Azure SQL database
cloudya deploy --template azure/sql --params server_name=myserver

# Azure Web App
cloudya deploy --template azure/webapp --params app_name=myapp
```

#### Deployment management
```bash
# List active deployments
cloudya deploy status

# View deployment details
cloudya deploy info --id deployment-123

# Destroy infrastructure
cloudya deploy destroy --id deployment-123

# Backup infrastructure
cloudya backup create --deployment-id deployment-123
```

### 📱 **Application Management**

#### Available applications

```bash
# List all applications
cloudya app list

# Application information
cloudya app show wordpress
cloudya app show nextcloud
cloudya app show gitlab
```

#### Application installation

**CMS and Blogs**
```bash
# Complete WordPress with database
cloudya app install wordpress \
  --platform aws \
  --params domain=myblog.com,admin_user=admin,admin_password=secure123

# Drupal for enterprise sites
cloudya app install drupal \
  --platform gcp \
  --params domain=mysite.com,site_name="My Site"
```

**Collaboration and Productivity**
```bash
# NextCloud - private cloud
cloudya app install nextcloud \
  --platform azure \
  --params domain=cloud.mycompany.com,admin_password=secure123

# GitLab CE - DevOps platform
cloudya app install gitlab \
  --platform aws \
  --params domain=git.mycompany.com,external_url=https://git.mycompany.com
```

**Monitoring and Observability**
```bash
# Prometheus + Grafana stack
cloudya app install monitoring \
  --platform kubernetes \
  --params grafana_domain=metrics.mycompany.com

# ELK Stack for logs
cloudya app install elk-stack \
  --platform docker \
  --params elasticsearch_memory=2g
```

#### Manage installed applications
```bash
# Status of all applications
cloudya app status

# Status of specific application
cloudya app status --id app-456

# Update an application
cloudya app update --id app-456

# Uninstall an application
cloudya app uninstall --id app-456
```

### 🤖 **AI Assistant and Chat**

#### Interactive chat interface
```bash
# Launch TUI chat (recommended)
cloudya chat

# Simple text chat mode
cloudya chat --fallback

# Execution mode (caution!)
cloudya chat --execute
```

#### Direct questions
```bash
# Infrastructure optimization
cloudya ask "How to reduce costs on my AWS infrastructure?"

# Problem solving
cloudya ask "My WordPress site is slow, what to do?"

# Best practices
cloudya ask "What are best practices for securing a Kubernetes cluster?"

# Code generation
cloudya ask "Generate a Terraform template for an AWS ALB load balancer"
```

#### Intelligent diagnosis
```bash
# General system diagnosis
cloudya diagnose

# Specific service diagnosis
cloudya diagnose --service nginx
cloudya diagnose --service mysql
cloudya diagnose --service docker

# AI diagnosis (premium)
cloudya chat diagnose --service postgresql
```

### 📊 **Monitoring and Supervision**

#### Real-time monitoring
```bash
# General system monitor
cloudya monitor

# Specific service monitor
cloudya monitor --service apache --interval 10

# Monitor with alert thresholds
cloudya monitor \
  --cpu-threshold 80 \
  --memory-threshold 90 \
  --disk-threshold 85
```

#### Reports and history
```bash
# Last 7 days report
cloudya monitor report --days 7 --output report.html

# JSON report for integration
cloudya monitor report --format json --service nginx

# Detailed performance report
cloudya monitor report \
  --service mysql \
  --days 30 \
  --include-graphs \
  --output mysql-performance.pdf
```

### 🔗 **Multi-Cloud Connections**

```bash
# AWS
cloudya connect aws --profile production --region eu-west-3

# Google Cloud
cloudya connect gcp --project my-project --config /path/to/credentials.json

# Microsoft Azure
cloudya connect azure --subscription my-subscription

# OpenStack
cloudya connect openstack --auth-url https://keystone.example.com:5000

# VMware vSphere
cloudya connect vmware --host vcenter.example.com --username admin

# Proxmox
cloudya connect proxmox --host proxmox.example.com --port 8006
```

---

## ⚙️ Advanced Configuration

### Configuration structure

Cloudya uses XDG standards to organize its files:

```
~/.config/cloudya/           # User configuration
├── config.yaml             # Main configuration
└── templates/               # Custom templates

~/.local/share/cloudya/      # User data
├── templates/               # Shared templates
├── deployments/             # Deployment history
└── logs/                    # Activity logs

~/.cache/cloudya/            # Temporary cache
├── downloaded-templates/    # Downloaded templates
└── terraform-cache/        # Terraform cache
```

### Main configuration file

`~/.config/cloudya/config.yaml`

```yaml
# Cloudya configuration
api:
  url: https://api.cloudya.ai
  timeout: 30
  max_retries: 3

preferences:
  default_provider: aws
  default_region: eu-west-3
  auto_approve: false
  colored_output: true

templates:
  default_engine: jinja2
  extensions: ['.j2', '.yaml', '.yml', '.tf', '.py']
  auto_update: true

repositories:
  - name: official
    url: https://github.com/acorvez/cloudya-templates
    branch: main
    enabled: true
  - name: community
    url: https://github.com/cloudya/community-templates
    branch: main
    enabled: true

monitoring:
  check_interval: 60
  retention_days: 30
  alerts_enabled: true
  alert_channels:
    - type: email
      address: admin@mycompany.com
    - type: slack
      webhook: https://hooks.slack.com/...

providers:
  aws:
    default_region: eu-west-3
    profile: default
  gcp:
    default_project: my-gcp-project
    default_zone: europe-west1-b
  azure:
    default_location: westeurope
    subscription: my-azure-subscription
```

### Environment variables

```bash
# Global configuration
export CLOUDYA_CONFIG_DIR="~/.config/cloudya"
export CLOUDYA_DEBUG=true
export CLOUDYA_NO_COLOR=false

# API and authentication
export CLOUDYA_API_URL="https://api.cloudya.ai"
export CLOUDYA_API_TOKEN="your-premium-token"

# Cloud providers
export AWS_PROFILE=production
export GOOGLE_CLOUD_PROJECT=my-project
export AZURE_SUBSCRIPTION_ID=my-subscription

# Custom paths
export CLOUDYA_TEMPLATES_DIR="/opt/cloudya/templates"
export TERRAFORM_CACHE_DIR="~/.cache/terraform"
```

---

## 🔧 Integrations and Ecosystem

### CI/CD

**GitHub Actions**
```yaml
name: Deploy with Cloudya
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Cloudya
        run: |
          curl -fsSL https://raw.githubusercontent.com/acorvez/CLOUDYA_FRONTEND/main/install.sh | bash
          cloudya login --token ${{ secrets.CLOUDYA_TOKEN }}
      - name: Deploy infrastructure
        run: |
          cloudya deploy --template aws/production \
            --params environment=production,region=eu-west-3
```

**GitLab CI**
```yaml
deploy:
  stage: deploy
  image: python:3.9
  before_script:
    - curl -fsSL https://raw.githubusercontent.com/acorvez/CLOUDYA_FRONTEND/main/install.sh | bash
    - cloudya login --token $CLOUDYA_TOKEN
  script:
    - cloudya stack deploy --template aws/webapp --app $APP_NAME
  only:
    - main
```

### Terraform

```hcl
# Use Cloudya outputs in your Terraform modules
data "cloudya_deployment" "vpc" {
  deployment_id = "vpc-123"
}

resource "aws_instance" "app" {
  subnet_id = data.cloudya_deployment.vpc.outputs.public_subnet_id
  # ...
}
```

### Ansible

```yaml
# Use Cloudya in your Ansible playbooks
- name: Deploy with Cloudya
  hosts: localhost
  tasks:
    - name: Create VPC
      shell: |
        cloudya deploy --template aws/vpc \
          --params vpc_cidr=10.0.0.0/16 \
          --output json
      register: vpc_deployment
    
    - name: Parse deployment output
      set_fact:
        vpc_id: "{{ (vpc_deployment.stdout | from_json).outputs.vpc_id }}"
```

### Monitoring with Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'cloudya-metrics'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: /api/metrics
    params:
      token: ['your-cloudya-token']
```

---

## 🧪 Complete Examples

### Deploy a complete application

```bash
# 1. Create infrastructure (VPC + Subnets + Security Groups)
cloudya deploy --template aws/webapp-infra \
  --params vpc_cidr=10.0.0.0/16,environment=production,region=eu-west-3

# 2. Deploy application servers
cloudya deploy --template aws/ec2-cluster \
  --params instance_type=t3.medium,min_size=2,max_size=10

# 3. Install WordPress with database
cloudya app install wordpress \
  --platform aws \
  --params domain=myblog.com,db_instance_class=db.t3.micro

# 4. Setup monitoring
cloudya app install monitoring \
  --platform aws \
  --params grafana_domain=metrics.myblog.com

# 5. Test and verify
cloudya monitor --service wordpress
cloudya diagnose --service mysql
```

### Environment migration

```bash
# 1. Backup source environment
cloudya backup create --env staging --name "migration-backup"

# 2. Create new environment
cloudya deploy --template aws/production-ready \
  --params backup_restore_id=migration-backup

# 3. Migrate data
cloudya app migrate --from staging --to production \
  --apps wordpress,mysql --strategy blue-green

# 4. Test new infrastructure
cloudya diagnose --env production --full-check

# 5. Switch traffic
cloudya dns switch --from staging.mysite.com --to production.mysite.com
```

### Complete DevOps with GitLab

```bash
# 1. Create DevOps infrastructure
cloudya stack deploy \
  --template aws/devops-platform \
  --apps gitlab,jenkins,monitoring \
  --params domain=devops.mycompany.com

# 2. Configure CI/CD runners
cloudya app configure gitlab \
  --add-runners kubernetes \
  --runner-count 5

# 3. Integrate monitoring
cloudya monitor setup \
  --services gitlab,jenkins,kubernetes \
  --alerts slack,email

# 4. Automate deployments
cloudya template generate cicd-pipeline \
  --provider aws \
  --apps frontend,backend,database
```

---

## 🏢 Enterprise Use Cases

### Multi-environment management

```bash
# Configure environments
cloudya env create --name development --provider aws --region eu-west-3
cloudya env create --name staging --provider aws --region eu-west-1  
cloudya env create --name production --provider aws --region us-east-1

# Progressive deployment
cloudya deploy --env development --template webapp --params debug=true
cloudya promote --from development --to staging --auto-tests
cloudya promote --from staging --to production --manual-approval
```

### Compliance and governance

```bash
# Compliance scanning
cloudya compliance scan --standards SOC2,GDPR,HIPAA
cloudya compliance report --format pdf --output compliance-report.pdf

# Access audit
cloudya audit users --provider aws --export csv
cloudya audit permissions --service s3 --detailed

# Cost management
cloudya costs analyze --provider aws --period last-month
cloudya costs optimize --recommendations auto-implement
```

### Backup and disaster recovery

```bash
# Automated backup strategy
cloudya backup schedule \
  --frequency daily \
  --retention 30d \
  --cross-region \
  --encryption enabled

# Disaster recovery test
cloudya dr test --scenario region-failure --env production
cloudya dr execute --plan automated-failover --confirm
```

---

## 🧑‍💻 Development and Contributing

### Development environment setup

```bash
# Clone repository
git clone https://github.com/acorvez/CLOUDYA_FRONTEND.git
cd CLOUDYA_FRONTEND

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run tests

```bash
# Unit tests
pytest tests/

# Tests with coverage
pytest --cov=cloudya --cov-report=html

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/ --slow
```

### Project structure

```
cloudya_frontend/
├── cloudya/                 # Main package
│   ├── cli/                # Command line interface
│   ├── templates/          # Default templates
│   ├── utils/              # Utilities
│   └── template_manager.py # Template manager
├── tests/                  # Tests
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── examples/               # Usage examples
```

### Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Contributing guidelines

- Follow Python code style (PEP 8)
- Add tests for new features
- Update documentation
- Ensure all tests pass

---

## 📋 Roadmap

### Version 1.1 (Q3 2025)
- [ ] Native Kubernetes support with Helm
- [ ] Optional web interface for monitoring
- [ ] ARM/Bicep templates for Azure
- [ ] GitOps integration with ArgoCD/Flux

### Version 1.2 (Q4 2025)
- [ ] Unified multi-cloud deployment
- [ ] AI for automatic cost optimization
- [ ] Integrated compliance scanner (SOC2, GDPR)
- [ ] Mobile companion app

### Version 2.0 (2026)
- [ ] Visual infrastructure designer
- [ ] Advanced AI assistant with learning
- [ ] Enterprise support with SSO
- [ ] Complete SaaS platform

---



## 🙏 Acknowledgments

- 🏗️ **HashiCorp** for Terraform, inspiration for provider architecture
- 🔧 **Red Hat** for Ansible, influencing our application management system
- 🐳 **Docker Inc.** for Docker, integrated into our deployment workflows
- 🌐 **Kubernetes Community** for Kubernetes, natively supported
- 💻 **Python Software Foundation** for Python, the language powering Cloudya
- 🤝 **Contributors** and users making Cloudya evolve every day
