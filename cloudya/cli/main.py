#!/usr/bin/env python3
"""
Point d'entrée principal pour Cloudya CLI
Inspiré de la structure d'Ansible
"""

import os
import sys
import subprocess
from pathlib import Path

def get_cli_directory():
    """Retourne le répertoire contenant les modules CLI"""
    return Path(__file__).parent.absolute()

def list_available_commands():
    """Liste les commandes CLI disponibles"""
    cli_dir = get_cli_directory()
    commands = []
    
    for file in cli_dir.glob("*.py"):
        if file.name not in ["__init__.py", "main.py"]:
            commands.append(file.stem)
    
    return sorted(commands)

def show_help():
    """Affiche l'aide principale"""
    print("🌩️ Cloudya CLI - DevOps intelligente pour l'automatisation d'infrastructures cloud")
    print()
    print("Usage: cloudya COMMAND [OPTIONS] [ARGS]...")
    print()
    print("Commandes disponibles:")
    
    commands = list_available_commands()
    if commands:
        for cmd in commands:
            description = get_command_description(cmd)
            print(f"  {cmd:<15} # {description}")
    else:
        print("  Aucune commande trouvée")
    
    print()
    print("Exemples:")
    print("  cloudya chat")
    print("  cloudya deploy list")
    print("  cloudya app install wordpress --platform aws")
    print()
    print("Pour l'aide d'une commande spécifique:")
    print("  cloudya COMMAND --help")

def get_command_description(command):
    """Retourne la description d'une commande"""
    descriptions = {
        "template": "Gérer les templates (list, show, install, remove)",
        "chat": "Interface de chat avec l'assistant IA",
        "deploy": "Déployer des infrastructures avec Terraform",
        "app": "Gérer les applications avec Ansible/Docker",
        "stack": "Déployer des stacks complètes",
        "monitor": "Surveiller les ressources système",
        "diagnose": "Diagnostiquer les problèmes",
        "connect": "Se connecter aux providers cloud",
        "login": "Se connecter à l'API Cloudya",
        "logout": "Se déconnecter de l'API Cloudya", 
        "register": "S'inscrire à l'API Cloudya",
        "info": "Afficher les informations de compte",
        "configure": "Configurer Cloudya",
        "ask": "Poser une question à l'IA",
        "hello": "Commandes de test",
        "chat_simple": "Chat simple en mode texte"
    }
    return descriptions.get(command, "")

def execute_command(command, args):
    """Exécute une commande CLI"""
    debug = os.environ.get("CLOUDYA_DEBUG") == "1"
    
    # Commandes intégrées
    if command in ["version", "--version", "-v"]:
        try:
            from cloudya import __version__
            print(f"Cloudya CLI v{__version__}")
        except ImportError:
            print("Cloudya CLI v1.0.0")
        return 0
    
    if command in ["help", "--help", "-h"]:
        show_help()
        return 0
    
    # Vérifier si la commande existe
    cli_dir = get_cli_directory()
    command_file = cli_dir / f"{command}.py"
    
    if not command_file.exists():
        print(f"❌ Erreur: Commande '{command}' inconnue.")
        print()
        available = list_available_commands()
        if available:
            print("Commandes disponibles:")
            for cmd in available:
                print(f"  {cmd}")
        else:
            print("Aucune commande disponible.")
        print()
        print("Utilisez 'cloudya help' pour plus d'informations.")
        return 1
    
    # Exécuter la commande
    try:
        if debug:
            print(f"🐛 Debug: Exécution de {command_file} avec args: {args}")
        
        # Exécuter le module CLI
        result = subprocess.run([sys.executable, str(command_file)] + args)
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️ Commande interrompue par l'utilisateur.")
        return 1
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de '{command}': {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 1

def main():
    """Point d'entrée principal - appelé par l'exécutable cloudya"""
    # Si aucun argument, afficher l'aide
    if len(sys.argv) <= 1:
        show_help()
        return 0
    
    # Parser les arguments
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Exécuter la commande
    return execute_command(command, args)

if __name__ == "__main__":
    sys.exit(main())
