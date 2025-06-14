#!/usr/bin/env python3
"""
Script pour corriger automatiquement le fichier chat.py
"""

import re
import os
import sys
from pathlib import Path

def patch_chat_file(file_path):
    """Applique les corrections au fichier chat.py"""
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return False
    
    print(f"🔧 Correction du fichier: {file_path}")
    
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Corriger le décorateur @work pour ajouter thread=True
    content = re.sub(
        r'@work\(exclusive=False\)\s*\n\s*async def _send_message',
        '@work(exclusive=False, thread=True)\n    def _send_message',
        content
    )
    
    # 2. Supprimer 'async' de la définition de _send_message
    content = re.sub(
        r'def _send_message\(self, message: str\) -> None:',
        'def _send_message(self, message: str) -> None:',
        content
    )
    
    # 3. Supprimer l'appel à _simulate_typing
    content = re.sub(
        r'\s*# Simuler un délai de réseau pour l\'animation de "en train d\'écrire"\s*\n\s*await self\._simulate_typing\(\)\s*\n',
        '\n            # Animation de typing\n            self._animate_typing()\n',
        content
    )
    
    # 4. Remplacer tous les 'await self.call_from_thread' par 'self.call_from_thread'
    content = re.sub(
        r'await self\.call_from_thread\(',
        'self.call_from_thread(',
        content
    )
    
    # 5. Supprimer la fonction _simulate_typing async et la remplacer
    simulate_typing_pattern = r'async def _simulate_typing\(self\) -> None:.*?await asyncio\.sleep\(0\.1\)'
    
    new_animate_typing = '''def _animate_typing(self) -> None:
        """Simule l'animation de frappe (version synchrone pour thread)"""
        status = self.query_one("#status")
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        for i in range(3):  # Durée de l'animation réduite
            for dot in dots[:3]:  # Moins de dots pour aller plus vite
                self.call_from_thread(status.update, f"Cloudya réfléchit {dot}")
                time.sleep(0.1)  # time.sleep synchrone au lieu d'asyncio.sleep'''
    
    content = re.sub(simulate_typing_pattern, new_animate_typing, content, flags=re.DOTALL)
    
    # 6. Supprimer les imports asyncio inutiles dans la fonction _send_message
    content = re.sub(
        r'\s*# Faire la requête à l\'API \(utilisation de requests en mode synchrone dans u.*?\n\s*loop = asyncio\.get_event_loop\(\)\s*\n\s*response = await loop\.run_in_executor\(\s*\n\s*None,\s*\n\s*lambda: requests\.post\(',
        '\n            # Faire la requête à l\'API\n            response = requests.post(',
        content,
        flags=re.DOTALL
    )
    
    # 7. Corriger la partie requests.post pour être synchrone
    content = re.sub(
        r'response = requests\.post\(\s*\n\s*f"\{self\.api_url\}/api/command",\s*\n\s*json=\{"user_input": message, "execution_mode": execution_mode\},\s*\n\s*headers=\{"Authorization": f"Bearer \{self\.token\}"\},\s*\n\s*timeout=30  # Timeout de 30 secondes\s*\n\s*\)',
        '''response = requests.post(
                f"{self.api_url}/api/command",
                json={"user_input": message, "execution_mode": execution_mode},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30  # Timeout de 30 secondes
            )''',
        content
    )
    
    # 8. Ajouter l'import time si nécessaire
    if 'import time' not in content:
        content = re.sub(
            r'(import asyncio\s*\n)',
            r'\1import time\n',
            content
        )
    
    # Créer une sauvegarde
    backup_path = file_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(open(file_path, 'r', encoding='utf-8').read())
    print(f"💾 Sauvegarde créée: {backup_path}")
    
    # Sauvegarder le fichier corrigé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fichier corrigé avec succès!")
    return True

def main():
    # Chemin vers le fichier chat.py
    chat_file = Path("/home/adrien/cloudya/commands/chat.py")
    
    if not chat_file.exists():
        print(f"❌ Fichier non trouvé: {chat_file}")
        print("Vérifiez le chemin vers votre fichier chat.py")
        return 1
    
    print("🔧 Correction automatique du fichier chat.py")
    print(f"Fichier: {chat_file}")
    
    if patch_chat_file(chat_file):
        print("\n✅ Correction terminée!")
        print("📝 Prochaines étapes:")
        print("1. Testez le chat: cloudya chat")
        print("2. Si problème, restaurez: cp chat.py.backup chat.py")
        return 0
    else:
        print("\n❌ Erreur lors de la correction")
        return 1

if __name__ == "__main__":
    sys.exit(main())
