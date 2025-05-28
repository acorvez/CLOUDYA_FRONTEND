#!/usr/bin/env python3
import argparse
import requests
import os
import sys
import json
import configparser
from pathlib import Path
import asyncio
import time
from datetime import datetime

# Bibliothèques pour le TUI
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, Log
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from textual import work
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.console import Console
from rich.syntax import Syntax

# Configuration
CONFIG_DIR = Path.home() / ".cloudya"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def get_config():
    """Charge la configuration"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    else:
        # Créer une config par défaut
        config['api'] = {'url': 'https://api.cloudya.ai'}
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
    
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

class UserMessage(Static):
    """Widget pour afficher un message utilisateur"""
    
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        yield Static(Panel(self.message, title="Vous", border_style="green"))

class AssistantMessage(Static):
    """Widget pour afficher un message de l'assistant"""
    
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        # Traiter le contenu pour afficher du code correctement
        content = self.message
        
        # Essayer de parser comme markdown
        try:
            md = Markdown(content)
            yield Static(Panel(md, title="Cloudya AI", border_style="blue"))
        except Exception:
            yield Static(Panel(content, title="Cloudya AI", border_style="blue"))

class CodeSnippet(Static):
    """Widget pour afficher un snippet de code"""
    
    def __init__(self, code: str, language: str = ""):
        super().__init__()
        self.code = code
        self.language = language
    
    def compose(self) -> ComposeResult:
        try:
            syntax = Syntax(self.code, self.language, theme="monokai", line_numbers=True)
            yield Static(Panel(syntax, title=f"Code {self.language}", border_style="yellow"))
        except Exception:
            # Fallback si la coloration syntaxique échoue
            yield Static(Panel(self.code, title=f"Code {self.language}", border_style="yellow"))

class CommandResult(Static):
    """Widget pour afficher le résultat d'une commande"""
    
    def __init__(self, result: str):
        super().__init__()
        self.result = result
    
    def compose(self) -> ComposeResult:
        yield Static(Panel(self.result, title="Résultat", border_style="cyan"))

class SystemMessage(Static):
    """Widget pour afficher un message système"""
    
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def compose(self) -> ComposeResult:
        # Utiliser une couleur valide au lieu de "gray"
        text = Text(self.message, style="dim")
        yield Static(Panel(text, title="Système", border_style="white"))

