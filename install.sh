#!/bin/bash

# Cloudya CLI - Script d'installation automatique
# Ce script installe Cloudya via pip puis corrige l'entry point

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions d'affichage
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║          CLOUDYA CLI INSTALLER      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# Variables
CLOUDYA_BIN="$HOME/.local/bin/cloudya"
PYTHON_CMD=""

# Détecter Python
detect_python() {
    info "Détection de Python..."
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d " " -f 2)
        success "Python trouvé: $PYTHON_VERSION"
    elif command -v python &>/dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d " " -f 2 | cut -d "." -f 1)
        if [ "$PYTHON_VERSION" -ge 3 ]; then
            PYTHON_CMD="python"
            success "Python trouvé: $(python --version)"
        else
            error "Python 3 requis, Python 2 détecté"
            exit 1
        fi
    else
        error "Python 3 non trouvé. Installez Python 3.8+"
        exit 1
    fi
}

# Détecter pip
detect_pip() {
    info "Détection de pip..."
    
    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &>/dev/null; then
        PIP_CMD="pip"
    else
        error "pip non trouvé. Installez pip"
        exit 1
    fi
    
    success "pip trouvé: $($PIP_CMD --version)"
}

# Vérifier le répertoire du projet
check_project_dir() {
    info "Vérification du répertoire du projet..."
    
    if [ ! -f "setup.py" ]; then
        error "setup.py non trouvé. Exécutez ce script depuis le répertoire cloudya_frontend"
        exit 1
    fi
    
    if [ ! -d "cloudya" ]; then
        error "Répertoire cloudya/ non trouvé"
        exit 1
    fi
    
    if [ ! -f "cloudya/cli/main.py" ]; then
        error "cloudya/cli/main.py non trouvé"
        exit 1
    fi
    
    success "Structure du projet validée"
}

# Nettoyer les installations précédentes
cleanup_previous() {
    info "Nettoyage des installations précédentes..."
    
    # Désinstaller cloudya si installé
    if $PIP_CMD show cloudya &>/dev/null; then
        warning "Désinstallation de l'ancienne version..."
        $PIP_CMD uninstall cloudya -y
    fi
    
    # Supprimer l'ancien exécutable
    if [ -f "$CLOUDYA_BIN" ]; then
        rm "$CLOUDYA_BIN"
        info "Ancien exécutable supprimé"
    fi
    
    # Nettoyer les builds
    rm -rf build/ dist/ *.egg-info/
    
    # Supprimer les packages installés
    rm -rf ~/.local/lib/python*/site-packages/cloudya*
    
    success "Nettoyage terminé"
}

# Installer via pip
install_package() {
    info "Installation de Cloudya via pip..."
    
    # S'assurer que ~/.local/bin existe
    mkdir -p ~/.local/bin
    
    # Installer le package
    if $PIP_CMD install --user . ; then
        success "Installation pip réussie"
    else
        error "Échec de l'installation pip"
        exit 1
    fi
}

# Corriger l'entry point
fix_entry_point() {
    info "Correction de l'entry point..."
    
    if [ ! -f "$CLOUDYA_BIN" ]; then
        error "Exécutable cloudya non trouvé dans $CLOUDYA_BIN"
        exit 1
    fi
    
    # Vérifier si la correction est nécessaire
    if grep -q "from cloudya.cli import main" "$CLOUDYA_BIN"; then
        warning "Entry point incorrect détecté, correction en cours..."
        
        # Créer un wrapper corrigé
        cat > "$CLOUDYA_BIN" << EOF
#!/usr/bin/env python3
"""
Cloudya CLI - Entry point corrigé
"""
import sys
import os

# Ajouter le chemin des packages locaux
import site
site.addsitedir(os.path.expanduser('~/.local/lib/python3.12/site-packages'))

try:
    from cloudya.cli.main import main
    if __name__ == '__main__':
        sys.exit(main())
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que Cloudya est installé: pip show cloudya")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
EOF
        
        # Rendre exécutable
        chmod +x "$CLOUDYA_BIN"
        success "Entry point corrigé"
    else
        success "Entry point déjà correct"
    fi
}

# Vérifier l'installation
verify_installation() {
    info "Vérification de l'installation..."
    
    # Vérifier que l'exécutable existe et est exécutable
    if [ ! -x "$CLOUDYA_BIN" ]; then
        error "Exécutable cloudya non trouvé ou non exécutable"
        exit 1
    fi
    
    # Tester l'exécutable
    if "$CLOUDYA_BIN" --help &>/dev/null; then
        success "Test cloudya --help réussi"
    else
        error "Test cloudya --help échoué"
        exit 1
    fi
    
    # Tester la version
    if "$CLOUDYA_BIN" version &>/dev/null; then
        success "Test cloudya version réussi"
    else
        warning "Test cloudya version échoué (non critique)"
    fi
}

# Configurer le PATH
setup_path() {
    info "Configuration du PATH..."
    
    # Vérifier si ~/.local/bin est dans le PATH
    if echo "$PATH" | grep -q "$HOME/.local/bin"; then
        success "~/.local/bin déjà dans le PATH"
    else
        warning "~/.local/bin absent du PATH"
        
        # Détecter le shell
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi
        
        # Ajouter au fichier de configuration du shell
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        success "PATH ajouté à $SHELL_RC"
        warning "Redémarrez votre terminal ou exécutez: source $SHELL_RC"
    fi
}

