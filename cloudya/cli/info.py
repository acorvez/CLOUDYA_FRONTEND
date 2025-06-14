#!/usr/bin/env python3
import argparse
import requests
import os
import sys
import json
import configparser
from pathlib import Path

# Configuration
CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def get_config():
    """Charge la configuration"""
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    return config

def get_token():
    """Récupère le token d'API"""
    # Vérifier d'abord la variable d'environnement
    token = os.environ.get("CLOUDYA_API_TOKEN")
    
    # Si pas de token dans l'environnement, vérifier la configuration
    if not token:
        config = get_config()
        if 'auth' in config and 'token' in config['auth']:
            token = config['auth']['token']
    
    return token

def main():
    # Définir les arguments de la commande
    parser = argparse.ArgumentParser(description="Afficher les informations sur votre compte Cloudya")
    parser.add_argument("--api-url", help="URL de l'API Cloudya (par défaut: depuis la configuration)")
    args = parser.parse_args()
    
    # Obtenir l'URL de l'API
    config = get_config()
    api_url = args.api_url or config.get('api', 'url', fallback='https://api.cloudya.ai')
    
    # Obtenir le token
    token = get_token()
    if not token:
        print("Vous n'êtes pas connecté à Cloudya.")
        print("Connectez-vous d'abord avec: cloudya login")
        return 1
    
    print("Récupération des informations du compte...")
    
    try:
        # Faire la requête à l'API
        response = requests.get(
            f"{api_url}/api/tokens/info",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Traiter la réponse
        if response.status_code == 200:
            data = response.json()
            
            print("\n===== Informations du compte =====")
            print(f"Utilisateur ID: {data.get('user_id', 'N/A')}")
            print(f"Email: {data.get('email', 'N/A')}")
            print(f"Plan: {data.get('plan', 'N/A')}")
            print(f"Tokens restants: {data.get('remaining_tokens', 'N/A')}")
            print(f"Expiration: {data.get('expiry', 'N/A')}")
            
            if "daily_trend" in data:
                print("\n===== Utilisation récente =====")
                for day in data["daily_trend"]:
                    print(f"{day['date']}: {day['tokens']} tokens utilisés")
            
            if "subscription" in data:
                sub = data["subscription"]
                print("\n===== Abonnement =====")
                print(f"Statut: {sub.get('status', 'N/A')}")
                print(f"Renouvelement: {sub.get('current_period_end', 'N/A')}")
                if sub.get('cancel_at_period_end', False):
                    print("Cet abonnement sera annulé à la fin de la période en cours.")
            
            return 0
        else:
            print(f"Erreur: {response.status_code}")
            print(response.text)
            
            # Si non autorisé, suggérer de se connecter
            if response.status_code == 401:
                print("\nVotre session a expiré. Veuillez vous reconnecter:")
                print("  cloudya login")
            
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