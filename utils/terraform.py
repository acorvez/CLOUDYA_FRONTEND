import os
import subprocess
import json
import yaml
from pathlib import Path
import shutil
import datetime
import uuid

from cloudya.utils.config import load_config

def get_terraform_path():
    """
    Récupère le chemin vers l'exécutable Terraform
    """
    # Charger la configuration
    config_file = os.path.expanduser("~/.cloudya/config.yaml")
    config = load_config(config_file)
    
    # Récupérer le chemin configuré ou utiliser 'terraform' par défaut
    terraform_path = config.get("preferences", {}).get("terraform_path", "terraform")
    
    return terraform_path

def get_cloudya_dir():
    """
    Récupère le répertoire de base de Cloudya
    """
    return os.path.expanduser("~/.cloudya")

def get_templates_dir():
    """
    Récupère le répertoire des templates
    """
    config_file = os.path.expanduser("~/.cloudya/config.yaml")
    config = load_config(config_file)
    
    templates_dir = config.get("paths", {}).get("templates", os.path.expanduser("~/.cloudya/templates"))
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(templates_dir, exist_ok=True)
    
    return templates_dir

def get_deployments_dir():
    """
    Récupère le répertoire des déploiements
    """
    config_file = os.path.expanduser("~/.cloudya/config.yaml")
    config = load_config(config_file)
    
    deployments_dir = config.get("paths", {}).get("deployments", os.path.expanduser("~/.cloudya/deployments"))
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(deployments_dir, exist_ok=True)
    
    return deployments_dir

