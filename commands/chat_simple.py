# Version simplifiée pour commands/chat_simple.py
#!/usr/bin/env python3
import argparse
import requests
import os
import sys
import configparser
from pathlib import Path
import json

CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def get_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    else:
        config['api'] = {'url': 'https://api.cloudya.ai'}
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    return config

def get_token():
    token = os.environ.get("CLOUDYA_API_TOKEN")
    if not token:
        config = get_config()
        if 'auth' in config and 'token' in config['auth']:
            token = config['auth']['token']
    return token

def format_response(data):
    """Formate joliment la réponse de l'API"""
    output = []
    
    if "explanation" in data and data["explanation"]:
        output.append("=" * 60)
        output.append("🤖 CLOUDYA AI")
        output.append("=" * 60)
        output.append(data["explanation"])
        output.append("")
    
    if "action" in data and data["action"]:
        output.append("💻 COMMANDE GÉNÉRÉE")
        output.append("-" * 30)
        output.append(data["action"])
        output.append("")
    
    if "output" in data and data["output"]:
        output.append("✅ RÉSULTAT D'EXÉCUTION")
        output.append("-" * 30)
        output.append(data["output"])
        output.append("")
    
    if "token_usage" in data:
        usage = data["token_usage"]
        output.append(f"📊 Tokens utilisés: {usage.get('total_tokens', 0)}")
        if "remaining_balance" in usage:
            output.append(f"💰 Solde restant: {usage['remaining_balance']}")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Chat simple avec Cloudya AI")
    parser.add_argument("--api-url", help="URL de l'API")
    parser.add_argument("-e", "--execute", action="store_true", help="Mode exécution")
    args = parser.parse_args()
    
    config = get_config()
    api_url = args.api_url or config.get('api', 'url', fallback='https://api.cloudya.ai')
    token = get_token()
    
    print("╔══════════════════════════════════════╗")
    print("║           CLOUDYA AI CHAT            ║")
    print("╚══════════════════════════════════════╝")
    print(f"🌐 API: {api_url}")
    print("💡 Tapez 'quit', 'exit' ou 'q' pour quitter")
    print("🔄 Tapez 'clear' pour effacer l'écran")
    print()
    
    if not token:
        print("⚠️  Vous n'êtes pas connecté!")
        print("   Utilisez: cloudya login")
        return 1
    
    conversation_history = []
    
    while True:
        try:
            # Saisie utilisateur
            user_input = input("🧑 Vous: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Au revoir!")
                break
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            if not user_input:
                continue
            
            # Ajouter à l'historique
            conversation_history.append({"role": "user", "content": user_input})
            
            print("\n🤔 Cloudya réfléchit...")
            
            # Requête API
            try:
                execution_mode = "supervised" if args.execute else "dry_run"
                response = requests.post(
                    f"{api_url}/api/command",
                    json={"user_input": user_input, "execution_mode": execution_mode},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Formater et afficher la réponse
                    formatted_response = format_response(data)
                    print(f"\n{formatted_response}")
                    
                    # Ajouter à l'historique
                    conversation_history.append({"role": "assistant", "content": formatted_response})
                    
                else:
                    print(f"\n❌ Erreur {response.status_code}: {response.text}")
                    if response.status_code == 401:
                        print("🔑 Votre session a expiré. Reconnectez-vous avec: cloudya login")
            
            except requests.exceptions.ConnectionError:
                print(f"\n🔌 Erreur de connexion à {api_url}")
                print("Vérifiez que le serveur est accessible.")
            except requests.exceptions.Timeout:
                print("\n⏱️  Timeout: La requête a pris trop de temps")
            except Exception as e:
                print(f"\n⚠️  Erreur: {e}")
            
            print("\n" + "─" * 60 + "\n")
        
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\n📝 Conversation terminée.")
    
    # Optionnel: sauvegarder l'historique
    if conversation_history:
        try:
            history_file = CONFIG_DIR / f"chat_history_{int(time.time())}.json"
            with open(history_file, 'w') as f:
                json.dump(conversation_history, f, indent=2)
            print(f"💾 Historique sauvegardé: {history_file}")
        except Exception:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())