"""
Module pour la gestion des instances pour déploiement d'applications
"""
import os
import datetime
from rich.console import Console
from rich.prompt import IntPrompt, Confirm
from rich.table import Table

# Importer le module terraform pour accéder aux déploiements
from .terraform import list_deployments

console = Console()

def get_terraform_instances():
    """
    Récupère la liste des instances déployées via Terraform
    
    Returns:
        Liste des instances déployées
    """
    instances = []
    
    # Récupérer tous les déploiements Terraform
    deployments = list_deployments()
    
    for deployment in deployments:
        # Ignorer les déploiements non déployés ou détruits
        if deployment.get("status") not in ["deployed", "updated"]:
            continue
        
        # Récupérer les outputs du déploiement
        outputs = deployment.get("outputs", {})
        
        # Extraire les instances des outputs
        # La structure dépend du template utilisé, mais nous cherchons des outputs
        # contenant des informations sur les instances (ip, id, etc.)
        for output_name, output_value in outputs.items():
            if isinstance(output_value, dict) and ("ip" in output_value or "address" in output_value or "host" in output_value):
                # Il s'agit probablement d'une instance
                instance = {
                    "name": output_name,
                    "deployment_id": deployment.get("id"),
                    "template": deployment.get("template"),
                    "ip": output_value.get("ip") or output_value.get("address") or output_value.get("host"),
                    "id": output_value.get("id", ""),
                    "platform": deployment.get("template", "").split("/")[0] if "/" in deployment.get("template", "") else "",
                    "created_at": deployment.get("created_at")
                }
                instances.append(instance)
            elif isinstance(output_value, str) and (output_name.endswith("_ip") or output_name.endswith("_address") or output_name.endswith("_host")):
                # Il s'agit probablement d'une adresse IP directe
                instance_name = output_name.replace("_ip", "").replace("_address", "").replace("_host", "")
                instance = {
                    "name": instance_name,
                    "deployment_id": deployment.get("id"),
                    "template": deployment.get("template"),
                    "ip": output_value,
                    "id": "",
                    "platform": deployment.get("template", "").split("/")[0] if "/" in deployment.get("template", "") else "",
                    "created_at": deployment.get("created_at")
                }
                instances.append(instance)
    
    # Si aucune instance n'est trouvée, utiliser des instances fictives pour la démonstration
    if not instances and os.environ.get("CLOUDYA_DEMO_MODE") == "1":
        instances = [
            {
                "name": "web-server",
                "deployment_id": "00000000-0000-0000-0000-000000000001",
                "template": "aws/ec2",
                "ip": "192.168.1.10",
                "id": "i-0123456789abcdef0",
                "platform": "aws",
                "created_at": datetime.datetime.now().isoformat()
            },
            {
                "name": "db-server",
                "deployment_id": "00000000-0000-0000-0000-000000000001",
                "template": "aws/ec2",
                "ip": "192.168.1.11",
                "id": "i-0123456789abcdef1",
                "platform": "aws",
                "created_at": datetime.datetime.now().isoformat()
            },
            {
                "name": "app-server",
                "deployment_id": "00000000-0000-0000-0000-000000000002",
                "template": "gcp/vm",
                "ip": "192.168.2.10",
                "id": "instance-1",
                "platform": "gcp",
                "created_at": datetime.datetime.now().isoformat()
            }
        ]
    
    return instances

def select_instance(platform=None):
    """
    Permet à l'utilisateur de sélectionner une instance
    
    Args:
        platform: Plateforme à filtrer (optionnel)
        
    Returns:
        Instance sélectionnée ou None si aucune sélection
    """
    # Récupérer les instances déployées
    instances = get_terraform_instances()
    
    # Filtrer par plateforme si spécifiée
    if platform:
        instances = [instance for instance in instances if instance["platform"] == platform]
    
    if not instances:
        console.print("[yellow]Aucune instance déployée trouvée.[/yellow]")
        if platform:
            console.print(f"[yellow]Assurez-vous d'avoir déployé des instances sur la plateforme {platform}.[/yellow]")
        else:
            console.print("[yellow]Déployez d'abord des instances avec la commande 'cloudya deploy'.[/yellow]")
        return None
    
    # Afficher les instances disponibles
    table = Table(title="Instances disponibles")
    table.add_column("#", style="cyan")
    table.add_column("Nom", style="green")
    table.add_column("Adresse IP", style="yellow")
    table.add_column("Plateforme", style="magenta")
    table.add_column("Template", style="blue")
    
    for i, instance in enumerate(instances, 1):
        table.add_row(
            str(i),
            instance["name"],
            instance["ip"],
            instance["platform"],
            instance["template"]
        )
    
    console.print(table)
    
    # Demander à l'utilisateur de sélectionner une instance
    choice = IntPrompt.ask(
        "Sélectionnez une instance (numéro)",
        default=1,
        show_default=True,
        min_value=1,
        max_value=len(instances)
    )
    
    return instances[choice - 1]
