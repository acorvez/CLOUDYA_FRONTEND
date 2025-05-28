import os
import subprocess
import json
import yaml
from pathlib import Path
import shutil
import datetime
import uuid
import socket
import ipaddress

from cloudya.utils.config import load_config

def get_ansible_path():
    """
    Récupère le chemin vers l'exécutable Ansible
    """
    # Charger la configuration
    config_file = os.path.expanduser("~/.cloudya/config.yaml")
    config = load_config(config_file)
    
    # Récupérer le chemin configuré ou utiliser 'ansible-playbook' par défaut
    ansible_path = config.get("preferences", {}).get("ansible_path", "ansible-playbook")
    
    return ansible_path

def get_docker_path():
    """
    Récupère le chemin vers l'exécutable Docker
    """
    # Charger la configuration
    config_file = os.path.expanduser("~/.cloudya/config.yaml")
    config = load_config(config_file)
    
    # Récupérer le chemin configuré ou utiliser 'docker' par défaut
    docker_path = config.get("preferences", {}).get("docker_path", "docker")
    
    return docker_path

def get_apps_dir():
    """
    Récupère le répertoire des applications
    """
    templates_dir = os.path.expanduser("~/.cloudya/templates")
    apps_dir = os.path.join(templates_dir, "apps")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(apps_dir, exist_ok=True)
    
    return apps_dir

def get_app_deployments_dir():
    """
    Récupère le répertoire des déploiements d'applications
    """
    deployments_dir = os.path.expanduser("~/.cloudya/deployments/apps")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(deployments_dir, exist_ok=True)
    
    return deployments_dir