# Créer la configuration
setup_config() {
    info "Configuration de Cloudya..."
    
    CONFIG_DIR="$HOME/.cloudya"
    
    # Créer le répertoire de configuration XDG
    XDG_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/cloudya"
    XDG_DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/cloudya"
    XDG_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/cloudya"
    
    mkdir -p "$XDG_CONFIG_DIR"
    mkdir -p "$XDG_DATA_DIR/templates"
    mkdir -p "$XDG_CACHE_DIR"
    
    # Créer aussi l'ancien répertoire pour compatibilité
    mkdir -p "$CONFIG_DIR/templates"
    mkdir -p "$CONFIG_DIR/logs"
    
    # Créer un fichier de configuration par défaut si inexistant
    if [ ! -f "$XDG_CONFIG_DIR/config.yaml" ]; then
        cat > "$XDG_CONFIG_DIR/config.yaml" << EOF
# Configuration Cloudya
api:
  url: https://api.cloudya.ai

preferences:
  default_provider: aws
  default_region: us-east-1

templates:
  default_engine: jinja2
  extensions: ['.j2', '.yaml', '.yml', '.tf', '.py']

repositories:
  - name: official
    url: https://github.com/acorvez/cloudya-templates
    branch: main

paths:
  templates: ~/.local/share/cloudya/templates
  cache: ~/.cache/cloudya
  logs: ~/.local/share/cloudya/logs
EOF
        success "Configuration par défaut créée dans $XDG_CONFIG_DIR"
    else
        info "Configuration existante conservée"
    fi
    
    # Créer des templates de base
    setup_default_templates
}

# Créer les templates par défaut
setup_default_templates() {
    info "Installation des templates par défaut..."
    
    TEMPLATES_DIR="$XDG_DATA_DIR/templates"
    
    # Créer la structure
    mkdir -p "$TEMPLATES_DIR/terraform/aws"
    mkdir -p "$TEMPLATES_DIR/terraform/gcp"
    mkdir -p "$TEMPLATES_DIR/terraform/azure"
    mkdir -p "$TEMPLATES_DIR/apps"
    mkdir -p "$TEMPLATES_DIR/config"
    
    # Template de configuration
    cat > "$TEMPLATES_DIR/config/cloudya.yaml.j2" << 'EOF'
# Configuration Cloudya générée
api:
  url: {{ api_url | default('https://api.cloudya.ai') }}

preferences:
  default_provider: {{ default_provider | default('aws') }}
  default_region: {{ default_region | default('us-east-1') }}
EOF
    
    # Template VPC AWS
    cat > "$TEMPLATES_DIR/terraform/aws/vpc.tf.j2" << 'EOF'
# VPC AWS généré par Cloudya
resource "aws_vpc" "main" {
  cidr_block           = "{{ vpc_cidr | default('10.0.0.0/16') }}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "{{ vpc_name | default('cloudya-vpc') }}"
    Environment = "{{ environment | default('dev') }}"
  }
}

resource "aws_subnet" "public" {
  count             = {{ public_subnet_count | default(2) }}
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "{{ vpc_name | default('cloudya') }}-public-${count.index + 1}"
    Type = "public"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
EOF
    
    # Template WordPress
    cat > "$TEMPLATES_DIR/apps/wordpress.yml.j2" << 'EOF'
# WordPress deployment via Ansible
- name: Install WordPress
  hosts: all
  become: yes
  vars:
    domain: "{{ domain | default('localhost') }}"
    admin_user: "{{ admin_user | default('admin') }}"
    admin_password: "{{ admin_password | default('changeme') }}"
    
  tasks:
    - name: Update package cache
      package:
        update_cache: yes
    
    - name: Install LAMP stack
      package:
        name:
          - nginx
          - php-fpm
          - php-mysql
          - mysql-server
          - unzip
          - curl
        state: present
    
    - name: Download WordPress
      get_url:
        url: https://wordpress.org/latest.tar.gz
        dest: /tmp/wordpress.tar.gz
    
    - name: Extract WordPress
      unarchive:
        src: /tmp/wordpress.tar.gz
        dest: /var/www/
        remote_src: yes
        owner: www-data
        group: www-data
EOF
    
    success "Templates par défaut installés dans $TEMPLATES_DIR"
}

# Afficher les informations finales
show_final_info() {
    echo
    success "🎉 Installation de Cloudya terminée avec succès !"
    echo
    info "Informations d'installation :"
    echo "  📁 Exécutable: $CLOUDYA_BIN"
    echo "  📁 Configuration: ~/.cloudya/"
    echo "  📁 Package Python: ~/.local/lib/python*/site-packages/cloudya/"
    echo
    info "Commandes disponibles :"
    echo "  cloudya --help        # Aide générale"
    echo "  cloudya version       # Version"
    echo "  cloudya chat          # Interface de chat IA"
    echo "  cloudya deploy list   # Lister les templates"
    echo "  cloudya login         # Se connecter à l'API"
    echo
    info "Premiers pas :"
    echo "  1. cloudya register --email votre@email.com"
    echo "  2. cloudya chat"
    echo
    if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
        warning "N'oubliez pas de redémarrer votre terminal !"
    fi
}

# Fonction principale
main() {
    detect_python
    detect_pip
    check_project_dir
    cleanup_previous
    install_package
    fix_entry_point
    verify_installation
    setup_path
    setup_config
    show_final_info
}

# Gestion des erreurs
trap 'error "Installation interrompue"; exit 1' INT

# Exécution
main

exit 0
