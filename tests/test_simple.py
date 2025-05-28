#!/usr/bin/env python3
import requests
import time
import sys
import subprocess
import threading
from pathlib import Path

API_URL = "http://localhost:8000"

def wait_for_server(max_attempts=10):
    """Attend que le serveur soit prêt"""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_api():
    """Tests de l'API"""
    print("🧪 Tests de l'API Cloudya")
    print("=" * 30)
    
    # Test 1: Santé du serveur
    print("🔍 Test santé du serveur... ", end="")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅")
        else:
            print("❌")
            return False
    except:
        print("❌")
        return False
    
    # Test 2: Login
    print("🔍 Test login... ", end="")
    try:
        response = requests.post(f"{API_URL}/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpass"
        })
        if response.status_code == 200 and "token" in response.json():
            print("✅")
            token = response.json()["token"]
        else:
            print("❌")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False
    
    # Test 3: Commande
    print("🔍 Test commande... ", end="")
    try:
        response = requests.post(f"{API_URL}/api/command", 
            json={"user_input": "Créer un bucket S3", "execution_mode": "dry_run"},
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "action" in data and "explanation" in data:
                print("✅")
            else:
                print("❌")
                return False
        else:
            print("❌")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False
    
    # Test 4: Info token
    print("🔍 Test info token... ", end="")
    try:
        response = requests.get(f"{API_URL}/api/tokens/info",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200 and "remaining_tokens" in response.json():
            print("✅")
        else:
            print("❌")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False
    
    print("\n🎉 Tous les tests sont passés!")
    return True

def main():
    print("🔍 Vérification du serveur...")
    if not wait_for_server():
        print("❌ Le serveur n'est pas accessible")
        print("Démarrez d'abord le serveur avec: python simple_test_server.py")
        return 1
    
    if test_api():
        print("\n💡 Vous pouvez maintenant tester:")
        print("   cloudya configure --api-url http://localhost:8000")
        print("   cloudya login")  # email: test@example.com, pass: n'importe quoi
        print("   cloudya ask 'Créer un cluster Kubernetes'")
        print("   cloudya chat")
        return 0
    else:
        print("\n❌ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())