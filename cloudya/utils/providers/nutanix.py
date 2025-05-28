"""
Module de connexion à Nutanix Prism
"""
import os
import sys
import subprocess
import json
import requests
import urllib3
from rich.console import Console
from rich.prompt import Prompt
from ..credentials import load_credentials_config, save_credentials_config

console = Console()

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def connect(host=None, username=None, password=None, port=9440):
    """
    Se connecte à Nutanix Prism Central
    
    Args:
        host (str, optional): Hôte Nutanix Prism Central (ex: prism.example.com)
        username (str, optional): Nom d'utilisateur Nutanix
        password (str, optional): Mot de passe Nutanix
        port (int, optional): Port du serveur Nutanix Prism Central
    """
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si host pas spécifié, utiliser celui dans la config ou demander
    if not host:
        if "host" in credentials.get("nutanix", {}):
            host = credentials["nutanix"]["host"]
        else:
            host = Prompt.ask("Entrez l'hôte Nutanix Prism Central (ex: prism.example.com)", default="")
    
    if not port:
        if "port" in credentials.get("nutanix", {}):
            port = credentials["nutanix"]["port"]
        else:
            port = 9440
    
    if not username:
        if "username" in credentials.get("nutanix", {}):
            username = credentials["nutanix"]["username"]
        else:
            username = Prompt.ask("Entrez le nom d'utilisateur Nutanix", default="admin")
    
    if not password:
        password = Prompt.ask("Entrez le mot de passe Nutanix", password=True)
    
    # Sauvegarder les préférences (sauf le mot de passe)
    if "nutanix" not in credentials:
        credentials["nutanix"] = {}
    credentials["nutanix"]["host"] = host
    credentials["nutanix"]["port"] = port
    credentials["nutanix"]["username"] = username
    save_credentials_config(credentials)
    
    # Tester la connexion
    console.print(f"[bold]Connexion à Nutanix Prism Central sur[/bold] [cyan]{host}:{port}[/cyan]")
    
    try:
        # Construire l'URL de base
        base_url = f"https://{host}:{port}/api/nutanix/v3"
        
        # Headers pour l'API
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Se connecter à l'API
        session = requests.Session()
        session.auth = (username, password)
        session.headers.update(headers)
        session.verify = False
        
        # Tester la connexion en récupérant les clusters
        response = session.get(f"{base_url}/clusters/list", data=json.dumps({"kind": "cluster"}))
        
        if response.status_code == 200:
            # Afficher les informations de connexion
            console.print("[bold green]Connecté avec succès à Nutanix Prism Central![/bold green]")
            console.print(f"[bold]Hôte:[/bold] [cyan]{host}:{port}[/cyan]")
            console.print(f"[bold]Utilisateur:[/bold] [cyan]{username}[/cyan]")
            
            # Afficher les clusters disponibles
            clusters = response.json()
            console.print("\n[bold]Clusters disponibles:[/bold]")
            
            if "entities" in clusters:
                for cluster in clusters["entities"]:
                    console.print(f"- {cluster['spec']['name']} (UUID: {cluster['metadata']['uuid']})")
            else:
                console.print("Aucun cluster trouvé.")
            
            # Récupérer les VMs
            try:
                vm_response = session.post(f"{base_url}/vms/list", data=json.dumps({"kind": "vm"}))
                if vm_response.status_code == 200:
                    vms = vm_response.json()
                    console.print("\n[bold]Machines virtuelles disponibles:[/bold]")
                    
                    if "entities" in vms and len(vms["entities"]) > 0:
                        for vm in vms["entities"]:
                            vm_name = vm["spec"]["name"]
                            vm_state = vm["spec"]["resources"]["power_state"]
                            power_color = "green" if vm_state == "ON" else "red"
                            console.print(f"- {vm_name} ([{power_color}]{vm_state}[/{power_color}])")
                    else:
                        console.print("Aucune VM trouvée.")
            except Exception as e:
                console.print(f"[yellow]Impossible de récupérer les VMs: {e}[/yellow]")
            
        else:
            console.print(f"[red]Échec de la connexion à Nutanix Prism Central: {response.status_code} - {response.text}[/red]")
            
    except Exception as e:
        console.print(f"[red]Erreur lors de la connexion à Nutanix Prism Central: {e}[/red]")
