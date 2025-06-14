#!/usr/bin/env python3
import argparse
import os
import sys
import configparser
from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def main():
    # Définir les arguments de la commande
    parser = argparse.ArgumentParser(description="Se déconnecter de l'API Cloudya")
    args = parser.parse_args()
    
    # Vérifier si le fichier de configuration existe
    if not CONFIG_FILE.exists():
        print("Vous n'êtes pas connecté à Cloudya.")
        return 0
    
    # Charger la configuration
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    # Supprimer le token s'il existe
    if 'auth' in config and 'token' in config['auth']:
        del config['auth']['token']
        
        # Sauvegarder la configuration mise à jour
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    
    print("Déconnexion réussie!")
    return 0

if __name__ == "__main__":
    sys.exit(main())