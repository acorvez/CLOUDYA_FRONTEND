"""
Module de connexion à VMware vSphere
"""
import os
import sys
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from ..credentials import load_credentials_config, save_credentials_config, install_python_module

console = Console()

def connect(host=None, username=None, password=None, port=443):
    """
    Se connecte à VMware vSphere (vCenter ou ESXi)
    
    Args:
        host (str, optional): Hôte vCenter ou ESXi (ex: vcenter.example.com)
        username (str, optional): Nom d'utilisateur VMware
        password (str, optional): Mot de passe VMware
        port (int, optional): Port du serveur vCenter ou ESXi
    """
    # Vérifier si les modules Python nécessaires sont disponibles
    if not install_python_module("pyVmomi"):
        return
    
    # Charger les credentials
    credentials = load_credentials_config()
    
    # Si host pas spécifié, utiliser celui dans la config ou demander
    if not host:
        if "host" in credentials.get("vmware", {}):
            host = credentials["vmware"]["host"]
        else:
            host = Prompt.ask("Entrez l'hôte vCenter ou ESXi (ex: vcenter.example.com)", default="")
    
    if not port:
        if "port" in credentials.get("vmware", {}):
            port = credentials["vmware"]["port"]
        else:
            port = 443
    
    if not username:
        if "username" in credentials.get("vmware", {}):
            username = credentials["vmware"]["username"]
        else:
            username = Prompt.ask("Entrez le nom d'utilisateur VMware", default="administrator@vsphere.local")
    
    if not password:
        password = Prompt.ask("Entrez le mot de passe VMware", password=True)
    
    # Sauvegarder les préférences (sauf le mot de passe)
    if "vmware" not in credentials:
        credentials["vmware"] = {}
    credentials["vmware"]["host"] = host
    credentials["vmware"]["port"] = port
    credentials["vmware"]["username"] = username
    save_credentials_config(credentials)
    
    # Tester la connexion
    console.print(f"[bold]Connexion à VMware vSphere sur[/bold] [cyan]{host}:{port}[/cyan]")
    
    try:
        from pyVim.connect import SmartConnect, Disconnect
        import ssl
        
        # Ignorer les erreurs de certificat SSL
        context = ssl._create_unverified_context()
        
        # Se connecter à vCenter/ESXi
        service_instance = SmartConnect(
            host=host, 
            user=username, 
            pwd=password, 
            port=port,
            sslContext=context
        )
        
        if service_instance:
            # Afficher les informations de connexion
            console.print("[bold green]Connecté avec succès à VMware vSphere![/bold green]")
            console.print(f"[bold]Hôte:[/bold] [cyan]{host}:{port}[/cyan]")
            console.print(f"[bold]Utilisateur:[/bold] [cyan]{username}[/cyan]")
            
            # Récupérer la version
            about = service_instance.content.about
            console.print(f"[bold]Produit:[/bold] {about.fullName}")
            
            # Récupérer les VM
            from pyVmomi import vim
            
            content = service_instance.RetrieveContent()
            container = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True
            )
            
            console.print("\n[bold]Machines virtuelles disponibles:[/bold]")
            vm_list = container.view
            for vm in vm_list:
                power_state = "sous tension" if vm.runtime.powerState == "poweredOn" else "hors tension"
                power_color = "green" if power_state == "sous tension" else "red"
                console.print(f"- {vm.name} ([{power_color}]{power_state}[/{power_color}])")
            
            # Fermer la connexion
            Disconnect(service_instance)
            
        else:
            console.print("[red]Échec de la connexion à VMware vSphere.[/red]")
            
    except ImportError:
        console.print("[red]Erreur: le module pyVmomi n'est pas disponible.[/red]")
    except Exception as e:
        console.print(f"[red]Erreur lors de la connexion à VMware vSphere: {e}[/red]")
