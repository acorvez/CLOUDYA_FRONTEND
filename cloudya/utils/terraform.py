"""
Module pour la gestion de Terraform
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
from rich.prompt import Prompt, Confirm

console = Console()

def get_terraform_path():
    """
    Récupère le chemin vers l'exécutable Terraform
    """
    # Charger la configuration
    config = load_config()
    
    # Récupérer le chemin configuré ou utiliser 'terraform' par défaut
    terraform_path = config.get("terraform_path", "terraform")
    
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
    config = load_config()
    
    templates_dir = config.get("templates_dir", os.path.expanduser("~/.cloudya/templates"))
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(templates_dir, exist_ok=True)
    
    return templates_dir

def get_deployments_dir():
    """
    Récupère le répertoire des déploiements
    """
    config = load_config()
    
    deployments_dir = config.get("deployments_dir", os.path.expanduser("~/.cloudya/deployments"))
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(deployments_dir, exist_ok=True)
    
    return deployments_dir

def load_config():
    """
    Charge la configuration générale
    """
    config_dir = get_cloudya_dir()
    config_file = os.path.join(config_dir, "config.json")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)
    
    # Créer le fichier de configuration s'il n'existe pas
    if not os.path.exists(config_file):
        default_config = {
            "terraform_path": "terraform",
            "templates_dir": os.path.expanduser("~/.cloudya/templates"),
            "deployments_dir": os.path.expanduser("~/.cloudya/deployments"),
            "log_level": "INFO"
        }
        
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    # Charger la configuration
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Erreur lors du chargement de la configuration: {e}[/red]")
        return {
            "terraform_path": "terraform",
            "templates_dir": os.path.expanduser("~/.cloudya/templates"),
            "deployments_dir": os.path.expanduser("~/.cloudya/deployments"),
            "log_level": "INFO"
        }

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
                console.print(f"[yellow]Erreur lors de la lecture du manifest {manifest_path}: {str(e)}[/yellow]")
    
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
        console.print(f"[yellow]Erreur lors de la lecture du manifest {manifest_path}: {str(e)}[/yellow]")
        return None

def prepare_deployment(template_path, params):
    """
    Prépare un déploiement Terraform à partir d'un template
    
    Args:
        template_path: Chemin relatif du template (ex: aws/vpc)
        params: Dictionnaire des paramètres
        
    Returns:
        Chemin du répertoire de déploiement ou None en cas d'erreur
    """
    # Récupérer les informations du template
    template_info = get_template_info(template_path)
    if not template_info:
        # Pour des besoins de test, on peut simuler un template
        if os.environ.get("CLOUDYA_SIMULATE_TEMPLATES") == "1":
            console.print("[yellow]Simulation d'un template pour des besoins de test.[/yellow]")
            template_info = {
                "name": template_path.split('/')[-1].upper(),
                "provider": template_path.split('/')[0],
                "description": f"Template {template_path} simulé",
                "parameters": []
            }
        else:
            console.print(f"[red]Template '{template_path}' non trouvé.[/red]")
            return None
    
    # Créer un ID unique pour le déploiement
    deployment_id = str(uuid.uuid4())
    
    # Créer le répertoire de déploiement
    deployments_dir = get_deployments_dir()
    deployment_dir = os.path.join(deployments_dir, deployment_id)
    os.makedirs(deployment_dir, exist_ok=True)
    
    # Copier les fichiers du template si le template existe réellement
    templates_dir = get_templates_dir()
    template_dir = os.path.join(templates_dir, "terraform", template_path)
    
    if os.path.exists(template_dir):
        for item in os.listdir(template_dir):
            if item != "manifest.yaml":  # Exclure le manifest
                source = os.path.join(template_dir, item)
                destination = os.path.join(deployment_dir, item)
                
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
    else:
        # Pour des besoins de test, créer un fichier Terraform minimal
        with open(os.path.join(deployment_dir, "main.tf"), "w") as f:
            f.write('provider "aws" {\n  region = "us-east-1"\n}\n\n')
            f.write('resource "null_resource" "example" {\n}\n')
        
        with open(os.path.join(deployment_dir, "variables.tf"), "w") as f:
            f.write('variable "region" {\n  description = "AWS region"\n  default = "us-east-1"\n}\n')
    
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

def run_terraform(deployment_dir, auto_approve=False):
    """
    Exécute Terraform pour un déploiement
    
    Args:
        deployment_dir: Chemin du répertoire de déploiement
        auto_approve: Approuver automatiquement le plan Terraform
        
    Returns:
        True si le déploiement a réussi, False sinon
    """
    terraform_path = get_terraform_path()
    
    # Vérifier si terraform est installé
    try:
        subprocess.run([terraform_path, "--version"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]Terraform n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez Terraform via: https://www.terraform.io/downloads.html")
        return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "initializing")
    
    # Initialiser Terraform
    with console.status("[bold green]Initialisation de Terraform...[/bold green]"):
        try:
            result = subprocess.run(
                [terraform_path, "init"],
                cwd=deployment_dir,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]Initialisation réussie![/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors de l'initialisation de Terraform:[/red] {e.stderr}")
            update_deployment_status(deployment_dir, "failed_init")
            return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "planning")
    
    # Exécuter terraform plan
    with console.status("[bold green]Planification du déploiement...[/bold green]"):
        try:
            result = subprocess.run(
                [terraform_path, "plan", "-out=tfplan"],
                cwd=deployment_dir,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]Plan créé avec succès![/green]")
            # Afficher le plan
            console.print("\n[bold]Plan Terraform:[/bold]")
            console.print(result.stdout)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors de la planification Terraform:[/red] {e.stderr}")
            update_deployment_status(deployment_dir, "failed_plan")
            return False
    
    # Demander confirmation si auto_approve n'est pas activé
    if not auto_approve:
        proceed = Confirm.ask("Voulez-vous procéder au déploiement?")
        if not proceed:
            console.print("[yellow]Déploiement annulé.[/yellow]")
            update_deployment_status(deployment_dir, "cancelled")
            return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "applying")
    
    # Exécuter terraform apply
    with console.status("[bold green]Déploiement en cours...[/bold green]"):
        try:
            result = subprocess.run(
                [terraform_path, "apply", "-auto-approve", "tfplan"],
                cwd=deployment_dir,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]Déploiement réussi![/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors de l'application Terraform:[/red] {e.stderr}")
            update_deployment_status(deployment_dir, "failed_apply")
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
        
        outputs = json.loads(result.stdout) if result.stdout.strip() else {}
        
        # Simplifier les outputs (Terraform les renvoie dans un format complexe)
        simplified_outputs = {}
        for key, value in outputs.items():
            if isinstance(value, dict) and "value" in value:
                simplified_outputs[key] = value["value"]
            else:
                simplified_outputs[key] = value
        
        # Mettre à jour les métadonnées avec les outputs
        update_deployment_metadata(deployment_dir, {"outputs": simplified_outputs})
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        console.print(f"[yellow]Avertissement: Erreur lors de la récupération des outputs Terraform: {str(e)}[/yellow]")
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "deployed")
    
    return True

def destroy_deployment(deployment_dir):
    """
    Détruit un déploiement Terraform
    
    Args:
        deployment_dir: Chemin du répertoire de déploiement
        
    Returns:
        True si la destruction a réussi, False sinon
    """
    terraform_path = get_terraform_path()
    
    # Vérifier si terraform est installé
    try:
        subprocess.run([terraform_path, "--version"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]Terraform n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez Terraform via: https://www.terraform.io/downloads.html")
        return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "destroying")
    
    # Exécuter terraform destroy
    with console.status("[bold red]Destruction en cours...[/bold red]"):
        try:
            result = subprocess.run(
                [terraform_path, "destroy", "-auto-approve"],
                cwd=deployment_dir,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]Destruction réussie![/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors de la destruction Terraform:[/red] {e.stderr}")
            update_deployment_status(deployment_dir, "failed_destroy")
            return False
    
    # Mettre à jour le statut
    update_deployment_status(deployment_dir, "destroyed")
    
    return True

def get_deployment_dir(deployment_id):
    """
    Récupère le répertoire d'un déploiement
    
    Args:
        deployment_id: ID du déploiement
        
    Returns:
        Chemin du répertoire de déploiement ou None si non trouvé
    """
    deployments_dir = get_deployments_dir()
    deployment_dir = os.path.join(deployments_dir, deployment_id)
    
    if os.path.exists(deployment_dir):
        return deployment_dir
    
    return None

def get_deployment_info(deployment_id):
    """
    Récupère les informations d'un déploiement
    
    Args:
        deployment_id: ID du déploiement
        
    Returns:
        Dictionnaire des informations du déploiement ou None si non trouvé
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
        console.print(f"[yellow]Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}[/yellow]")
        return None

