#!/usr/bin/env python3
import argparse
import os
import sys
import configparser
from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def get_config():
    """Charge la configuration ou crée une configuration par défaut"""
    # Créer le répertoire de configuration s'il n'existe pas
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config = configparser.ConfigParser()
    
    # Si le fichier de configuration existe, le charger
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    else:
        # Sinon, créer une configuration par défaut
        config['api'] = {
            'url': 'https://api.cloudya.ai'  # URL par défaut
        }
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    
    return config

def main():
    # Définir les arguments de la commande
    parser = argparse.ArgumentParser(description="Configurer l'API Cloudya")
    parser.add_argument("--api-url", help="URL de l'API Cloudya")
    args = parser.parse_args()
    
    # Charger la configuration existante
    config = get_config()
    
    # Si l'URL est fournie en argument, la définir
    if args.api_url:
        if 'api' not in config:
            config['api'] = {}
        config['api']['url'] = args.api_url
        
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        
        print(f"URL de l'API configurée: {args.api_url}")
    else:
        # Sinon, afficher la configuration actuelle et demander la nouvelle URL
        current_url = config.get('api', 'url', fallback='https://api.cloudya.ai')
        
        print(f"URL actuelle de l'API: {current_url}")
        new_url = input(f"Nouvelle URL de l'API [{current_url}]: ") or current_url
        
        if new_url != current_url:
            if 'api' not in config:
                config['api'] = {}
            config['api']['url'] = new_url
            
            with open(CONFIG_FILE, 'w') as f:
                config.write(f)
            
            print(f"URL de l'API configurée: {new_url}")
        else:
            print("Configuration inchangée.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())