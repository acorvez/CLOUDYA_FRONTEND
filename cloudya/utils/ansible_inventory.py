"""
Module pour la gestion des inventaires Ansible
"""
import os
import tempfile
from rich.console import Console
from rich.prompt import Prompt, IntPrompt

console = Console()

def prepare_inventory(instance, ssh_user="ubuntu", ssh_key=None):
    """
    Prépare un fichier d'inventaire Ansible pour une instance
    
    Args:
        instance: Instance à ajouter à l'inventaire
        ssh_user: Utilisateur SSH pour la connexion
        ssh_key: Chemin vers la clé SSH privée
        
    Returns:
        Chemin vers le fichier d'inventaire
    """
    # Demander l'utilisateur SSH si non spécifié
    if not ssh_user:
        ssh_user = Prompt.ask(
            "Utilisateur SSH pour la connexion à l'instance",
            default="ubuntu"
        )
    
    # Demander la clé SSH si non spécifiée
    if not ssh_key:
        # Proposer quelques emplacements courants
        default_keys = [
            os.path.expanduser("~/.ssh/id_rsa"),
            os.path.expanduser("~/.ssh/id_ed25519")
        ]
        
        available_keys = [key for key in default_keys if os.path.exists(key)]
        
        if available_keys:
            console.print("[bold]Clés SSH disponibles:[/bold]")
            for i, key in enumerate(available_keys, 1):
                console.print(f"{i}. {key}")
            
            key_choice = IntPrompt.ask(
                "Sélectionnez une clé SSH (numéro)",
                default=1,
                show_default=True,
                min_value=1,
                max_value=len(available_keys)
            )
            
            ssh_key = available_keys[key_choice - 1]
        else:
            ssh_key = Prompt.ask(
                "Chemin vers la clé SSH privée",
                default="~/.ssh/id_rsa"
            )
            ssh_key = os.path.expanduser(ssh_key)
    
    # Créer un fichier d'inventaire temporaire
    inventory_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ini")
    
    # Écrire l'inventaire
    with open(inventory_file.name, "w") as f:
        f.write(f"[target]\n")
        f.write(f"{instance['ip']} ansible_user={ssh_user} ansible_ssh_private_key_file={ssh_key}\n")
        f.write("\n[all:vars]\n")
        f.write("ansible_python_interpreter=/usr/bin/python3\n")
    
    return inventory_file.name
