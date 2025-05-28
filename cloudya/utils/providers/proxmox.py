"""
Module de connexion à Proxmox VE
"""
import os
import sys
import subprocess
from rich.console import Console
from rich.prompt import Prompt, Confirm
from ..credentials import load_credentials_config, save_credentials_config, install_python_module

console = Console()

def connect(host=None, port=8006, username=None, token_name=None, token_value=None):
    """
    Se connecte à Proxmox VE
    
    Args:
        host (str, optional): Hôte Proxmox (ex: proxmox.example.com)
        port (int, optional): Port de l'API Proxmox
        username (str, optional): Nom d'utilisateur Proxmox (ex: root@pam)
        token_name (str, optional): Nom du token d'API Proxmox
        token_value (str, optional): Valeur du token d'API Proxmox
    """
    # Vérifier si les modules Python nécessaires sont disponibles
    if not install_python_module("proxmoxer", ["requests"]):
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si host pas spécifié, utiliser celui dans la config ou demander
    if not host:
        if "host" in credentials.get("proxmox", {}):
            host = credentials["proxmox"]["host"]
        else:
            host = Prompt.ask("Entrez l'hôte Proxmox (ex: proxmox.example.com)", default="")
    
    if not port:
        if "port" in credentials.get("proxmox", {}):
            port = credentials["proxmox"]["port"]
        else:
            port = 8006
    
    if not username:
        if "username" in credentials.get("proxmox", {}):
            username = credentials["proxmox"]["username"]
        else:
            username = Prompt.ask("Entrez le nom d'utilisateur Proxmox (ex: root@pam)", default="root@pam")
    
    if not token_name:
        if "token_name" in credentials.get("proxmox", {}):
            token_name = credentials["proxmox"]["token_name"]
        else:
            use_token = Confirm.ask("Voulez-vous utiliser un token API au lieu d'un mot de passe?", default=True)
            if use_token:
                token_name = Prompt.ask("Entrez le nom du token API", default="")
            else:
                token_name = ""
    
    if token_name and not token_value:
        if "token_value" in credentials.get("proxmox", {}):
            token_value = credentials["proxmox"]["token_value"]
        else:
            token_value = Prompt.ask("Entrez la valeur du token API", password=True)
    
    # Si on n'utilise pas de token, demander le mot de passe
    password = None
    if not token_name:
        password = Prompt.ask("Entrez le mot de passe Proxmox", password=True)
    
    # Sauvegarder les préférences (sauf le mot de passe)
    if "proxmox" not in credentials:
        credentials["proxmox"] = {}
    credentials["proxmox"]["host"] = host
    credentials["proxmox"]["port"] = port
    credentials["proxmox"]["username"] = username
    if token_name:
        credentials["proxmox"]["token_name"] = token_name
        credentials["proxmox"]["token_value"] = token_value
    save_credentials_config(credentials)
    
    # Tester la connexion
    console.print(f"[bold]Connexion à Proxmox VE sur[/bold] [cyan]{host}:{port}[/cyan]")
    
    try:
        from proxmoxer import ProxmoxAPI
        
        if token_name and token_value:
            proxmox = ProxmoxAPI(
                host=host,
                port=port,
                user=username,
                token_name=token_name,
                token_value=token_value,
                verify_ssl=False
            )
        else:
            proxmox = ProxmoxAPI(
                host=host,
                port=port,
                user=username,
                password=password,
                verify_ssl=False
            )
        
        # Tester la connexion en récupérant la version
        version = proxmox.version.get()
        
        # Afficher les informations de connexion
        console.print("[bold green]Connecté avec succès à Proxmox VE![/bold green]")
        console.print(f"[bold]Hôte:[/bold] [cyan]{host}:{port}[/cyan]")
        console.print(f"[bold]Utilisateur:[/bold] [cyan]{username}[/cyan]")
        console.print(f"[bold]Version:[/bold] [cyan]{version.get('version')}[/cyan]")
        
        # Afficher les nœuds disponibles
        console.print("\n[bold]Nœuds disponibles:[/bold]")
        for node in proxmox.nodes.get():
            status = "[green]en ligne[/green]" if node["status"] == "online" else "[red]hors ligne[/red]"
            console.print(f"- {node['node']} ({status})")
        
    except ImportError:
        console.print("[red]Erreur: le module proxmoxer n'est pas disponible.[/red]")
    except Exception as e:
        console.print(f"[red]Erreur lors de la connexion à Proxmox VE: {e}[/red]")