class CloudyaChatApp(App):
    """Application TUI pour le chat Cloudya"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #chat-container {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
        border: solid $primary;
    }
    
    #input-container {
        height: 5;
        padding: 1;
        background: $panel;
        border-top: solid $primary;
    }
    
    #status-bar {
        height: 1;
        background: $primary-darken-1;
        color: $text;
        text-align: center;
        padding: 0 1;
    }
    
    #user-input {
        border: solid $accent;
        background: $surface;
        color: $text;
        padding: 0 1;
        height: 3;
    }
    
    #user-input:focus {
        border: solid $accent-lighten-2;
        background: $surface-lighten-1;
    }
    
    UserMessage {
        margin: 1 0;
    }
    
    AssistantMessage {
        margin: 1 0;
    }
    
    SystemMessage {
        margin: 1 0;
    }
    
    CodeSnippet {
        margin: 1 0;
    }
    
    CommandResult {
        margin: 1 0;
    }
    
    Header {
        background: $primary-darken-2;
    }
    
    Footer {
        background: $primary-darken-2;
    }
    """
    
    TITLE = "Cloudya AI Chat"
    SUB_TITLE = "Assistant d'infrastructure cloud"
    BINDINGS = [
        ("ctrl+c", "quit", "Quitter"),
        ("ctrl+l", "clear_chat", "Effacer"),
        ("escape", "focus_input", "Focus Input"),
    ]
    
    def __init__(self, api_url: str = None, execute_mode: bool = False):
        super().__init__()
        self.token = get_token()
        config = get_config()
        self.api_url = api_url or config.get('api', 'url', fallback='https://api.cloudya.ai')
        self.execute_mode = execute_mode
        self.history = []
        self.status = "Prêt"
        
        # Vérifier si l'utilisateur est connecté
        if not self.token:
            self.status = "Non connecté. Exécutez 'cloudya login' pour vous connecter."
    
    def compose(self) -> ComposeResult:
        """Compose l'interface de l'application"""
        yield Header()
        
        with Vertical():
            with Container(id="chat-container"):
                # Message de bienvenue
                yield SystemMessage("Bienvenue dans le chat Cloudya! Posez vos questions sur l'infrastructure cloud.")
                
                if not self.token:
                    yield SystemMessage("⚠️ Vous n'êtes pas connecté. Exécutez 'cloudya login' pour vous connecter.")
            
            with Container(id="input-container"):
                yield Input(
                    placeholder="Tapez votre message ici... (Entrée pour envoyer)",
                    id="user-input"
                )
            
            with Container(id="status-bar"):
                yield Static(self.status, id="status")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Appelé lorsque l'application est montée"""
        # Focus sur le champ de saisie après un petit délai
        self.set_timer(0.1, self.focus_input)
    
    def focus_input(self) -> None:
        """Met le focus sur le champ de saisie"""
        try:
            input_field = self.query_one("#user-input", Input)
            input_field.focus()
        except Exception:
            pass
    
    def action_focus_input(self) -> None:
        """Action pour mettre le focus sur l'input"""
        self.focus_input()
    
    def action_clear_chat(self) -> None:
        """Action pour effacer le chat"""
        chat = self.query_one("#chat-container")
        chat.remove_children()
        chat.mount(SystemMessage("Chat effacé. Nouvelle conversation démarrée."))
        self.query_one("#status").update("Prêt")
        self.focus_input()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Appelé lorsque l'utilisateur soumet un message"""
        if not event.value.strip():
            return
        
        user_input = event.value
        input_field = self.query_one("#user-input", Input)
        input_field.value = ""
        
        # Remettre le focus sur l'input
        input_field.focus()
        
        # Afficher le message utilisateur
        chat = self.query_one("#chat-container")
        chat.mount(UserMessage(user_input))
        
        # Scroll vers le bas pour voir le nouveau message
        chat.scroll_end(animate=False)
        
        # Mettre à jour le statut
        self.query_one("#status").update("Traitement en cours...")
        
        # Si l'utilisateur n'est pas connecté, afficher un message
        if not self.token:
            chat.mount(SystemMessage("⚠️ Vous n'êtes pas connecté. Exécutez 'cloudya login' pour vous connecter."))
            self.query_one("#status").update("Non connecté")
            chat.scroll_end(animate=False)
            return
        
        # Envoyer la requête à l'API - correction ici
        self._send_message(user_input)
    
    @work(exclusive=False)
    async def _send_message(self, message: str) -> None:
        """Envoie un message à l'API et affiche la réponse"""
        chat = self.query_one("#chat-container")
        
        # Préparer la requête
        execution_mode = "supervised" if self.execute_mode else "dry_run"
        
        try:
            # Simuler un délai de réseau pour l'animation de "en train d'écrire"
            await self._simulate_typing()
            
            # Faire la requête à l'API (utilisation de requests en mode synchrone dans un executor)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    f"{self.api_url}/api/command",
                    json={"user_input": message, "execution_mode": execution_mode},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=30  # Timeout de 30 secondes
                )
            )
            
            # Traiter la réponse
            if response.status_code == 200:
                data = response.json()
                
                # Afficher l'explication générale
                if "explanation" in data and data["explanation"]:
                    await self.call_from_thread(chat.mount, AssistantMessage(data["explanation"]))
                
                # Afficher la commande générée
                if "action" in data and data["action"]:
                    command = data["action"]
                    
                    # Détecter le langage pour la coloration syntaxique
                    if command.startswith("aws ") or command.startswith("kubectl "):
                        language = "bash"
                    elif "terraform" in command.lower():
                        language = "hcl"
                    elif command.startswith("docker "):
                        language = "dockerfile"
                    else:
                        language = "bash"  # Par défaut
                    
                    await self.call_from_thread(chat.mount, CodeSnippet(command, language))
                
                # Afficher le résultat d'exécution si disponible
                if "output" in data and data["output"]:
                    await self.call_from_thread(chat.mount, CommandResult(data["output"]))
                
                # Afficher les informations d'utilisation des tokens
                if "token_usage" in data:
                    token_info = f"Tokens utilisés: {data['token_usage'].get('total_tokens', 0)}"
                    if "remaining_balance" in data["token_usage"]:
                        token_info += f" | Solde restant: {data['token_usage']['remaining_balance']}"
                    
                    await self.call_from_thread(self.query_one("#status").update, token_info)
                else:
                    await self.call_from_thread(self.query_one("#status").update, "Prêt")
            else:
                # En cas d'erreur
                error_message = f"Erreur {response.status_code}: {response.text}"
                await self.call_from_thread(chat.mount, SystemMessage(f"⚠️ {error_message}"))
                
                # Si non autorisé, suggérer de se connecter
                if response.status_code == 401:
                    await self.call_from_thread(chat.mount, SystemMessage("Votre session a expiré. Exécutez 'cloudya login' pour vous reconnecter."))
                
                await self.call_from_thread(self.query_one("#status").update, "Erreur")
        
        except requests.exceptions.Timeout:
            await self.call_from_thread(chat.mount, SystemMessage("⚠️ Timeout: La requête a pris trop de temps"))
            await self.call_from_thread(self.query_one("#status").update, "Timeout")
        except requests.exceptions.ConnectionError:
            await self.call_from_thread(chat.mount, SystemMessage(f"⚠️ Erreur de connexion: impossible de se connecter à {self.api_url}"))
            await self.call_from_thread(self.query_one("#status").update, "Erreur de connexion")
        except Exception as e:
            # En cas d'exception
            await self.call_from_thread(chat.mount, SystemMessage(f"⚠️ Erreur: {str(e)}"))
            await self.call_from_thread(self.query_one("#status").update, "Erreur")
        
        # Scroll vers le bas pour voir la réponse
        await self.call_from_thread(chat.scroll_end, animate=False)
        
        # Remettre le focus sur l'input
        await self.call_from_thread(self.focus_input)
    
    async def _simulate_typing(self) -> None:
        """Simule l'animation de frappe"""
        status = self.query_one("#status")
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        for i in range(5):  # Durée de l'animation
            for dot in dots:
                await self.call_from_thread(status.update, f"Cloudya réfléchit {dot}")
                await asyncio.sleep(0.1)

