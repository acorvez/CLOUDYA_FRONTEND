"""
Module pour la gestion des applications Ansible
"""
import os
import yaml
from rich.console import Console

from .ansible import get_apps_dir

console = Console()

def get_available_apps():
    """
    Récupère la liste des applications disponibles
    
    Returns:
        Liste des applications disponibles
    """
    apps = []
    apps_dir = get_apps_dir()
    
    # Vérifier si le répertoire existe
    if not os.path.exists(apps_dir):
        return apps
    
    # Parcourir le répertoire des applications
    for app_name in os.listdir(apps_dir):
        app_dir = os.path.join(apps_dir, app_name)
        if os.path.isdir(app_dir):
            # Vérifier si le fichier manifest.yaml existe
            manifest_path = os.path.join(app_dir, "manifest.yaml")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = yaml.safe_load(f)
                    
                    # Ajouter l'application à la liste
                    app = {
                        "name": manifest.get("name", app_name),
                        "type": manifest.get("type", "ansible"),
                        "description": manifest.get("description", ""),
                        "platforms": manifest.get("platforms", []),
                        "parameters": manifest.get("parameters", [])
                    }
                    apps.append(app)
                except Exception as e:
                    console.print(f"[yellow]Erreur lors de la lecture du manifest {manifest_path}: {str(e)}[/yellow]")
    
    # Si aucune application n'est trouvée, utiliser des applications fictives pour la démonstration
    if not apps:
        apps = [
            {
                "name": "WordPress",
                "type": "ansible",
                "description": "Système de gestion de contenu pour les sites web",
                "platforms": ["aws", "gcp", "azure", "proxmox", "vmware", "openstack"],
                "parameters": [
                    {
                        "name": "domain",
                        "description": "Nom de domaine pour WordPress",
                        "required": True
                    },
                    {
                        "name": "admin_user",
                        "description": "Nom d'utilisateur administrateur",
                        "default": "admin",
                        "required": False
                    },
                    {
                        "name": "admin_password",
                        "description": "Mot de passe administrateur",
                        "default": "",
                        "required": True
                    },
                    {
                        "name": "db_password",
                        "description": "Mot de passe de la base de données",
                        "default": "",
                        "required": True
                    }
                ]
            },
            {
                "name": "Nextcloud",
                "type": "docker",
                "description": "Cloud privé pour le stockage et la collaboration",
                "platforms": ["aws", "gcp", "azure", "proxmox", "vmware", "openstack"],
                "parameters": [
                    {
                        "name": "domain",
                        "description": "Nom de domaine pour Nextcloud",
                        "required": True
                    },
                    {
                        "name": "admin_user",
                        "description": "Nom d'utilisateur administrateur",
                        "default": "admin",
                        "required": False
                    },
                    {
                        "name": "admin_password",
                        "description": "Mot de passe administrateur",
                        "default": "",
                        "required": True
                    }
                ]
            },
            {
                "name": "LAMP",
                "type": "ansible",
                "description": "Stack Linux, Apache, MySQL, PHP",
                "platforms": ["aws", "gcp", "azure", "proxmox", "vmware", "openstack"],
                "parameters": [
                    {
                        "name": "mysql_password",
                        "description": "Mot de passe root MySQL",
                        "required": True
                    },
                    {
                        "name": "php_version",
                        "description": "Version de PHP",
                        "default": "8.0",
                        "required": False
                    }
                ]
            }
        ]
    
    return apps

def get_app_info(app_name):
    """
    Récupère les informations d'une application
    
    Args:
        app_name: Nom de l'application
        
    Returns:
        Dictionnaire des informations de l'application ou None si non trouvée
    """
    apps = get_available_apps()
    
    for app in apps:
        if app["name"].lower() == app_name.lower():
            return app
    
    return None
