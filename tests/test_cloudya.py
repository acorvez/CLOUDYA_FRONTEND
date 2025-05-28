#!/usr/bin/env python3
import requests
import json
import time
import subprocess
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TEST_TOKEN = "test-token-123456789"

def test_server_running():
    """Teste si le serveur est en marche"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_login():
    """Teste la connexion"""
    response = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    
    return response.status_code == 200 and "token" in response.json()

def test_command_request():
    """Teste une requête de commande"""
    response = requests.post(
        f"{API_URL}/api/command",
        json={"user_input": "Créer un cluster Kubernetes", "execution_mode": "dry_run"},
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return "action" in data and "explanation" in data
    return False

def test_token_info():
    """Teste la récupération d'infos du token"""
    response = requests.get(
        f"{API_URL}/api/tokens/info",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    return response.status_code == 200 and "remaining_tokens" in response.json()

def run_cli_test():
    """Teste la CLI avec le serveur local"""
    try:
        # Tester la commande ask
        result = subprocess.run([
            sys.executable, "-m", "cloudya.commands.ask", 
            "Déployer une application sur AWS"
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0
    except:
        return False

def main():
    print("🧪 Tests de Cloudya en local")
    print("=" * 40)
    
    tests = [
        ("Serveur en marche", test_server_running),
        ("Login", test_login),
        ("Requête de commande", test_command_request),
        ("Info du token", test_token_info),
        ("CLI", run_cli_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔍 Test: {test_name}... ", end="")
        try:
            result = test_func()
            if result:
                print("✅ PASSÉ")
                results.append(True)
            else:
                print("❌ ÉCHOUÉ")
                results.append(False)
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            results.append(False)
        
        time.sleep(0.5)
    
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        return 0
    else:
        print("⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())