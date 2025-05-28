#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def monitor_api():
    """Surveille l'activité de l'API"""
    print("🔍 Monitoring de l'API Cloudya de test")
    print("Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        while True:
            try:
                # Vérifier la santé
                start_time = time.time()
                response = requests.get(f"{API_URL}/health")
                response_time = (time.time() - start_time) * 1000
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if response.status_code == 200:
                    print(f"[{timestamp}] ✅ API OK - {response_time:.1f}ms")
                else:
                    print(f"[{timestamp}] ❌ API ERROR {response.status_code}")
                
            except requests.exceptions.ConnectionError:
                print(f"[{timestamp}] 🔌 Connexion échouée")
            except Exception as e:
                print(f"[{timestamp}] ⚠️  Erreur: {e}")
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n👋 Monitoring arrêté")

if __name__ == "__main__":
    monitor_api()