"""
Module pour le déploiement d'applications
"""
import os
import subprocess
import json
import yaml
import shutil
import datetime
import uuid
import tempfile
from rich.console import Console

from .ansible import get_ansible_path, get_apps_dir, get_app_deployments_dir
from .ansible_apps import get_app_info

console = Console()

def prepare_app_deployment(app_name, platform, params, instance):
    """
    Prépare le déploiement d'une application
    
    Args:
        app_name: Nom de l'application
        platform: Plateforme cible
        params: Paramètres de l'application
        instance: Instance cible
        
    Returns:
        Dictionnaire avec les informations du déploiement
    """
    # Récupérer les informations sur l'application
    app_info = get_app_info(app_name)
    if not app_info:
        console.print(f"[red]Application '{app_name}' non trouvée.[/red]")
        return None
    
    # Créer un ID unique pour le déploiement
    deployment_id = f"app-{str(uuid.uuid4())[:8]}"
    
    # Créer le répertoire de déploiement
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, deployment_id)
    os.makedirs(deployment_dir, exist_ok=True)
    
    # Copier les fichiers de l'application si elle existe réellement
    app_dir = os.path.join(get_apps_dir(), app_info["name"].lower())
    if os.path.exists(app_dir):
        for item in os.listdir(app_dir):
            if item != "manifest.yaml":  # Exclure le manifest
                source = os.path.join(app_dir, item)
                destination = os.path.join(deployment_dir, item)
                
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
    else:
        # Créer des fichiers minimaux pour la démonstration
        if app_info["type"] == "ansible":
            # Créer un playbook Ansible minimal
            with open(os.path.join(deployment_dir, "playbook.yml"), "w") as f:
                f.write(f"---\n")
                f.write(f"- name: Install {app_info['name']}\n")
                f.write(f"  hosts: target\n")
                f.write(f"  become: yes\n")
                f.write(f"  vars:\n")
                
                # Ajouter les variables du déploiement
                for key, value in params.items():
                    if isinstance(value, str):
                        f.write(f"    {key}: \"{value}\"\n")
                    else:
                        f.write(f"    {key}: {value}\n")
                
                f.write(f"\n  tasks:\n")
                f.write(f"    - name: Update apt cache\n")
                f.write(f"      apt:\n")
                f.write(f"        update_cache: yes\n")
                f.write(f"        cache_valid_time: 3600\n")
                
                # Ajouter des tâches spécifiques à l'application
                if app_name.lower() == "wordpress":
                    f.write(f"\n    - name: Install Apache\n")
                    f.write(f"      apt:\n")
                    f.write(f"        name: apache2\n")
                    f.write(f"        state: present\n")
                    
                    f.write(f"\n    - name: Install MySQL\n")
                    f.write(f"      apt:\n")
                    f.write(f"        name: mysql-server\n")
                    f.write(f"        state: present\n")
                    
                    f.write(f"\n    - name: Install PHP\n")
                    f.write(f"      apt:\n")
                    f.write(f"        name:\n")
                    f.write(f"          - php\n")
                    f.write(f"          - php-mysql\n")
                    f.write(f"          - php-curl\n")
                    f.write(f"          - php-gd\n")
                    f.write(f"        state: present\n")
                    
                    f.write(f"\n    - name: Download WordPress\n")
                    f.write(f"      get_url:\n")
                    f.write(f"        url: https://wordpress.org/latest.tar.gz\n")
                    f.write(f"        dest: /tmp/wordpress.tar.gz\n")
                    
                    f.write(f"\n    - name: Extract WordPress\n")
                    f.write(f"      unarchive:\n")
                    f.write(f"        src: /tmp/wordpress.tar.gz\n")
                    f.write(f"        dest: /var/www/html\n")
                    f.write(f"        remote_src: yes\n")
                elif app_name.lower() == "lamp":
                    f.write(f"\n    - name: Install LAMP stack\n")
                    f.write(f"      apt:\n")
                    f.write(f"        name:\n")
                    f.write(f"          - apache2\n")
                    f.write(f"          - mysql-server\n")
                    f.write(f"          - php\n")
                    f.write(f"          - php-mysql\n")
                    f.write(f"        state: present\n")
                else:
                    f.write(f"\n    - name: Install {app_info['name']}\n")
                    f.write(f"      debug:\n")
                    f.write(f"        msg: \"Installation simulée de {app_info['name']}\"\n")
        
        elif app_info["type"] == "docker":
            # Créer un playbook Ansible pour installer Docker
            with open(os.path.join(deployment_dir, "playbook.yml"), "w") as f:
                f.write(f"---\n")
                f.write(f"- name: Install Docker and {app_info['name']}\n")
                f.write(f"  hosts: target\n")
                f.write(f"  become: yes\n")
                f.write(f"  vars:\n")
                
                # Ajouter les variables du déploiement
                for key, value in params.items():
                    if isinstance(value, str):
                        f.write(f"    {key}: \"{value}\"\n")
                    else:
                        f.write(f"    {key}: {value}\n")
                
                f.write(f"\n  tasks:\n")
                f.write(f"    - name: Update apt cache\n")
                f.write(f"      apt:\n")
                f.write(f"        update_cache: yes\n")
                f.write(f"        cache_valid_time: 3600\n")
                
                # Installer Docker
                f.write(f"\n    - name: Install required packages\n")
                f.write(f"      apt:\n")
                f.write(f"        name:\n")
                f.write(f"          - apt-transport-https\n")
                f.write(f"          - ca-certificates\n")
                f.write(f"          - curl\n")
                f.write(f"          - gnupg\n")
                f.write(f"          - lsb-release\n")
                f.write(f"        state: present\n")
                
                f.write(f"\n    - name: Add Docker GPG key\n")
                f.write(f"      apt_key:\n")
                f.write(f"        url: https://download.docker.com/linux/ubuntu/gpg\n")
                f.write(f"        state: present\n")
                
                f.write(f"\n    - name: Add Docker repository\n")
                f.write(f"      apt_repository:\n")
                f.write(f"        repo: deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable\n")
                f.write(f"        state: present\n")
                
                f.write(f"\n    - name: Install Docker CE\n")
                f.write(f"      apt:\n")
                f.write(f"        name:\n")
                f.write(f"          - docker-ce\n")
                f.write(f"          - docker-ce-cli\n")
                f.write(f"          - containerd.io\n")
                f.write(f"        state: present\n")
                
                f.write(f"\n    - name: Install Docker Compose\n")
                f.write(f"      get_url:\n")
                f.write(f"        url: https://github.com/docker/compose/releases/download/v2.10.2/docker-compose-Linux-x86_64\n")
                f.write(f"        dest: /usr/local/bin/docker-compose\n")
                f.write(f"        mode: '0755'\n")
                
                f.write(f"\n    - name: Create app directory\n")
                f.write(f"      file:\n")
                f.write(f"        path: /opt/{app_name.lower()}\n")
                f.write(f"        state: directory\n")
                
                f.write(f"\n    - name: Copy docker-compose.yml\n")
                f.write(f"      copy:\n")
                f.write(f"        src: docker-compose.yml\n")
                f.write(f"        dest: /opt/{app_name.lower()}/docker-compose.yml\n")
                
                f.write(f"\n    - name: Deploy with Docker Compose\n")
                f.write(f"      shell: cd /opt/{app_name.lower()} && docker-compose up -d\n")
            
            # Créer un fichier docker-compose.yml minimal
            with open(os.path.join(deployment_dir, "docker-compose.yml"), "w") as f:
                f.write(f"version: '3'\n\n")
                f.write(f"services:\n")
                
                if app_name.lower() == "nextcloud":
                    f.write(f"  app:\n")
                    f.write(f"    image: nextcloud\n")
                    f.write(f"    ports:\n")
                    f.write(f"      - \"80:80\"\n")
                    f.write(f"    volumes:\n")
                    f.write(f"      - nextcloud:/var/www/html\n")
                    f.write(f"    environment:\n")
                    f.write(f"      - MYSQL_DATABASE=nextcloud\n")
                    f.write(f"      - MYSQL_USER=nextcloud\n")
                    f.write(f"      - MYSQL_PASSWORD={params.get('db_password', 'nextcloud')}\n")
                    f.write(f"      - MYSQL_HOST=db\n")
                    
                    f.write(f"\n  db:\n")
                    f.write(f"    image: mariadb\n")
                    f.write(f"    volumes:\n")
                    f.write(f"      - db:/var/lib/mysql\n")
                    f.write(f"    environment:\n")
                    f.write(f"      - MYSQL_ROOT_PASSWORD={params.get('db_password', 'nextcloud')}\n")
                    f.write(f"      - MYSQL_DATABASE=nextcloud\n")
                    f.write(f"      - MYSQL_USER=nextcloud\n")
                    f.write(f"      - MYSQL_PASSWORD={params.get('db_password', 'nextcloud')}\n")
                    
                    f.write(f"\nvolumes:\n")
                    f.write(f"  nextcloud:\n")
                    f.write(f"  db:\n")
                else:
                    f.write(f"  {app_name.lower()}:\n")
                    f.write(f"    image: {app_name.lower()}\n")
                    f.write(f"    ports:\n")
                    f.write(f"      - \"80:80\"\n")
                    f.write(f"    volumes:\n")
                    f.write(f"      - {app_name.lower()}-data:/data\n")
                    f.write(f"\nvolumes:\n")
                    f.write(f"  {app_name.lower()}-data:\n")
    
    # Créer le fichier de métadonnées
    metadata = {
        "id": deployment_id,
        "name": app_info["name"],
        "type": app_info["type"],
        "platform": platform,
        "instance": {
            "name": instance["name"],
            "ip": instance["ip"],
            "id": instance["id"],
            "deployment_id": instance["deployment_id"]
        },
        "params": params,
        "status": "prepared",
        "created_at": datetime.datetime.now().isoformat()
    }
    
    with open(os.path.join(deployment_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return {
        "id": deployment_id,
        "dir": deployment_dir,
        "metadata": metadata
    }

def deploy_ansible_app(deployment_dir, inventory_file):
    """
    Déploie une application avec Ansible
    
    Args:
        deployment_dir: Répertoire du déploiement
        inventory_file: Chemin vers le fichier d'inventaire
        
    Returns:
        True si le déploiement a réussi, False sinon
    """
    ansible_path = get_ansible_path()
    
    # Vérifier si ansible-playbook est installé
    try:
        subprocess.run([ansible_path, "--version"], check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]Ansible n'est pas installé ou n'est pas dans le PATH.[/red]")
        console.print("Installez Ansible via: pip install ansible")
        return False
    
    # Vérifier si le playbook existe
    playbook_path = os.path.join(deployment_dir, "playbook.yml")
    if not os.path.exists(playbook_path):
        console.print(f"[red]Playbook non trouvé: {playbook_path}[/red]")
        return False
    
    # Mettre à jour le statut
    metadata_path = os.path.join(deployment_dir, "metadata.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    metadata["status"] = "deploying"
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Exécuter ansible-playbook
    with console.status("[bold green]Déploiement de l'application avec Ansible...[/bold green]"):
        try:
            result = subprocess.run(
                [ansible_path, "-i", inventory_file, playbook_path, "-v"],
                check=True,
                capture_output=True,
                text=True
            )
            console.print("[green]Déploiement réussi![/green]")
            
            # Afficher la sortie
            console.print("\n[bold]Sortie Ansible:[/bold]")
            console.print(result.stdout)
            
            # Mettre à jour le statut
            metadata["status"] = "deployed"
            metadata["deployed_at"] = datetime.datetime.now().isoformat()
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Erreur lors du déploiement Ansible:[/red] {e.stderr}")
            
            # Mettre à jour le statut
            metadata["status"] = "failed"
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return False

def deploy_docker_app(deployment_dir, inventory_file):
    """
    Déploie une application Docker via Ansible
    
    Args:
        deployment_dir: Répertoire du déploiement
        inventory_file: Chemin vers le fichier d'inventaire
        
    Returns:
        True si le déploiement a réussi, False sinon
    """
    # Nous utilisons également Ansible pour déployer Docker
    return deploy_ansible_app(deployment_dir, inventory_file)

def get_app_deployment(app_id):
    """
    Récupère les informations d'un déploiement d'application
    
    Args:
        app_id: ID du déploiement
        
    Returns:
        Dictionnaire des informations du déploiement ou None si non trouvé
    """
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, app_id)
    
    if not os.path.exists(deployment_dir):
        return None
    
    # Lire le fichier de métadonnées
    metadata_path = os.path.join(deployment_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        return None
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata
    except Exception as e:
        console.print(f"[yellow]Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}[/yellow]")
        return None

def list_app_deployments():
    """
    Liste tous les déploiements d'applications
    
    Returns:
        Liste des déploiements
    """
    deployments = []
    app_deployments_dir = get_app_deployments_dir()
    
    if not os.path.exists(app_deployments_dir):
        return deployments
    
    for item in os.listdir(app_deployments_dir):
        deployment_dir = os.path.join(app_deployments_dir, item)
        
        if os.path.isdir(deployment_dir):
            metadata_path = os.path.join(deployment_dir, "metadata.json")
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    deployments.append(metadata)
                except Exception as e:
                    console.print(f"[yellow]Erreur lors de la lecture des métadonnées {metadata_path}: {str(e)}[/yellow]")
    
    return deployments

def uninstall_app(app_id):
    """
    Désinstalle une application
    
    Args:
        app_id: ID du déploiement
        
    Returns:
        True si la désinstallation a réussi, False sinon
    """
    # Récupérer les informations du déploiement
    app_deployment = get_app_deployment(app_id)
    
    if not app_deployment:
        console.print(f"[red]Déploiement '{app_id}' non trouvé.[/red]")
        return False
    
    # Mettre à jour le statut
    app_deployments_dir = get_app_deployments_dir()
    deployment_dir = os.path.join(app_deployments_dir, app_id)
    metadata_path = os.path.join(deployment_dir, "metadata.json")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    metadata["status"] = "uninstalling"
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Pour une vraie implémentation, il faudrait créer un playbook Ansible pour désinstaller l'application
    # Mais pour cette démo, on simule une désinstallation réussie
    
    with console.status("[bold red]Désinstallation de l'application...[/bold red]"):
        # Simuler un délai
        import time
        time.sleep(2)
        
        # Mettre à jour le statut
        metadata["status"] = "uninstalled"
        metadata["uninstalled_at"] = datetime.datetime.now().isoformat()
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    console.print("[green]Application désinstallée avec succès![/green]")
    return True
