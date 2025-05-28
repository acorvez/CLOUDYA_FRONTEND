"""
Module de connexion à AWS
"""
import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from ..credentials import load_credentials_config, save_credentials_config, is_command_available

console = Console()

def connect(profile=None, region=None):
    """
    Se connecte à AWS Cloud
    
    Args:
        profile (str, optional): Profil AWS à utiliser
        region (str, optional): Région AWS
    """
    # Vérifier si la commande AWS CLI est disponible
    if not is_command_available("aws"):
        console.print("[red]AWS CLI n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez AWS CLI via: https://aws.amazon.com/cli/")
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si profile pas spécifié, utiliser celui dans la config ou demander
    if not profile:
        if "default_profile" in credentials.get("aws", {}):
            profile = credentials["aws"]["default_profile"]
        else:
            aws_profiles = []
            try:
                # Lister les profils AWS disponibles
                aws_config_file = Path.home() / ".aws" / "config"
                if aws_config_file.exists():
                    with open(aws_config_file, "r") as f:
                        for line in f:
                            if line.strip().startswith("[profile "):
                                aws_profiles.append(line.strip()[9:-1])
                
                if aws_profiles:
                    console.print("[bold]Profils AWS disponibles:[/bold]")
                    for i, p in enumerate(aws_profiles, 1):
                        console.print(f"{i}. {p}")
                    profile_idx = Prompt.ask("Sélectionnez un profil (numéro)", default="1")
                    try:
                        profile = aws_profiles[int(profile_idx) - 1]
                    except (ValueError, IndexError):
                        profile = "default"
                else:
                    profile = Prompt.ask("Entrez le nom du profil AWS", default="default")
            except Exception:
                profile = Prompt.ask("Entrez le nom du profil AWS", default="default")
    
    # Si région pas spécifiée, utiliser celle dans la config ou demander
    if not region:
        if "default_region" in credentials.get("aws", {}):
            region = credentials["aws"]["default_region"]
        else:
            region = Prompt.ask("Entrez la région AWS", default="us-east-1")
    
    # Sauvegarder les préférences
    if "aws" not in credentials:
        credentials["aws"] = {}
    credentials["aws"]["default_profile"] = profile
    credentials["aws"]["default_region"] = region
    save_credentials_config(credentials)
    
    # Construire la commande
    command = ["aws"]
    
    if profile:
        command.extend(["--profile", profile])
    
    if region:
        command.extend(["--region", region])
    
    command.append("configure")
    command.append("list")
    
    # Exécuter la commande
    console.print(f"[bold]Connexion à AWS avec le profil[/bold] [cyan]{profile}[/cyan] [bold]et la région[/bold] [cyan]{region}[/cyan]")
    
    try:
        result = subprocess.run(command, check=True)
        
        # Si réussi, lancer un shell interactif avec les variables d'environnement configurées
        env = os.environ.copy()
        env["AWS_PROFILE"] = profile
        env["AWS_REGION"] = region
        
        # Afficher les informations de connexion
        console.print("[bold green]Connecté avec succès à AWS![/bold green]")
        console.print(f"[bold]Profil:[/bold] [cyan]{profile}[/cyan]")
        console.print(f"[bold]Région:[/bold] [cyan]{region}[/cyan]")
        
        # Exécuter AWS S3 LS pour montrer que ça fonctionne
        console.print("\n[bold]Liste des buckets S3:[/bold]")
        subprocess.run(["aws", "s3", "ls"], env=env)
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Erreur lors de la connexion à AWS: {e}[/red]")
