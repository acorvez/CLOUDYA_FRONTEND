#!/usr/bin/env python3
import argparse
import requests
import os
import sys
import json
import configparser
from pathlib import Path
import getpass

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
    parser = argparse.ArgumentParser(description="S'inscrire à l'API Cloudya")
    parser.add_argument("--email", help="Votre adresse email")
    parser.add_argument("--name", help="Votre nom complet")
    parser.add_argument("--api-url", help="URL de l'API Cloudya (par défaut: depuis la configuration)")
    args = parser.parse_args()
    
    # Obtenir l'URL de l'API
    config = get_config()
    api_url = args.api_url or config.get('api', 'url', fallback='https://api.cloudya.ai')
    
    # Demander les informations d'inscription
    email = args.email or input("Email: ")
    name = args.name or input("Nom complet: ")
    password = getpass.getpass("Mot de passe: ")
    password_confirm = getpass.getpass("Confirmez le mot de passe: ")
    
    # Vérifier que les mots de passe correspondent
    if password != password_confirm:
        print("Erreur: Les mots de passe ne correspondent pas!")
        return 1
    
    print(f"Inscription à Cloudya ({api_url})...")
    
    try:
        # Faire la requête d'inscription
        response = requests.post(
            f"{api_url}/api/auth/register",
            json={
                "email": email,
                "name": name,
                "password": password
            }
        )
        
        # Traiter la réponse
        if response.status_code == 201:
            print("Inscription réussie!")
            print("Veuillez vérifier votre email pour activer votre compte.")
            print("Ensuite, connectez-vous avec: cloudya login")
            return 0
        else:
            print(f"Échec de l'inscription: {response.status_code}")
            print(response.text)
            return 1
    
    except requests.exceptions.ConnectionError:
        print(f"Erreur de connexion: impossible de se connecter à {api_url}")
        print("Vérifiez votre connexion internet ou l'URL de l'API.")
        return 1
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())