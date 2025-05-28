"""
Module de configuration pour Cloudya
"""
import os
import json
from pathlib import Path

def get_cloudya_dir():
    """
    Récupère le répertoire de base de Cloudya
    """
    return os.path.expanduser("~/.cloudya")

def load_config():
    """
    Charge la configuration de Cloudya
    
    Returns:
        Dictionnaire de configuration
    """
    config_dir = get_cloudya_dir()
    config_file = os.path.join(config_dir, "config.json")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)
    
    # Créer le fichier de configuration s'il n'existe pas
    if not os.path.exists(config_file):
        default_config = {
            "terraform_path": "terraform",
            "ansible_path": "ansible-playbook",
            "templates_dir": os.path.expanduser("~/.cloudya/templates"),
            "log_level": "INFO"
        }
        
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    # Charger la configuration
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return {
            "terraform_path": "terraform",
            "ansible_path": "ansible-playbook",
            "templates_dir": os.path.expanduser("~/.cloudya/templates"),
            "log_level": "INFO"
        }

def save_config(config):
    """
    Sauvegarde la configuration de Cloudya
    
    Args:
        config: Dictionnaire de configuration
        
    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    config_dir = get_cloudya_dir()
    config_file = os.path.join(config_dir, "config.json")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(config_dir, exist_ok=True)
    
    # Sauvegarder la configuration
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")
        return False
