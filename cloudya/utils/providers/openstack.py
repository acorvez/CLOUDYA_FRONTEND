"""
Module de connexion à OpenStack
"""
import os
import subprocess
import yaml
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from ..credentials import load_credentials_config, save_credentials_config, is_command_available

console = Console()

def connect(auth_url=None, username=None, password=None, project_name=None, cloud_name=None):
    """
    Se connecte à OpenStack
    
    Args:
        auth_url (str, optional): URL d'authentification OpenStack
        username (str, optional): Nom d'utilisateur OpenStack
        password (str, optional): Mot de passe OpenStack
        project_name (str, optional): Nom du projet OpenStack
        cloud_name (str, optional): Nom du cloud dans clouds.yaml
    """
    # Vérifier si la commande OpenStack CLI est disponible
    if not is_command_available("openstack"):
        console.print("[red]OpenStack CLI n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez OpenStack CLI via: pip install python-openstackclient")
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si cloud_name est fourni, on utilise directement ce profil
    if cloud_name:
        # Vérifier si le profil existe dans clouds.yaml
        clouds_file = Path.home() / ".config" / "openstack" / "clouds.yaml"
        if not clouds_file.exists():
            console.print(f"[yellow]Le fichier clouds.yaml n'existe pas à {clouds_file}[/yellow]")
            create_clouds = Confirm.ask("Voulez-vous créer un nouveau fichier clouds.yaml?")
            if not create_clouds:
                return
            
            # Créer le répertoire si nécessaire
            os.makedirs(clouds_file.parent, exist_ok=True)
            
            # Créer un fichier clouds.yaml vide
            with open(clouds_file, "w") as f:
                yaml.dump({"clouds": {}}, f)
        
        # Si auth_url, username, password et project_name sont fournis, on les ajoute au clouds.yaml
        if auth_url and username and project_name:
            try:
                with open(clouds_file, "r") as f:
                    clouds_config = yaml.safe_load(f) or {"clouds": {}}
                
                if "clouds" not in clouds_config:
                    clouds_config["clouds"] = {}
                
                # Ajouter ou mettre à jour le profil
                clouds_config["clouds"][cloud_name] = {
                    "auth": {
                        "auth_url": auth_url,
                        "username": username,
                        "password": password if password else "",
                        "project_name": project_name
                    }
                }
                
                with open(clouds_file, "w") as f:
                    yaml.dump(clouds_config, f)
                
                console.print(f"[green]Profil '{cloud_name}' ajouté/mis à jour dans clouds.yaml[/green]")
            except Exception as e:
                console.print(f"[red]Erreur lors de la mise à jour de clouds.yaml: {e}[/red]")
                return
    else:
        # Si on n'a pas de cloud_name, on demande les informations manquantes
        if "default_cloud" in credentials.get("openstack", {}):
            cloud_name = credentials["openstack"]["default_cloud"]
        else:
            # Vérifier si clouds.yaml existe et contient des profils
            clouds_file = Path.home() / ".config" / "openstack" / "clouds.yaml"
            cloud_profiles = []
            
            if clouds_file.exists():
                try:
                    with open(clouds_file, "r") as f:
                        clouds_config = yaml.safe_load(f) or {"clouds": {}}
                    
                    if "clouds" in clouds_config:
                        cloud_profiles = list(clouds_config["clouds"].keys())
                except Exception:
                    pass
            
            if cloud_profiles:
                console.print("[bold]Profils OpenStack disponibles:[/bold]")
                for i, p in enumerate(cloud_profiles, 1):
                    console.print(f"{i}. {p}")
                cloud_idx = Prompt.ask("Sélectionnez un profil (numéro)", default="1")
                try:
                    cloud_name = cloud_profiles[int(cloud_idx) - 1]
                except (ValueError, IndexError):
                    cloud_name = Prompt.ask("Entrez le nom du profil OpenStack", default="")
            else:
                cloud_name = Prompt.ask("Entrez le nom du profil OpenStack", default="")
                
                # Si pas de profil et pas d'information d'authentification, demander
                if not auth_url:
                    auth_url = Prompt.ask("URL d'authentification OpenStack", default="")
                if not username:
                    username = Prompt.ask("Nom d'utilisateur OpenStack", default="")
                if not password:
                    password = Prompt.ask("Mot de passe OpenStack", password=True)
                if not project_name:
                    project_name = Prompt.ask("Nom du projet OpenStack", default="")
                
                # Créer le profil dans clouds.yaml
                if auth_url and username and project_name:
                    try:
                        clouds_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        if clouds_file.exists():
                            with open(clouds_file, "r") as f:
                                clouds_config = yaml.safe_load(f) or {"clouds": {}}
                        else:
                            clouds_config = {"clouds": {}}
                        
                        if "clouds" not in clouds_config:
                            clouds_config["clouds"] = {}
                        
                        # Ajouter le profil
                        clouds_config["clouds"][cloud_name] = {
                            "auth": {
                                "auth_url": auth_url,
                                "username": username,
                                "password": password if password else "",
                                "project_name": project_name
                            }
                        }
                        
                        with open(clouds_file, "w") as f:
                            yaml.dump(clouds_config, f)
                        
                        console.print(f"[green]Profil '{cloud_name}' ajouté dans clouds.yaml[/green]")
                    except Exception as e:
                        console.print(f"[red]Erreur lors de la création de clouds.yaml: {e}[/red]")
                        return
    
    # Sauvegarder les préférences
    if "openstack" not in credentials:
        credentials["openstack"] = {}
    if cloud_name:
        credentials["openstack"]["default_cloud"] = cloud_name
    save_credentials_config(credentials)
    
    # Construire la commande pour tester la connexion
    env = os.environ.copy()
    env["OS_CLOUD"] = cloud_name
    
    console.print(f"[bold]Connexion à OpenStack avec le profil[/bold] [cyan]{cloud_name}[/cyan]")
    
    try:
        # Tester la connexion en listant les projets
        result = subprocess.run(
            ["openstack", "project", "list"],
            env=env,
            check=True
        )
        
        # Afficher les informations de connexion
        console.print("[bold green]Connecté avec succès à OpenStack![/bold green]")
        console.print(f"[bold]Profil:[/bold] [cyan]{cloud_name}[/cyan]")
        
        # Exécuter openstack server list pour montrer que ça fonctionne
        console.print("\n[bold]Liste des serveurs:[/bold]")
        subprocess.run(["openstack", "server", "list"], env=env)
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Erreur lors de la connexion à OpenStack: {e}[/red]")
