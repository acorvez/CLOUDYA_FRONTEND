#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from typing import Optional, List
import os
import sys
import time
import json
import yaml
from pathlib import Path

# Importer les modules Cloudya pour le déploiement d'infrastructure
from cloudya.utils.terraform import (
    get_terraform_path,
    get_template_info,
    prepare_deployment,
    run_terraform,
    list_deployments
)

# Importer les modules Cloudya pour le déploiement d'applications
from cloudya.utils.ansible_apps import get_available_apps, get_app_info
from cloudya.utils.ansible_inventory import prepare_inventory
from cloudya.utils.ansible_deployment import (
    prepare_app_deployment,
    deploy_ansible_app,
    deploy_docker_app
)

# Importer les modules pour la connexion aux providers
from cloudya.utils.providers import (
    aws, gcp, azure, openstack, proxmox, vmware, nutanix
)

app = typer.Typer(help="Déployer des stacks complètes (infrastructure + applications)")
console = Console()

@app.command("list")
def list_stacks():
    """
    Liste les stacks préconfigurées disponibles
    """
    # Cette fonction pourrait lister des "stacks" préconfigurées
    # qui combinent un template d'infrastructure et une ou plusieurs applications
    
    # Pour l'instant, simulons quelques stacks prédéfinies
    stacks = [
        {
            "name": "wordpress-aws",
            "description": "WordPress sur AWS EC2",
            "infrastructure": {
                "template": "aws/ec2",
                "params": {
                    "instance_type": "t2.micro",
                    "region": "us-east-1"
                }
            },
            "applications": [
                {
                    "name": "WordPress",
                    "params": {
                        "domain": "wordpress.example.com"
                    }
                }
            ]
        },
        {
            "name": "lamp-gcp",
            "description": "Stack LAMP sur Google Cloud",
            "infrastructure": {
                "template": "gcp/vm",
                "params": {
                    "machine_type": "e2-medium",
                    "region": "us-central1"
                }
            },
            "applications": [
                {
                    "name": "LAMP",
                    "params": {
                        "php_version": "8.1"
                    }
                }
            ]
        },
        {
            "name": "nextcloud-azure",
            "description": "Nextcloud sur Azure VM",
            "infrastructure": {
                "template": "azure/vm",
                "params": {
                    "vm_size": "Standard_B2s",
                    "region": "eastus"
                }
            },
            "applications": [
                {
                    "name": "Nextcloud",
                    "params": {
                        "domain": "cloud.example.com"
                    }
                }
            ]
        }
    ]
    
    # Afficher les stacks disponibles
    table = Table(title="Stacks préconfigurées")
    table.add_column("Nom", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Infrastructure", style="green")
    table.add_column("Applications", style="yellow")
    
    for stack in stacks:
        infra = f"{stack['infrastructure']['template']}"
        apps = ", ".join([app['name'] for app in stack['applications']])
        
        table.add_row(
            stack['name'],
            stack['description'],
            infra,
            apps
        )
    
    console.print(table)
    
    # Information supplémentaire
    console.print("\n[bold]Note:[/bold] Vous pouvez également créer une stack personnalisée avec la commande [cyan]cloudya stack deploy[/cyan].")

@app.command("deploy")
def deploy_stack(
    template: str = typer.Option(..., "--template", "-t", help="Template d'infrastructure (ex: aws/ec2)"),
    app_name: str = typer.Option(..., "--app", "-a", help="Nom de l'application à installer"),
    infra_params: str = typer.Option(None, "--infra-params", "-i", help="Paramètres d'infrastructure au format key1=value1,key2=value2"),
    app_params: str = typer.Option(None, "--app-params", "-p", help="Paramètres d'application au format key1=value1,key2=value2"),
    ssh_user: str = typer.Option(None, "--ssh-user", "-u", help="Utilisateur SSH pour la connexion"),
    ssh_key: str = typer.Option(None, "--ssh-key", "-k", help="Chemin vers la clé SSH privée"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Approuver automatiquement les étapes")
):
    """
    Déploie une stack complète (infrastructure + application)
    """
    # Étape 1: Valider le template d'infrastructure
    template_parts = template.split('/')
    if len(template_parts) < 2:
        console.print(f"[red]Format de template invalide: {template}[/red]")
        console.print("Le format attendu est provider/template, par exemple: aws/ec2")
        return
    
    provider = template_parts[0].lower()
    
    # Vérifier le provider
    valid_providers = ["aws", "gcp", "azure", "openstack", "proxmox", "vmware", "nutanix"]
    if provider not in valid_providers:
        console.print(f"[red]Provider non supporté: {provider}[/red]")
        console.print(f"Providers supportés: {', '.join(valid_providers)}")
        return
    
    # Étape 2: Valider l'application
    app_info = get_app_info(app_name)
    if not app_info:
        console.print(f"[red]Application '{app_name}' non trouvée.[/red]")
        console.print("Utilisez 'cloudya app list' pour voir les applications disponibles.")
        return
    
    # Vérifier si la plateforme est supportée
    if provider not in app_info.get("platforms", []):
        console.print(f"[red]La plateforme '{provider}' n'est pas supportée pour l'application '{app_name}'.[/red]")
        console.print(f"Plateformes supportées: {', '.join(app_info.get('platforms', []))}")
        return
    
    # Étape 3: Parser les paramètres
    infra_param_dict = {}
    if infra_params:
        for pair in infra_params.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                infra_param_dict[key.strip()] = value.strip()
    
    app_param_dict = {}
    if app_params:
        for pair in app_params.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                app_param_dict[key.strip()] = value.strip()
    
    # Étape 4: Afficher le résumé et demander confirmation
    console.print("\n[bold]Résumé du déploiement:[/bold]")
    console.print(f"[bold]Infrastructure:[/bold] [cyan]{template}[/cyan]")
    if infra_param_dict:
        console.print("[bold]Paramètres d'infrastructure:[/bold]")
        for key, value in infra_param_dict.items():
            console.print(f" - [green]{key}:[/green] {value}")
    
    console.print(f"\n[bold]Application:[/bold] [cyan]{app_name}[/cyan]")
    if app_param_dict:
        console.print("[bold]Paramètres d'application:[/bold]")
        for key, value in app_param_dict.items():
            if "password" in key.lower():
                console.print(f" - [green]{key}:[/green] ********")
            else:
                console.print(f" - [green]{key}:[/green] {value}")
    
    # Demander confirmation si auto_approve n'est pas activé
    if not auto_approve:
        proceed = Confirm.ask("Voulez-vous procéder au déploiement de la stack?", default=True)
        if not proceed:
            console.print("[yellow]Déploiement annulé.[/yellow]")
            return
    
    # Étape 5: Connecter au provider
    console.print(f"\n[bold]Connexion au provider: [cyan]{provider.upper()}[/cyan][/bold]")
    
    try:
        # Appeler la fonction de connexion correspondante
        if provider == "aws":
            aws.connect()
        elif provider == "gcp":
            gcp.connect()
        elif provider == "azure":
            azure.connect()
        elif provider == "openstack":
            openstack.connect()
        elif provider == "proxmox":
            proxmox.connect()
        elif provider == "vmware":
            vmware.connect()
        elif provider == "nutanix":
            nutanix.connect()
    except Exception as e:
        console.print(f"[red]Erreur lors de la connexion au provider {provider}: {e}[/red]")
        if not Confirm.ask("Continuer quand même avec le déploiement?"):
            return
    
    # Étape 6: Déployer l'infrastructure
    console.print(f"\n[bold]Déploiement de l'infrastructure: [cyan]{template}[/cyan][/bold]")
    
    try:
        # Récupérer les informations du template
        template_info = get_template_info(template)
        if not template_info:
            console.print(f"[yellow]Template '{template}' non trouvé dans le répertoire des templates.[/yellow]")
            simulate = Confirm.ask("Voulez-vous effectuer une simulation de déploiement?")
            if not simulate:
                return
            
            # Utiliser un template factice pour la démonstration
            template_info = {
                "name": template.split('/')[-1].upper(),
                "provider": provider,
                "description": f"Template {template} simulé",
                "parameters": [
                    {"name": "region", "description": "Région", "default": "us-east-1", "required": True},
                    {"name": "instance_type", "description": "Type d'instance", "default": "t2.micro", "required": False}
                ]
            }
        
        # Vérifier les paramètres requis
        missing_params = []
        for param in template_info.get("parameters", []):
            if param.get("required", False) and param["name"] not in infra_param_dict:
                # Si le paramètre a une valeur par défaut, l'utiliser
                if "default" in param:
                    infra_param_dict[param["name"]] = param["default"]
                else:
                    missing_params.append(param)
        
        # Demander les paramètres manquants
        if missing_params:
            console.print("[yellow]Paramètres d'infrastructure requis manquants:[/yellow]")
            for param in missing_params:
                value = Prompt.ask(
                    f"{param['description']} ({param['name']})",
                    default="" if "default" not in param else str(param["default"])
                )
                infra_param_dict[param["name"]] = value
        
        # Préparer le déploiement
        deployment_dir = prepare_deployment(template, infra_param_dict)
        
        if not deployment_dir:
            console.print("[red]Erreur lors de la préparation du déploiement d'infrastructure.[/red]")
            return
        
        # Exécuter le déploiement Terraform
        success = run_terraform(deployment_dir, auto_approve)
        
        if not success:
            console.print("[bold red]Erreur lors du déploiement de l'infrastructure.[/bold red]")
            return
        
        console.print("[bold green]Déploiement de l'infrastructure réussi ![/bold green]")
        
        # Récupérer l'ID du déploiement
        metadata_file = os.path.join(deployment_dir, "metadata.json")
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        infra_deployment_id = metadata.get("id")
        console.print(f"[bold]ID du déploiement d'infrastructure:[/bold] {infra_deployment_id}")
        
    except Exception as e:
        console.print(f"[red]Erreur lors du déploiement de l'infrastructure: {e}[/red]")
        return
    
    # Étape 7: Attendre que l'infrastructure soit prête
    console.print("\n[bold]Attente de la disponibilité de l'infrastructure...[/bold]")
    
    with console.status("[bold green]Attente...[/bold green]"):
        # Dans une vraie implémentation, on pourrait vérifier l'état de l'infrastructure
        # Pour l'instant, on attend juste quelques secondes
        time.sleep(5)
    
    # Étape 8: Récupérer les informations sur l'instance déployée
    console.print("\n[bold]Récupération des informations sur l'instance déployée...[/bold]")
    
    # Importer ici pour éviter les imports circulaires
    from cloudya.utils.ansible_instances import get_terraform_instances
    
    # Attendre quelques secondes pour que les instances soient enregistrées
    time.sleep(2)
    
    # Récupérer les instances
    instances = get_terraform_instances()
    
    # Filtrer pour ne garder que les instances du déploiement actuel
    deployment_instances = [inst for inst in instances if inst.get("deployment_id") == infra_deployment_id]
    
    if not deployment_instances:
        console.print("[yellow]Aucune instance trouvée pour le déploiement actuel.[/yellow]")
        console.print("L'installation de l'application ne peut pas continuer.")
        return
    
    # Utiliser la première instance
    instance = deployment_instances[0]
    console.print(f"[bold]Instance détectée:[/bold] {instance['name']} ({instance['ip']})")
    
    # Étape 9: Vérification des paramètres de l'application
    console.print(f"\n[bold]Préparation de l'installation de {app_name}...[/bold]")
    
    # Vérifier les paramètres requis
    missing_params = []
    if "parameters" in app_info:
        for param in app_info["parameters"]:
            if param.get("required", False) and param["name"] not in app_param_dict:
                # Si le paramètre a une valeur par défaut, l'utiliser
                if "default" in param and param["default"]:
                    app_param_dict[param["name"]] = param["default"]
                else:
                    missing_params.append(param["name"])
    
    if missing_params:
        console.print("[yellow]Paramètres d'application requis manquants:[/yellow]")
        for param_name in missing_params:
            # Trouver la description du paramètre
            param_info = next((p for p in app_info["parameters"] if p["name"] == param_name), {})
            description = param_info.get("description", param_name)
            
            value = Prompt.ask(f"{description}", password="password" in param_name.lower())
            app_param_dict[param_name] = value
    
    # Étape 10: Préparer le déploiement de l'application
    app_deployment = prepare_app_deployment(app_name, provider, app_param_dict, instance)
    
    if not app_deployment:
        console.print("[red]Erreur lors de la préparation du déploiement de l'application.[/red]")
        return
    
    # Étape 11: Préparer l'inventaire Ansible
    console.print(f"\n[bold]Préparation de l'inventaire Ansible...[/bold]")
    inventory_file = prepare_inventory(instance, ssh_user, ssh_key)
    
    # Étape 12: Déployer l'application
    console.print(f"\n[bold]Déploiement de l'application {app_name}...[/bold]")
    
    app_type = app_info.get("type", "ansible")
    
    if app_type == "docker":
        success = deploy_docker_app(app_deployment["dir"], inventory_file)
    else:  # ansible par défaut
        success = deploy_ansible_app(app_deployment["dir"], inventory_file)
    
    if success:
        console.print(f"[bold green]Installation de '{app_name}' réussie ![/bold green]")
        
        # Afficher les informations de déploiement
        console.print(f"[bold]ID du déploiement d'application:[/bold] {app_deployment['id']}")
        
        # Afficher un message sur la façon d'accéder à l'application
        if "domain" in app_param_dict:
            console.print(f"\n[bold]Accès à l'application:[/bold]")
            console.print(f"http://{app_param_dict['domain']} (configurez votre DNS pour pointer vers {instance['ip']})")
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
    
    # Étape 13: Résumé final
    console.print("\n[bold]Résumé du déploiement de la stack:[/bold]")
    console.print(f"[bold]Infrastructure:[/bold] {template} (ID: {infra_deployment_id})")
    console.print(f"[bold]Application:[/bold] {app_name} (ID: {app_deployment['id']})")
    console.print(f"[bold]Instance:[/bold] {instance['name']} ({instance['ip']})")
    
    console.print("\n[bold green]Déploiement de la stack terminé avec succès ![/bold green]")

if __name__ == "__main__":
    app()