def list_deployments():
    """
    Liste tous les déploiements
    
    Returns:
        Liste des déploiements
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
                    console.print(f"[yellow]Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}[/yellow]")
    
    return deployments

def update_deployment_status(deployment_dir, status):
    """
    Met à jour le statut d'un déploiement
    
    Args:
        deployment_dir: Chemin du répertoire de déploiement
        status: Nouveau statut
        
    Returns:
        True si la mise à jour a réussi, False sinon
    """
    return update_deployment_metadata(deployment_dir, {"status": status})

def update_deployment_metadata(deployment_dir, metadata_updates):
    """
    Met à jour les métadonnées d'un déploiement
    
    Args:
        deployment_dir: Chemin du répertoire de déploiement
        metadata_updates: Dictionnaire des mises à jour
        
    Returns:
        True si la mise à jour a réussi, False sinon
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
        console.print(f"[yellow]Erreur lors de la mise à jour des métadonnées {metadata_path}: {str(e)}[/yellow]")
        return False

def create_template_skeleton(template_path, provider, description=""):
    """
    Crée un squelette de template Terraform
    
    Args:
        template_path: Chemin relatif du template (ex: aws/vpc)
        provider: Provider du template (ex: aws, gcp, azure)
        description: Description du template
        
    Returns:
        Chemin du répertoire du template créé ou None en cas d'erreur
    """
    templates_dir = get_templates_dir()
    full_path = os.path.join(templates_dir, "terraform", template_path)
    
    # Créer le répertoire s'il n'existe pas
    try:
        os.makedirs(full_path, exist_ok=True)
    except Exception as e:
        console.print(f"[red]Erreur lors de la création du répertoire {full_path}: {str(e)}[/red]")
        return None
    
    # Créer le fichier manifest.yaml
    manifest = {
        "name": os.path.basename(template_path).upper(),
        "provider": provider,
        "description": description or f"Template {template_path}",
        "parameters": [
            {
                "name": "region",
                "description": f"Région {provider.upper()}",
                "default": "us-east-1" if provider == "aws" else "us-central1" if provider == "gcp" else "eastus",
                "required": True
            }
        ]
    }
    
    try:
        with open(os.path.join(full_path, "manifest.yaml"), 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
    except Exception as e:
        console.print(f"[red]Erreur lors de la création du manifest: {str(e)}[/red]")
        return None
    
    # Créer les fichiers de base Terraform
    files = {
        "main.tf": f'provider "{provider}" {{\n  region = var.region\n}}\n',
        "variables.tf": 'variable "region" {\n  description = "Region"\n}\n',
        "outputs.tf": "# Outputs\n",
        "README.md": f"# {manifest['name']}\n\n{manifest['description']}\n\n## Usage\n\n```bash\ncloudya deploy template {template_path} --params region=us-east-1\n```\n"
    }
    
    for filename, content in files.items():
        try:
            with open(os.path.join(full_path, filename), 'w') as f:
                f.write(content)
        except Exception as e:
            console.print(f"[red]Erreur lors de la création du fichier {filename}: {str(e)}[/red]")
    
    return full_path
