#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    # Obtenir le répertoire racine du projet (où se trouve cli.py)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Debug mode
    debug = os.environ.get("CLOUDYA_DEBUG") == "1"
    
    # Afficher des informations de débogage
    if debug:
        print(f"Répertoire racine: {root_dir}")
    
    # Chemin vers le répertoire commands - d'abord essayer la structure complète
    commands_dir = os.path.join(root_dir, "cloudya", "commands")
    
    # Vérifier si le répertoire existe, sinon utiliser le répertoire commands au niveau racine
    if not os.path.isdir(commands_dir):
        commands_dir = os.path.join(root_dir, "commands")
    
    if debug:
        print(f"Répertoire des commandes: {commands_dir}")
        if os.path.isdir(commands_dir):
            print(f"Contenu du répertoire commands: {os.listdir(commands_dir)}")
        else:
            print(f"Le répertoire des commandes n'existe pas: {commands_dir}")
    
    # Vérifier les arguments
    if len(sys.argv) <= 1 or sys.argv[1] in ["-h", "--help", "help"]:
        print("Usage: cloudya COMMAND [OPTIONS] [ARGS]...")
        print("\nCommandes disponibles :")
        try:
            if os.path.isdir(commands_dir):
                for f in sorted(os.listdir(commands_dir)):
                    if f.endswith('.py') and not f.startswith('__'):
                        cmd = f[:-3]
                        print(f" {cmd}")
            else:
                print("Aucune commande disponible. Le répertoire des commandes n'existe pas.")
        except Exception as e:
            print(f"Erreur lors de la lecture des commandes: {e}")
        print(" version  Afficher la version de Cloudya")
        return 0
    
    # Obtenir la commande et les arguments
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Commande version
    if command == "version":
        print("Cloudya v0.1.0")
        print("Mode: CLI locale (sans IA)")
        return 0
    
    # Chemin vers le script de la commande
    command_file = f"{command}.py"
    command_path = os.path.join(commands_dir, command_file)
    
    if not os.path.exists(command_path):
        print(f"Erreur: Commande '{command}' inconnue.")
        print(f"Fichier non trouvé: {command_path}")
        print("Utilisez 'cloudya --help' pour voir les commandes disponibles.")
        return 1
    
    # Exécuter le script avec les arguments
    try:
        if debug:
            print(f"Exécution de: {sys.executable} {command_path} {' '.join(args)}")
        result = subprocess.run([sys.executable, command_path] + args)
        return result.returncode
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())