def main():
    # Définir les arguments de la commande
    parser = argparse.ArgumentParser(description="Discuter avec l'assistant Cloudya via une interface TUI")
    parser.add_argument("--api-url", help="URL de l'API Cloudya (par défaut: depuis la configuration)")
    parser.add_argument("-e", "--execute", action="store_true", help="Exécuter les commandes générées")
    args = parser.parse_args()
    
    # Vérifier que les bibliothèques nécessaires sont installées
    try:
        import textual
        import rich
    except ImportError as e:
        print(f"Erreur: Bibliothèque manquante - {e}")
        print("Installez les dépendances avec:")
        print("  pip install textual rich")
        return 1
    
    # Obtenir l'URL de l'API
    config = get_config()
    api_url = args.api_url or config.get('api', 'url', fallback='https://api.cloudya.ai')
    
    # Obtenir le token
    token = get_token()
    if not token:
        print("Note: Vous n'êtes pas connecté à Cloudya.")
        print("Vous pouvez quand même lancer le chat, mais vous devrez vous connecter.")
        print("Utilisez 'cloudya login' pour vous connecter.")
        print("\nLancement du chat dans 3 secondes...")
        import time
        time.sleep(3)
    
    try:
        # Lancer l'application TUI
        app = CloudyaChatApp(api_url=api_url, execute_mode=args.execute)
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\nChat fermé.")
        return 0
    except Exception as e:
        print(f"Erreur lors du lancement du chat: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())