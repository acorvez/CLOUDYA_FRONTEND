#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import os
import sys
from pathlib import Path

# Importer les modules Cloudya
from cloudya.utils import ansible
from cloudya.utils.ansible_apps import get_available_apps, get_app_info
from cloudya.utils.ansible_instances import get_terraform_instances, select_instance
from cloudya.utils.ansible_inventory import prepare_inventory
from cloudya.utils.ansible_deployment import (
    prepare_app_deployment,
    deploy_ansible_app,
    deploy_docker_app,
    get_app_deployment,
    list_app_deployments,
    uninstall_app
)

app = typer.Typer(help="Gérer les applications avec Ansible ou Docker")
console = Console()

@app.command("list")
def list_apps():
    """
    Liste les applications disponibles
    """
    apps = get_available_apps()
    
    if not apps:
        console.print("[yellow]Aucune application trouvée.[/yellow]")
        return
    
    table = Table(title="Applications disponibles")
    table.add_column("Nom", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Plateformes", style="yellow")
    table.add_column("Description", style="white")
    
    for app_info in apps:
        platforms = ", ".join(app_info.get("platforms", []))
        table.add_row(
            app_info["name"], 
            app_info.get("type", "ansible"), 
            platforms,
            app_info.get("description", "")
        )
    
    console.print(table)

@app.command("show")
def show_app(app_name: str):
    """
    Affiche les détails d'une application
    """
    app_info = get_app_info(app_name)
    
    if not app_info:
        console.print(f"[red]Application '{app_name}' non trouvée.[/red]")
        return
    
    console.print(f"[bold cyan]Application:[/bold cyan] {app_info['name']}")
    console.print(f"[bold green]Type:[/bold green] {app_info.get('type', 'ansible')}")
    console.print(f"[bold yellow]Plateformes:[/bold yellow] {', '.join(app_info.get('platforms', []))}")
    console.print(f"[bold white]Description:[/bold white] {app_info.get('description', '')}")
    
    if app_info.get("parameters"):
        table = Table(title="Paramètres")
        table.add_column("Nom", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Default", style="green")
        table.add_column("Requis", style="yellow")
        
        for param in app_info["parameters"]:
            table.add_row(
                param["name"],
                param.get("description", ""),
                str(param.get("default", "")),
                "✓" if param.get("required", False) else "✗"
            )
        
        console.print(table)

@app.command("install")
def install_app(
    app_name: str,
    platform: str = typer.Option(..., "--platform", "-p", help="Plateforme cible (aws, gcp, azure, vmware, proxmox, nutanix, openstack)"),
    params: str = typer.Option(None, "--params", help="Paramètres au format key1=value1,key2=value2"),
    ssh_user: str = typer.Option(None, "--ssh-user", "-u", help="Utilisateur SSH pour la connexion"),
    ssh_key: str = typer.Option(None, "--ssh-key", "-k", help="Chemin vers la clé SSH privée")
):
    """
    Installe une application sur une infrastructure
    """
    # Vérifier si l'application existe
    app_info = get_app_info(app_name)
    if not app_info:
        console.print(f"[red]Application '{app_name}' non trouvée.[/red]")
        return
    
    # Vérifier si la plateforme est supportée
    if platform not in app_info.get("platforms", []):
        console.print(f"[red]La plateforme '{platform}' n'est pas supportée pour l'application '{app_name}'.[/red]")
        console.print(f"Plateformes supportées: {', '.join(app_info.get('platforms', []))}")
        return
    
    # Parser les paramètres
    param_dict = {}
    if params:
        param_pairs = params.split(",")
        for pair in param_pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                param_dict[key.strip()] = value.strip()
    
    # Vérifier les paramètres requis
    missing_params = []
    if "parameters" in app_info:
        for param in app_info["parameters"]:
            if param.get("required", False) and param["name"] not in param_dict:
                # Si le paramètre a une valeur par défaut, l'utiliser
                if "default" in param and param["default"]:
                    param_dict[param["name"]] = param["default"]
                else:
                    missing_params.append(param["name"])
    
    if missing_params:
        console.print("[red]Paramètres requis manquants:[/red]")
        for param in missing_params:
            console.print(f"- {param}")
        return
    
    # Déterminer la cible (instance)
    console.print(f"[bold]Sélection d'une instance pour déployer '{app_name}'...[/bold]")
    instance = ansible.determine_target(platform)
    
    if not instance:
        console.print("[red]Impossible de déterminer une cible de déploiement.[/red]")
        console.print("Déployez d'abord une infrastructure avec la commande 'cloudya deploy'.")
        return
    
    # Préparer le déploiement
    console.print(f"[bold]Préparation du déploiement de '{app_name}' sur '{instance['name']}'...[/bold]")
    deployment = prepare_app_deployment(app_name, platform, param_dict, instance)
    
    if not deployment:
        console.print("[red]Erreur lors de la préparation du déploiement.[/red]")
        return
    
    # Préparer l'inventaire Ansible
    console.print(f"[bold]Préparation de l'inventaire Ansible...[/bold]")
    inventory_file = prepare_inventory(instance, ssh_user, ssh_key)
    
    # Exécuter le déploiement
    console.print(f"[bold]Déploiement de '{app_name}' en cours...[/bold]")
    
    app_type = app_info.get("type", "ansible")
    
    if app_type == "docker":
        success = deploy_docker_app(deployment["dir"], inventory_file)
    else:  # ansible par défaut
        success = deploy_ansible_app(deployment["dir"], inventory_file)
    
    if success:
        console.print(f"[bold green]Installation de '{app_name}' réussie ![/bold green]")
        
        # Afficher les informations de déploiement
        console.print(f"[bold]ID du déploiement:[/bold] {deployment['id']}")
        console.print(f"[bold]Application:[/bold] {app_info['name']}")
        console.print(f"[bold]Instance:[/bold] {instance['name']} ({instance['ip']})")
        
        # Afficher un message sur la façon d'accéder à l'application
        if "domain" in param_dict:
            console.print(f"\n[bold]Accès à l'application:[/bold]")
            console.print(f"http://{param_dict['domain']} (configurez votre DNS pour pointer vers {instance['ip']})")
        else:
            console.print(f"\n[bold]Accès à l'application:[/bold]")
            console.print(f"http://{instance['ip']}")
    else:
        console.print(f"[bold red]Erreur lors de l'installation de '{app_name}'.[/bold red]")
        console.print("Consultez les logs pour plus de détails.")
    
    # Nettoyer le fichier d'inventaire
    try:
        os.unlink(inventory_file)
    except:
        pass

@app.command("uninstall")
def uninstall_app_command(
    app_id: str = typer.Option(..., "--id", help="ID de l'application à désinstaller")
):
    """
    Désinstalle une application
    """
    app_deployment = get_app_deployment(app_id)
    
    if not app_deployment:
        console.print(f"[red]Déploiement d'application '{app_id}' non trouvé.[/red]")
        return
    
    from rich.prompt import Confirm
    confirm = Confirm.ask(f"Êtes-vous sûr de vouloir désinstaller l'application '{app_deployment.get('name', app_id)}' ?")
    if not confirm:
        console.print("Opération annulée.")
        return
    
    if uninstall_app(app_id):
        console.print(f"[bold green]Désinstallation de l'application '{app_id}' réussie ![/bold green]")
    else:
        console.print(f"[bold red]Erreur lors de la désinstallation de l'application '{app_id}'.[/bold red]")
        console.print("Consultez les logs pour plus de détails.")

@app.command("status")
def app_status(
    app_id: Optional[str] = typer.Option(None, "--id", help="ID de l'application à vérifier (optionnel)")
):
    """
    Affiche le statut des applications installées
    """
    if app_id:
        # Vérifier une application spécifique
        app_info = get_app_deployment(app_id)
        if not app_info:
            console.print(f"[red]Déploiement d'application '{app_id}' non trouvé.[/red]")
            return
        
        console.print(f"[bold cyan]Application:[/bold cyan] {app_info.get('name', 'Inconnue')}")
        console.print(f"[bold green]Plateforme:[/bold green] {app_info.get('platform', 'Inconnue')}")
        console.print(f"[bold yellow]Statut:[/bold yellow] {app_info.get('status', 'Inconnu')}")
        console.print(f"[bold white]Date d'installation:[/bold white] {app_info.get('deployed_at', app_info.get('created_at', 'Inconnue'))}")
        
        # Informations sur l'instance
        instance = app_info.get("instance", {})
        console.print(f"\n[bold]Instance:[/bold]")
        console.print(f"  [cyan]Nom:[/cyan] {instance.get('name', 'Inconnue')}")
        console.print(f"  [cyan]IP:[/cyan] {instance.get('ip', 'Inconnue')}")
        
        # Accès à l'application
        params = app_info.get("params", {})
        if "domain" in params:
            console.print(f"\n[bold]Accès à l'application:[/bold]")
            console.print(f"http://{params['domain']} (configurez votre DNS pour pointer vers {instance.get('ip', '')})")
        else:
            console.print(f"\n[bold]Accès à l'application:[/bold]")
            console.print(f"http://{instance.get('ip', '')}")
        
        # Paramètres
        if params:
            console.print("\n[bold]Configuration:[/bold]")
            for key, value in params.items():
                # Ne pas afficher les mots de passe
                if "password" in key.lower():
                    value = "********"
                console.print(f"  [cyan]{key}:[/cyan] {value}")
    else:
        # Lister toutes les applications
        apps = list_app_deployments()
        
        if not apps:
            console.print("[yellow]Aucune application installée trouvée.[/yellow]")
            return
        
        table = Table(title="Applications installées")
        table.add_column("ID", style="cyan")
        table.add_column("Nom", style="green")
        table.add_column("Plateforme", style="yellow")
        table.add_column("Instance", style="blue")
        table.add_column("Statut", style="white")
        table.add_column("Date d'installation", style="white")
        
        for app_info in apps:
            instance = app_info.get("instance", {})
            deployed_at = app_info.get("deployed_at", app_info.get("created_at", ""))
            if len(deployed_at) > 19:  # Tronquer la date ISO
                deployed_at = deployed_at[:19].replace("T", " ")
                
            table.add_row(
                app_info["id"],
                app_info.get("name", "Inconnue"),
                app_info.get("platform", "Inconnue"),
                f"{instance.get('name', '')} ({instance.get('ip', '')})",
                app_info.get("status", "Inconnu"),
                deployed_at
            )
        
        console.print(table)

if __name__ == "__main__":
    app()
