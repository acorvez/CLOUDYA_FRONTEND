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

def get_token():
    """Récupère le token d'API depuis la configuration ou les variables d'environnement"""
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
    parser = argparse.ArgumentParser(description="Demander à l'IA Cloudya de l'aide sur l'infrastructure cloud")
    parser.add_argument("prompt", nargs="*", help="Votre question ou demande d'infrastructure cloud")
    parser.add_argument("-e", "--execute", action="store_true", help="Exécuter la commande générée")
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
    
    # Construire la requête
    if not args.prompt:
        prompt = input("Que voulez-vous demander à Cloudya? ")
    else:
        prompt = " ".join(args.prompt)
    
    execution_mode = "supervised" if args.execute else "dry_run"
    
    # Afficher un message d'attente
    print(f"Interrogation de Cloudya AI... {'' if not args.execute else '(mode exécution)'}")
    
    try:
        # Faire la requête à l'API
        response = requests.post(
            f"{api_url}/api/command",
            json={"user_input": prompt, "execution_mode": execution_mode},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        )
        
        # Traiter la réponse
        if response.status_code == 200:
            data = response.json()
            
            # Afficher la commande générée
            print("\n===== Cloudya Command =====")
            print(data.get("action", "Aucune commande générée."))
            
            # Afficher l'explication si présente
            if "explanation" in data and data["explanation"]:
                print("\n===== Explication =====")
                print(data["explanation"])
            
            # Afficher le résultat d'exécution si disponible
            if "output" in data and data["output"]:
                print("\n===== Résultat =====")
                print(data["output"])
            
            # Afficher les informations d'utilisation des tokens
            if "token_usage" in data:
                print(f"\nTokens utilisés: {data['token_usage'].get('total_tokens', 0)}")
                if "remaining_balance" in data["token_usage"]:
                    print(f"Solde restant: {data['token_usage']['remaining_balance']}")
            
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