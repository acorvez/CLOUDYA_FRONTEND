"""
Module de base pour la gestion d'Ansible et l'installation d'applications
"""
import os
import subprocess
import json
import yaml
from pathlib import Path
import shutil
import datetime
import uuid
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table

# Importer les sous-modules
from .ansible_inventory import prepare_inventory
from .ansible_apps import get_available_apps, get_app_info
from .ansible_deployment import (
    prepare_app_deployment,
    deploy_ansible_app,
    deploy_docker_app,
    get_app_deployment,
    list_app_deployments,
    uninstall_app
)
from .ansible_instances import get_terraform_instances, select_instance

console = Console()

def get_ansible_path():
    """
    Récupère le chemin vers l'exécutable Ansible
    """
    # Charger la configuration
    from .config import load_config
    config = load_config()
    
    # Récupérer le chemin configuré ou utiliser 'ansible-playbook' par défaut
    ansible_path = config.get("ansible_path", "ansible-playbook")
    
    return ansible_path

def get_cloudya_dir():
    """
    Récupère le répertoire de base de Cloudya
    """
    return os.path.expanduser("~/.cloudya")

def get_templates_dir():
    """
    Récupère le répertoire des templates d'applications
    """
    from .config import load_config
    config = load_config()
    
    templates_dir = config.get("templates_dir", os.path.expanduser("~/.cloudya/templates"))
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(templates_dir, exist_ok=True)
    
    return templates_dir

def get_apps_dir():
    """
    Récupère le répertoire des applications
    """
    apps_dir = os.path.join(get_templates_dir(), "apps")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(apps_dir, exist_ok=True)
    
    return apps_dir

def get_app_deployments_dir():
    """
    Récupère le répertoire des déploiements d'applications
    """
    app_deployments_dir = os.path.join(get_cloudya_dir(), "app_deployments")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(app_deployments_dir, exist_ok=True)
    
    return app_deployments_dir

def determine_target(platform):
    """
    Détermine une cible de déploiement pour une plateforme
    
    Args:
        platform: Plateforme cible
        
    Returns:
        Instance cible ou None si aucune trouvée
    """
    # Filtrer les instances par plateforme
    instances = get_terraform_instances()
    platform_instances = [i for i in instances if i["platform"].lower() == platform.lower()]
    
    if not platform_instances:
        console.print(f"[yellow]Aucune instance trouvée pour la plateforme '{platform}'.[/yellow]")
        use_any = Confirm.ask("Voulez-vous voir toutes les instances disponibles (toutes plateformes)?")
        if use_any:
            return select_instance()
        else:
            return None
    
    # S'il n'y a qu'une seule instance, l'utiliser directement
    if len(platform_instances) == 1:
        instance = platform_instances[0]
        confirm = Confirm.ask(
            f"Utiliser l'instance '{instance['name']}' ({instance['ip']}) ?",
            default=True
        )
        if confirm:
            return instance
    
    # Sinon, demander à l'utilisateur de choisir
    return select_instance(platform)
