#!/usr/bin/env python3
import typer
import os
import sys
import yaml
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Importer les fonctions de connexion aux providers
from cloudya.utils.providers import aws, gcp, azure, openstack, proxmox, vmware, nutanix
# Importer les fonctions pour Terraform
from cloudya.utils.terraform import (
    get_terraform_path, 
    get_templates_dir, 
    get_available_templates,
    get_template_info,
    prepare_deployment,
    run_terraform
)

app = typer.Typer(help="Déployer des infrastructures avec Terraform")
console = Console()

@app.command("list")
def list_templates():
    """
    Liste les templates Terraform disponibles
    """
    # Récupérer les templates disponibles
    templates = get_available_templates()
    
    if not templates:
        console.print("[yellow]Aucun template disponible.[/yellow]")
        console.print("Vous pouvez créer des templates dans le répertoire:")
        console.print(f"[cyan]{get_templates_dir()}/terraform/[/cyan]")
        
        # Simuler des templates si aucun n'est trouvé
        console.print("\n[bold]Templates simulés (pour démonstration):[/bold]")
        console.print(" - [cyan]aws/vpc[/cyan] (VPC AWS avec des sous-réseaux publics et privés)")
        console.print(" - [cyan]aws/eks[/cyan] (Cluster Kubernetes AWS)")
        console.print(" - [cyan]gcp/vpc[/cyan] (VPC Google Cloud Platform)")
        return
    
    console.print("[bold]Templates disponibles:[/bold]")
    
    # Organiser les templates par provider
    templates_by_provider = {}
    for template in templates:
        provider = template.get("provider", "unknown")
        if provider not in templates_by_provider:
            templates_by_provider[provider] = []
        templates_by_provider[provider].append(template)
    
    # Afficher les templates par provider
    for provider, provider_templates in templates_by_provider.items():
        console.print(f"\n[bold]{provider.upper()}:[/bold]")
        for template in provider_templates:
            console.print(f" - [cyan]{template['path']}[/cyan] ({template['description']})")

