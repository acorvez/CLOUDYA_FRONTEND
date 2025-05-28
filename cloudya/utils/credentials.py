"""
Utilitaires de gestion des credentials pour les différents fournisseurs cloud
"""
import os
import yaml
import platform
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def load_credentials_config():
    """Charge la configuration des credentials"""
    config_dir = Path.home() / ".cloudya"
    credentials_file = config_dir / "credentials.yaml"
    
    # Créer le répertoire de configuration s'il n'existe pas
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer le fichier de credentials s'il n'existe pas
    if not credentials_file.exists():
        default_config = {
            "aws": {},
            "gcp": {},
            "azure": {},
            "openstack": {},
            "proxmox": {},
            "vmware": {},
            "nutanix": {}
        }
        with open(credentials_file, "w") as f:
            yaml.dump(default_config, f)
        return default_config
        
    # Charger la configuration existante
    try:
        with open(credentials_file, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Erreur lors du chargement des credentials: {e}[/red]")
        return {
            "aws": {},
            "gcp": {},
            "azure": {},
            "openstack": {},
            "proxmox": {},
            "vmware": {},
            "nutanix": {}
        }

def save_credentials_config(config):
    """Sauvegarde la configuration des credentials"""
    config_dir = Path.home() / ".cloudya"
    credentials_file = config_dir / "credentials.yaml"
    
    # Créer le répertoire de configuration s'il n'existe pas
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder la configuration
    try:
        with open(credentials_file, "w") as f:
            yaml.dump(config, f)
        return True
    except Exception as e:
        console.print(f"[red]Erreur lors de la sauvegarde des credentials: {e}[/red]")
        return False

def is_command_available(command):
    """Vérifie si une commande est disponible sur le système"""
    if platform.system() == "Windows":
        try:
            subprocess.run(["where", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        try:
            subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

def install_python_module(module_name, extra_modules=None):
    """Installe un module Python si nécessaire"""
    import importlib.util
    import sys
    
    modules_to_install = [module_name]
    if extra_modules:
        modules_to_install.extend(extra_modules)
    
    # Vérifier si le module est déjà installé
    try:
        if importlib.util.find_spec(module_name) is None:
            console.print(f"[yellow]Le module Python '{module_name}' n'est pas installé.[/yellow]")
            install = Confirm.ask("Voulez-vous l'installer?", default=True)
            
            if install:
                try:
                    console.print(f"[bold]Installation de {', '.join(modules_to_install)}...[/bold]")
                    subprocess.run([sys.executable, "-m", "pip", "install"] + modules_to_install, check=True)
                    console.print(f"[green]Modules installés avec succès![/green]")
                    return True
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Erreur lors de l'installation: {e}[/red]")
                    return False
            else:
                return False
        return True
    except Exception as e:
        console.print(f"[red]Erreur lors de la vérification du module: {e}[/red]")
        return False
