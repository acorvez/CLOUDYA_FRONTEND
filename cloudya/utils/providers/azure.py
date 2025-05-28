"""
Module de connexion à Microsoft Azure
"""
import os
import subprocess
import json
from rich.console import Console
from rich.prompt import Prompt
from ..credentials import load_credentials_config, save_credentials_config, is_command_available

console = Console()

def connect(subscription=None):
    """
    Se connecte à Microsoft Azure
    
    Args:
        subscription (str, optional): Abonnement Azure à utiliser
    """
    # Vérifier si la commande Azure CLI est disponible
    if not is_command_available("az"):
        console.print("[red]Azure CLI n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez Azure CLI via: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si subscription pas spécifiée, utiliser celle dans la config ou demander
    if not subscription:
        if "default_subscription" in credentials.get("azure", {}):
            subscription = credentials["azure"]["default_subscription"]
        else:
            # Se connecter d'abord à Azure
            console.print("[bold]Connexion à Azure...[/bold]")
            try:
                subprocess.run(["az", "login"], check=True)
                
                # Lister les abonnements Azure disponibles
                result = subprocess.run(
                    ["az", "account", "list", "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                subscriptions = json.loads(result.stdout)
                
                if subscriptions:
                    console.print("[bold]Abonnements Azure disponibles:[/bold]")
                    for i, s in enumerate(subscriptions, 1):
                        is_default = " (défaut)" if s.get("isDefault") else ""
                        console.print(f"{i}. {s['name']} - {s['id']}{is_default}")
                    sub_idx = Prompt.ask("Sélectionnez un abonnement (numéro)", default="1")
                    try:
                        subscription = subscriptions[int(sub_idx) - 1]["id"]
                    except (ValueError, IndexError):
                        subscription = Prompt.ask("Entrez l'ID de l'abonnement Azure", default="")
                else:
                    subscription = Prompt.ask("Entrez l'ID de l'abonnement Azure", default="")
            except subprocess.CalledProcessError:
                console.print("[red]Erreur lors de la connexion à Azure.[/red]")
                return
    
    # Sauvegarder les préférences
    if "azure" not in credentials:
        credentials["azure"] = {}
    if subscription:
        credentials["azure"]["default_subscription"] = subscription
    save_credentials_config(credentials)
    
    # Définir l'abonnement par défaut
    if subscription:
        console.print(f"[bold]Configuration de l'abonnement par défaut:[/bold] [cyan]{subscription}[/cyan]")
        try:
            subprocess.run(["az", "account", "set", "--subscription", subscription], check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors de la définition de l'abonnement: {e}[/red]")
            return
    
    # Afficher les informations de connexion
    console.print("[bold green]Connecté avec succès à Microsoft Azure![/bold green]")
    console.print(f"[bold]Abonnement:[/bold] [cyan]{subscription}[/cyan]")
    
    # Exécuter az account show pour montrer que ça fonctionne
    console.print("\n[bold]Informations sur le compte Azure:[/bold]")
    subprocess.run(["az", "account", "show", "--output", "yaml"])