def get_available_apps():
    """
    Récupère la liste des applications disponibles
    """
    apps = []
    apps_dir = get_apps_dir()
    
    # Vérifier si le répertoire existe
    if not os.path.exists(apps_dir):
        return apps
    
    # Parcourir le répertoire des applications
    for item in os.listdir(apps_dir):
        app_dir = os.path.join(apps_dir, item)
        
        if os.path.isdir(app_dir):
            # Vérifier si le répertoire contient un fichier manifest.yaml
            manifest_path = os.path.join(app_dir, "manifest.yaml")
            
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = yaml.safe_load(f)
                    
                    # Ajouter l'application à la liste
                    app = {
                        "name": manifest.get("name", item),
                        "type": manifest.get("type", "ansible"),
                        "platforms": manifest.get("platforms", []),
                        "description": manifest.get("description", "")
                    }
                    apps.append(app)
                except Exception as e:
                    print(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
    
    return apps

def get_app_info(app_name):
    """
    Récupère les informations d'une application
    """
    apps_dir = get_apps_dir()
    app_dir = os.path.join(apps_dir, app_name)
    
    # Vérifier si le répertoire existe
    if not os.path.exists(app_dir):
        return None
    
    # Vérifier si le manifest existe
    manifest_path = os.path.join(app_dir, "manifest.yaml")
    if not os.path.exists(manifest_path):
        return None
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Créer l'objet application
        app = {
            "name": manifest.get("name", app_name),
            "type": manifest.get("type", "ansible"),
            "platforms": manifest.get("platforms", []),
            "description": manifest.get("description", ""),
            "parameters": manifest.get("parameters", [])
        }
        
        return app
    except Exception as e:
        print(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
        return None

def determine_target(platform):
    """
    Détermine une cible de déploiement pour une plateforme donnée
    """
    # Dans une implémentation réelle, vous pourriez interroger votre infrastructure
    # pour trouver une cible appropriée. Pour l'instant, nous utilisons des valeurs par défaut.
    
    if platform == "local":
        return "localhost"
    elif platform in ["aws", "gcp", "azure", "openstack"]:
        # Dans ce cas, il faudrait interroger l'API du cloud pour obtenir les instances
        # Pour l'instant, on retourne None pour indiquer qu'il faut spécifier une cible
        return None
    elif platform in ["vmware", "proxmox", "nutanix"]:
        # Idem pour les infrastructures virtualisées
        return None
    else:
        return None

def prepare_app_deployment(app_name, platform, params, target):
    """
    Prépare un déploiement d'application
    """
    # Récupérer les informations de l'application
    app_info = get_app_info(app_name)
    if not app_info:
        raise ValueError(f"Application '{app_name}' non trouvée.")
    
    # Vérifier si la plateforme est supportée
    if platform not in app_info.get("platforms", []):
        raise ValueError(f"La plateforme '{platform}' n'est pas supportée pour l'application '{app_name}'.")
    
    # Créer un ID unique pour le déploiement
    deployment_id = str(uuid.uuid4())
    
    # Créer le répertoire de déploiement
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, deployment_id)
    os.makedirs(deployment_dir, exist_ok=True)
    
    # Copier les fichiers de l'application
    apps_dir = get_apps_dir()
    app_dir = os.path.join(apps_dir, app_name)
    
    # Copier les fichiers spécifiques à la plateforme si disponibles
    platform_dir = os.path.join(app_dir, platform)
    if os.path.exists(platform_dir):
        # Copier les fichiers spécifiques à la plateforme
        for item in os.listdir(platform_dir):
            source = os.path.join(platform_dir, item)
            destination = os.path.join(deployment_dir, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    else:
        # Copier les fichiers génériques
        for item in os.listdir(app_dir):
            if item != "manifest.yaml" and not os.path.isdir(os.path.join(app_dir, item)):
                source = os.path.join(app_dir, item)
                destination = os.path.join(deployment_dir, item)
                shutil.copy2(source, destination)
    
    # Créer le fichier d'inventaire Ansible si nécessaire
    if app_info.get("type") == "ansible":
        create_ansible_inventory(deployment_dir, target, platform)
    
    # Créer le fichier de métadonnées
    metadata = {
        "id": deployment_id,
        "name": app_name,
        "platform": platform,
        "target": target,
        "params": params,
        "type": app_info.get("type", "ansible"),
        "installed_at": datetime.datetime.now().isoformat(),
        "status": "prepared"
    }
    
    with open(os.path.join(deployment_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return deployment_dir

def create_ansible_inventory(deployment_dir, target, platform):
    """
    Crée un fichier d'inventaire Ansible pour un déploiement
    """
    inventory_content = ""
    
    # Vérifier si la cible est une adresse IP, un nom d'hôte ou un groupe
    try:
        # Essayer de parser comme une adresse IP
        ipaddress.ip_address(target)
        # Si c'est une IP, créer un inventaire simple
        inventory_content = f"""[target]
{target} ansible_connection=ssh ansible_user=root
"""
    except ValueError:
        # Si ce n'est pas une IP, c'est peut-être un nom d'hôte ou un groupe
        if target == "localhost":
            inventory_content = f"""[target]
{target} ansible_connection=local
"""
        else:
            # Pour les autres cas, utiliser une connexion SSH par défaut
            inventory_content = f"""[target]
{target} ansible_connection=ssh ansible_user=root
"""
    
    # Ajouter des variables spécifiques à la plateforme
    inventory_content += f"""
[all:vars]
platform={platform}
"""
    
    # Écrire le fichier d'inventaire
    with open(os.path.join(deployment_dir, "inventory.ini"), 'w') as f:
        f.write(inventory_content)

def deploy_ansible_app(deployment_dir, params, target):
    """
    Déploie une application avec Ansible
    """
    ansible_path = get_ansible_path()
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "installing")
    
    # Construire les extra-vars pour Ansible (paramètres)
    extra_vars = {}
    extra_vars.update(params)
    
    # Convertir les extra-vars en format JSON
    extra_vars_json = json.dumps(extra_vars)
    
    # Exécuter Ansible
    try:
        result = subprocess.run(
            [ansible_path, "-i", "inventory.ini", "playbook.yml", "-e", extra_vars_json],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution d'Ansible: {e.stderr}")
        update_app_deployment_status(deployment_dir, "failed")
        return False
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "installed")
    
    return True

def deploy_docker_app(deployment_dir, params, target):
    """
    Déploie une application avec Docker
    """
    docker_path = get_docker_path()
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "installing")
    
    # Vérifier si le fichier docker-compose.yml existe
    docker_compose_path = os.path.join(deployment_dir, "docker-compose.yml")
    if not os.path.exists(docker_compose_path):
        print(f"Fichier docker-compose.yml non trouvé dans {deployment_dir}")
        update_app_deployment_status(deployment_dir, "failed")
        return False
    
    # Si la cible est distante, il faut utiliser docker context pour se connecter à la cible
    # Pour simplifier, nous supposons que c'est localhost
    
    # Exécuter docker-compose
    try:
        result = subprocess.run(
            [docker_path, "compose", "up", "-d"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de Docker Compose: {e.stderr}")
        update_app_deployment_status(deployment_dir, "failed")
        return False
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "installed")
    
    return True

def uninstall_app(app_id):
    """
    Désinstalle une application
    """
    # Récupérer les informations du déploiement
    app_deployment = get_app_deployment(app_id)
    if not app_deployment:
        return False
    
    # Récupérer le répertoire de déploiement
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, app_id)
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "uninstalling")
    
    # Exécuter la désinstallation en fonction du type d'application
    if app_deployment.get("type") == "ansible":
        return uninstall_ansible_app(deployment_dir, app_deployment)
    elif app_deployment.get("type") == "docker":
        return uninstall_docker_app(deployment_dir, app_deployment)
    else:
        print(f"Type d'application non supporté: {app_deployment.get('type')}")
        update_app_deployment_status(deployment_dir, "failed_uninstall")
        return False

def uninstall_ansible_app(deployment_dir, app_deployment):
    """
    Désinstalle une application déployée avec Ansible
    """
    ansible_path = get_ansible_path()
    
    # Vérifier si un playbook de désinstallation existe
    uninstall_playbook = os.path.join(deployment_dir, "uninstall.yml")
    if os.path.exists(uninstall_playbook):
        # Exécuter le playbook de désinstallation
        try:
            result = subprocess.run(
                [ansible_path, "-i", "inventory.ini", "uninstall.yml"],
                cwd=deployment_dir,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la désinstallation avec Ansible: {e.stderr}")
            update_app_deployment_status(deployment_dir, "failed_uninstall")
            return False
    else:
        # Si aucun playbook de désinstallation n'existe, nous marquons simplement l'application comme désinstallée
        pass
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "uninstalled")
    
    return True

def uninstall_docker_app(deployment_dir, app_deployment):
    """
    Désinstalle une application déployée avec Docker
    """
    docker_path = get_docker_path()
    
    # Exécuter docker-compose down
    try:
        result = subprocess.run(
            [docker_path, "compose", "down", "-v"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la désinstallation avec Docker Compose: {e.stderr}")
        update_app_deployment_status(deployment_dir, "failed_uninstall")
        return False
    
    # Mettre à jour le statut
    update_app_deployment_status(deployment_dir, "uninstalled")
    
    return True

def get_app_deployment(app_id):
    """
    Récupère les informations d'un déploiement d'application
    """
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, app_id)
    
    if not os.path.exists(deployment_dir):
        return None
    
    # Lire le fichier de métadonnées
    metadata_path = os.path.join(deployment_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata
    except Exception as e:
        print(f"Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}")
        return None

def list_app_deployments():
    """
    Liste tous les déploiements d'applications
    """
    deployments = []
    app_deployments_dir = get_app_deployments_dir()
    
    if not os.path.exists(app_deployments_dir):
        return deployments
    
    for item in os.listdir(app_deployments_dir):
        deployment_dir = os.path.join(app_deployments_dir, item)
        
        if os.path.isdir(deployment_dir):
            metadata_path = os.path.join(deployment_dir, "metadata.json")
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    deployments.append(metadata)
                except Exception as e:
                    print(f"Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}")
    
    return deployments

def update_app_deployment_status(deployment_dir, status):
    """
    Met à jour le statut d'un déploiement d'application
    """
    return update_app_deployment_metadata(deployment_dir, {"status": status})

def update_app_deployment_metadata(deployment_dir, metadata_updates):
    """
    Met à jour les métadonnées d'un déploiement d'application
    """
    metadata_path = os.path.join(deployment_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        return False
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Mettre à jour les métadonnées
        metadata.update(metadata_updates)
        
        # Enregistrer les métadonnées
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour des métadonnées {metadata_path}: {str(e)}")
        return False