def get_available_templates():
    """
    Récupère la liste des templates Terraform disponibles
    """
    templates = []
    templates_dir = get_templates_dir()
    terraform_dir = os.path.join(templates_dir, "terraform")
    
    # Vérifier si le répertoire existe
    if not os.path.exists(terraform_dir):
        return templates
    
    # Parcourir le répertoire des templates
    for root, dirs, files in os.walk(terraform_dir):
        # Vérifier si le répertoire contient un fichier manifest.yaml
        if "manifest.yaml" in files:
            manifest_path = os.path.join(root, "manifest.yaml")
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                
                # Ajouter le template à la liste
                template = {
                    "name": manifest.get("name", os.path.basename(root)),
                    "provider": manifest.get("provider", "unknown"),
                    "description": manifest.get("description", ""),
                    "path": os.path.relpath(root, terraform_dir)
                }
                templates.append(template)
            except Exception as e:
                print(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
    
    return templates

def get_template_info(template_path):
    """
    Récupère les informations d'un template Terraform
    """
    templates_dir = get_templates_dir()
    full_path = os.path.join(templates_dir, "terraform", template_path)
    
    # Vérifier si le répertoire existe
    if not os.path.exists(full_path):
        return None
    
    # Vérifier si le manifest existe
    manifest_path = os.path.join(full_path, "manifest.yaml")
    if not os.path.exists(manifest_path):
        return None
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Créer l'objet template
        template = {
            "name": manifest.get("name", os.path.basename(full_path)),
            "provider": manifest.get("provider", "unknown"),
            "description": manifest.get("description", ""),
            "parameters": manifest.get("parameters", []),
            "path": template_path
        }
        
        return template
    except Exception as e:
        print(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
        return None

def prepare_deployment(template_path, params):
    """
    Prépare un déploiement Terraform à partir d'un template
    """
    # Récupérer les informations du template
    template_info = get_template_info(template_path)
    if not template_info:
        raise ValueError(f"Template '{template_path}' non trouvé.")
    
    # Créer un ID unique pour le déploiement
    deployment_id = str(uuid.uuid4())
    
    # Créer le répertoire de déploiement
    deployments_dir = get_deployments_dir()
    deployment_dir = os.path.join(deployments_dir, deployment_id)
    os.makedirs(deployment_dir, exist_ok=True)
    
    # Copier les fichiers du template
    templates_dir = get_templates_dir()
    template_dir = os.path.join(templates_dir, "terraform", template_path)
    
    for item in os.listdir(template_dir):
        if item != "manifest.yaml":  # Exclure le manifest
            source = os.path.join(template_dir, item)
            destination = os.path.join(deployment_dir, item)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
    
    # Créer le fichier de variables Terraform
    tfvars_content = ""
    for key, value in params.items():
        if isinstance(value, str):
            tfvars_content += f'{key} = "{value}"\n'
        else:
            tfvars_content += f'{key} = {value}\n'
    
    with open(os.path.join(deployment_dir, "terraform.tfvars"), 'w') as f:
        f.write(tfvars_content)
    
    # Créer le fichier de métadonnées
    metadata = {
        "id": deployment_id,
        "template": template_path,
        "params": params,
        "created_at": datetime.datetime.now().isoformat(),
        "status": "prepared"
    }
    
    with open(os.path.join(deployment_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return deployment_dir

def run_terraform(deployment_dir, params=None):
    """
    Exécute Terraform pour un déploiement
    """
    terraform_path = get_terraform_path()
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "initializing")
    
    # Initialiser Terraform
    try:
        result = subprocess.run(
            [terraform_path, "init"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'initialisation de Terraform: {e.stderr}")
        update_deployment_status(deployment_dir, "failed")
        return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "planning")
    
    # Exécuter terraform plan
    try:
        result = subprocess.run(
            [terraform_path, "plan", "-out=tfplan"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la planification Terraform: {e.stderr}")
        update_deployment_status(deployment_dir, "failed")
        return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "applying")
    
    # Exécuter terraform apply
    try:
        result = subprocess.run(
            [terraform_path, "apply", "-auto-approve", "tfplan"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'application Terraform: {e.stderr}")
        update_deployment_status(deployment_dir, "failed")
        return False
    
    # Récupérer les outputs
    try:
        result = subprocess.run(
            [terraform_path, "output", "-json"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        outputs = json.loads(result.stdout)
        
        # Simplifier les outputs (Terraform les renvoie dans un format complexe)
        simplified_outputs = {}
        for key, value in outputs.items():
            if "value" in value:
                simplified_outputs[key] = value["value"]
        
        # Mettre à jour les métadonnées avec les outputs
        update_deployment_metadata(deployment_dir, {"outputs": simplified_outputs})
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Erreur lors de la récupération des outputs Terraform: {str(e)}")
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "deployed")
    
    return True

def destroy_deployment(deployment_dir):
    """
    Détruit un déploiement Terraform
    """
    terraform_path = get_terraform_path()
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "destroying")
    
    # Exécuter terraform destroy
    try:
        result = subprocess.run(
            [terraform_path, "destroy", "-auto-approve"],
            cwd=deployment_dir,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la destruction Terraform: {e.stderr}")
        update_deployment_status(deployment_dir, "failed_destroy")
        return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "destroyed")
    
    return True

def get_deployment_dir(deployment_id):
    """
    Récupère le répertoire d'un déploiement
    """
    deployments_dir = get_deployments_dir()
    deployment_dir = os.path.join(deployments_dir, deployment_id)
    
    if os.path.exists(deployment_dir):
        return deployment_dir
    
    return None

def get_deployment_info(deployment_id):
    """
    Récupère les informations d'un déploiement
    """
    deployment_dir = get_deployment_dir(deployment_id)
    
    if not deployment_dir:
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

def list_deployments():
    """
    Liste tous les déploiements
    """
    deployments = []
    deployments_dir = get_deployments_dir()
    
    if not os.path.exists(deployments_dir):
        return deployments
    
    for item in os.listdir(deployments_dir):
        deployment_dir = os.path.join(deployments_dir, item)
        
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

def update_deployment_status(deployment_dir, status):
    """
    Met à jour le statut d'un déploiement
    """
    return update_deployment_metadata(deployment_dir, {"status": status})

def update_deployment_metadata(deployment_dir, metadata_updates):
    """
    Met à jour les métadonnées d'un déploiement
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
