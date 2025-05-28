#!/usr/bin/env python3
import configparser
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def setup_test_environment():
    """Configure l'environnement de test local"""
    
    # Créer le répertoire de configuration
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configuration pour les tests
    config = configparser.ConfigParser()
    config['api'] = {
        'url': 'http://localhost:8000'
    }
    # Ne pas définir de token - l'utilisateur devra se connecter
    
    # Sauvegarder la configuration
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    
    print("✅ Configuration de test créée")
    print(f"📁 Fichier de config: {CONFIG_FILE}")
    print("🔧 API URL: http://localhost:8000")
    print("\n🔑 Pour vous connecter:")
    print("   cloudya login")
    print("   Email: test@example.com")
    print("   Mot de passe: n'importe quoi")
    print("\n💡 Puis testez avec:")
    print("   cloudya ask 'Créer un bucket S3'")
    print("   cloudya chat")

if __name__ == "__main__":
    setup_test_environment()