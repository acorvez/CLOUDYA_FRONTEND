"""
Module de connexion à Google Cloud Platform
"""
import os
import subprocess
import json
from rich.console import Console
from rich.prompt import Prompt
from ..credentials import load_credentials_config, save_credentials_config, is_command_available

console = Console()

def connect(project=None, config_file=None):
    """
    Se connecte à Google Cloud Platform
    
    Args:
        project (str, optional): Projet GCP à utiliser
        config_file (str, optional): Chemin vers le fichier de configuration GCP
    """
    # Vérifier si la commande GCP CLI est disponible
    if not is_command_available("gcloud"):
        console.print("[red]Google Cloud SDK n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez Google Cloud SDK via: https://cloud.google.com/sdk/docs/install")
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si project pas spécifié, utiliser celui dans la config ou demander
    if not project:
        if "default_project" in credentials.get("gcp", {}):
            project = credentials["gcp"]["default_project"]
        else:
            # Lister les projets GCP disponibles
            try:
                result = subprocess.run(
                    ["gcloud", "projects", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                projects = json.loads(result.stdout)
                
                if projects:
                    console.print("[bold]Projets GCP disponibles:[/bold]")
                    for i, p in enumerate(projects, 1):
                        console.print(f"{i}. {p['projectId']} - {p.get('name', 'N/A')}")
                    project_idx = Prompt.ask("Sélectionnez un projet (numéro)", default="1")
                    try:
                        project = projects[int(project_idx) - 1]["projectId"]
                    except (ValueError, IndexError):
                        project = Prompt.ask("Entrez l'ID du projet GCP", default="")
                else:
                    project = Prompt.ask("Entrez l'ID du projet GCP", default="")
            except (subprocess.CalledProcessError, json.JSONDecodeError):
                project = Prompt.ask("Entrez l'ID du projet GCP", default="")
    
    # Si fichier de config pas spécifié, utiliser celui dans la config ou le chemin par défaut
    if not config_file:
        if "config_file" in credentials.get("gcp", {}):
            config_file = credentials["gcp"]["config_file"]
    
    # Sauvegarder les préférences
    if "gcp" not in credentials:
        credentials["gcp"] = {}
    if project:
        credentials["gcp"]["default_project"] = project
    if config_file:
        credentials["gcp"]["config_file"] = config_file
    save_credentials_config(credentials)
    
    # Construire la commande pour initialiser GCP
    command = ["gcloud", "auth", "login"]
    
    # Exécuter la commande d'authentification
    console.print("[bold]Authentification à Google Cloud Platform...[/bold]")
    
    try:
        subprocess.run(command, check=True)
        
        if project:
            # Définir le projet par défaut
            console.print(f"[bold]Configuration du projet par défaut:[/bold] [cyan]{project}[/cyan]")
            subprocess.run(["gcloud", "config", "set", "project", project], check=True)
        
        # Afficher les informations de connexion
        console.print("[bold green]Connecté avec succès à Google Cloud Platform![/bold green]")
        console.print(f"[bold]Projet:[/bold] [cyan]{project}[/cyan]")
        
        # Exécuter gcloud info pour montrer que ça fonctionne
        console.print("\n[bold]Informations sur la configuration GCP:[/bold]")
        subprocess.run(["gcloud", "info", "--format=yaml"])
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Erreur lors de la connexion à GCP: {e}[/red]")