@app.command("template")
def deploy_template(
    template_name: str = typer.Argument(..., help="Nom du template à déployer"),
    params: str = typer.Option(None, "--params", "-p", help="Paramètres au format key1=value1,key2=value2"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Approuver automatiquement le plan Terraform")
):
    """
    Déploie un template Terraform avec des paramètres
    """
    # Analyser le nom du template pour déterminer le provider
    parts = template_name.split('/')
    if len(parts) < 2:
        console.print(f"[red]Format de template invalide: {template_name}[/red]")
        console.print("Le format attendu est provider/template, par exemple: aws/vpc")
        return
    
    provider = parts[0].lower()
    
    # Vérifier le provider
    valid_providers = ["aws", "gcp", "azure", "openstack", "proxmox", "vmware", "nutanix"]
    if provider not in valid_providers:
        console.print(f"[red]Provider non supporté: {provider}[/red]")
        console.print(f"Providers supportés: {', '.join(valid_providers)}")
        return
    
    # Récupérer les informations sur le template
    template_info = get_template_info(template_name)
    
    if not template_info:
        # Si le template n'existe pas, simuler avec un template fictif
        console.print(f"[yellow]Template '{template_name}' non trouvé dans le répertoire des templates.[/yellow]")
        simulate = Confirm.ask("Voulez-vous effectuer une simulation de déploiement?")
        if not simulate:
            return
        
        template_info = {
            "name": template_name.split('/')[-1].upper(),
            "provider": provider,
            "description": f"Template {template_name} simulé",
            "parameters": [
                {"name": "region", "description": "Région", "default": "us-east-1", "required": True},
                {"name": "instance_type", "description": "Type d'instance", "default": "t2.micro", "required": False}
            ]
        }
    
    # Analyser les paramètres
    params_dict = {}
    if params:
        for pair in params.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                params_dict[key.strip()] = value.strip()
    
    # Vérifier les paramètres requis
    missing_params = []
    for param in template_info.get("parameters", []):
        if param.get("required", False) and param["name"] not in params_dict:
            # Si le paramètre a une valeur par défaut, l'utiliser
            if "default" in param:
                params_dict[param["name"]] = param["default"]
            else:
                missing_params.append(param)
    
    # Demander les paramètres manquants
    if missing_params:
        console.print("[yellow]Paramètres requis manquants:[/yellow]")
        for param in missing_params:
            value = Prompt.ask(
                f"{param['description']} ({param['name']})",
                default="" if "default" not in param else str(param["default"])
            )
            params_dict[param["name"]] = value
    
    # Connecter au provider approprié
    console.print(f"[bold]Connexion au provider: [cyan]{provider.upper()}[/cyan][/bold]")
    
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
    
    # Préparer le déploiement
    console.print(f"\n[bold]Préparation du déploiement du template: [cyan]{template_name}[/cyan][/bold]")
    console.print("[bold]Paramètres:[/bold]")
    for key, value in params_dict.items():
        console.print(f" - [green]{key}:[/green] {value}")
    
    try:
        # Préparer le déploiement (créer le répertoire de travail et copier les fichiers)
        deployment_dir = prepare_deployment(template_name, params_dict)
        
        if not deployment_dir:
            # Simuler le déploiement pour la démonstration
            from uuid import uuid4
            from datetime import datetime
            
            deployment_id = str(uuid4())
            console.print("\n[bold]Déploiement simulé (pour démonstration)...[/bold]")
            
            with console.status("[bold green]Initialisation de Terraform...[/bold green]"):
                import time
                time.sleep(1)
            
            with console.status("[bold green]Planification du déploiement...[/bold green]"):
                time.sleep(1)
            
            if not auto_approve:
                proceed = Confirm.ask("Voulez-vous procéder au déploiement?")
                if not proceed:
                    console.print("[yellow]Déploiement annulé.[/yellow]")
                    return
            
            with console.status("[bold green]Déploiement en cours...[/bold green]"):
                time.sleep(2)
            
            console.print("[bold green]Déploiement simulé réussi ![/bold green]")
            console.print(f"[bold]ID du déploiement:[/bold] {deployment_id}")
            console.print(f"[bold]Date:[/bold] {datetime.now().isoformat()}")
            
            return
        
        # Exécuter Terraform
        success = run_terraform(deployment_dir, auto_approve)
        
        if success:
            console.print("[bold green]Déploiement réussi ![/bold green]")
            
            # Afficher les informations du déploiement
            metadata_file = os.path.join(deployment_dir, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                
                console.print(f"[bold]ID du déploiement:[/bold] {metadata.get('id', 'inconnu')}")
                console.print(f"[bold]Date:[/bold] {metadata.get('created_at', 'inconnue')}")
                
                # Afficher les outputs si disponibles
                if "outputs" in metadata:
                    console.print("\n[bold]Outputs:[/bold]")
                    for key, value in metadata["outputs"].items():
                        console.print(f" - [green]{key}:[/green] {value}")
        else:
            console.print("[bold red]Erreur lors du déploiement.[/bold red]")
            
    except Exception as e:
        console.print(f"[red]Erreur lors du déploiement: {e}[/red]")

@app.command("destroy")
def destroy_deployment(
    deployment_id: str = typer.Argument(..., help="ID du déploiement à détruire"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Approuver automatiquement la destruction")
):
    """
    Détruit un déploiement existant
    """
    from cloudya.utils.terraform import get_deployment_dir, get_deployment_info, destroy_deployment
    
    # Vérifier si le déploiement existe
    deployment_dir = get_deployment_dir(deployment_id)
    
    if not deployment_dir:
        console.print(f"[red]Déploiement '{deployment_id}' non trouvé.[/red]")
        return
    
    # Récupérer les informations du déploiement
    deployment_info = get_deployment_info(deployment_id)
    
    if not deployment_info:
        console.print(f"[red]Impossible de récupérer les informations du déploiement '{deployment_id}'.[/red]")
        return
    
    # Afficher les informations du déploiement
    console.print(f"[bold]Déploiement:[/bold] {deployment_id}")
    console.print(f"[bold]Template:[/bold] {deployment_info.get('template', 'inconnu')}")
    console.print(f"[bold]Créé le:[/bold] {deployment_info.get('created_at', 'inconnu')}")
    console.print(f"[bold]Statut:[/bold] {deployment_info.get('status', 'inconnu')}")
    
    # Demander confirmation si auto_approve n'est pas activé
    if not auto_approve:
        confirm = Confirm.ask("Êtes-vous sûr de vouloir détruire ce déploiement?")
        if not confirm:
            console.print("[yellow]Destruction annulée.[/yellow]")
            return
    
    # Extraire le provider à partir du template
    template = deployment_info.get('template', '')
    provider = template.split('/')[0] if '/' in template else None
    
    # Connecter au provider si possible
    if provider in ["aws", "gcp", "azure", "openstack", "proxmox", "vmware", "nutanix"]:
        console.print(f"[bold]Connexion au provider: [cyan]{provider.upper()}[/cyan][/bold]")
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
            console.print(f"[yellow]Avertissement: Erreur lors de la connexion au provider {provider}: {e}[/yellow]")
            if not Confirm.ask("Continuer quand même avec la destruction?"):
                return
    
    # Détruire le déploiement
    console.print(f"[bold]Destruction du déploiement '{deployment_id}' en cours...[/bold]")
    
    try:
        success = destroy_deployment(deployment_dir)
        
        if success:
            console.print("[bold green]Déploiement détruit avec succès ![/bold green]")
        else:
            console.print("[bold red]Erreur lors de la destruction du déploiement.[/bold red]")
            
    except Exception as e:
        console.print(f"[red]Erreur lors de la destruction: {e}[/red]")

@app.command("list-deployments")
def list_deployments():
    """
    Liste tous les déploiements
    """
    from cloudya.utils.terraform import list_deployments
    
    # Récupérer tous les déploiements
    deployments = list_deployments()
    
    if not deployments:
        console.print("[yellow]Aucun déploiement trouvé.[/yellow]")
        return
    
    console.print("[bold]Déploiements:[/bold]")
    
    # Créer une table pour afficher les déploiements
    from rich.table import Table
    table = Table(title="Déploiements")
    
    # Ajouter les colonnes
    table.add_column("ID", style="cyan")
    table.add_column("Template", style="green")
    table.add_column("Créé le", style="yellow")
    table.add_column("Statut", style="white")
    
    # Ajouter les lignes
    for deployment in deployments:
        table.add_row(
            deployment.get("id", ""),
            deployment.get("template", ""),
            deployment.get("created_at", ""),
            deployment.get("status", "")
        )
    
    # Afficher la table
    console.print(table)

if __name__ == "__main__":
    app()
