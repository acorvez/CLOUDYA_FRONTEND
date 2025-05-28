#!/usr/bin/env python3
"""
Serveur de test simple pour Cloudya sans dépendances externes complexes
"""
import json
import http.server
import socketserver
import urllib.parse
import random
import threading
import time
from datetime import datetime

PORT = 8000

# Réponses mockées
MOCK_RESPONSES = {
    "aws": {
        "explanation": "Pour AWS, je recommande d'utiliser AWS CLI avec les bonnes pratiques de sécurité.",
        "action": "aws s3 mb s3://my-test-bucket --region eu-west-3",
    },
    "kubernetes": {
        "explanation": "Kubernetes permet d'orchestrer vos conteneurs. Voici un déploiement basique.",
        "action": "kubectl create deployment nginx --image=nginx:latest\nkubectl expose deployment nginx --port=80 --type=LoadBalancer",
    },
    "terraform": {
        "explanation": "Terraform pour l'infrastructure as code.",
        "action": 'resource "aws_instance" "web" {\n  ami           = "ami-0c55b159cbfafe1f0"\n  instance_type = "t2.micro"\n}',
    },
    "docker": {
        "explanation": "Docker pour conteneuriser vos applications.",
        "action": "docker build -t myapp .\ndocker run -d -p 8080:80 myapp",
    }
}

def find_response(query):
    """Trouve une réponse basée sur les mots-clés"""
    query_lower = query.lower()
    
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in query_lower:
            return response
    
    return {
        "explanation": f"Voici une suggestion pour votre demande: '{query}'",
        "action": f"echo 'Commande suggérée pour: {query}'",
    }

class CloudyaTestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_json_response({"status": "ok"})
        elif self.path == '/api/tokens/info':
            if self.check_auth():
                self.send_json_response({
                    "user_id": "test-user",
                    "email": "test@example.com",
                    "plan": "pro",
                    "remaining_tokens": random.randint(5000, 10000),
                    "expiry": "2024-12-31T23:59:59",
                    "daily_trend": [
                        {"date": "2024-05-20", "tokens": 250},
                        {"date": "2024-05-21", "tokens": 180},
                        {"date": "2024-05-22", "tokens": 320}
                    ]
                })
            else:
                self.send_error_response(401, "Token requis")
        elif self.path == '/':
            self.send_json_response({
                "message": "Cloudya Test Server",
                "version": "1.0.0",
                "status": "running"
            })
        else:
            self.send_error_response(404, "Not found")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            self.send_error_response(400, "Invalid JSON")
            return
        
        if self.path == '/api/auth/login':
            if data.get('email') and data.get('password'):
                self.send_json_response({
                    "token": "test-token-123456789",
                    "user_id": "test-user",
                    "email": data.get('email')
                })
            else:
                self.send_error_response(400, "Email et mot de passe requis")
        
        elif self.path == '/api/command':
            if not self.check_auth():
                self.send_error_response(401, "Token requis")
                return
            
            user_input = data.get('user_input', '')
            execution_mode = data.get('execution_mode', 'dry_run')
            
            # Simuler un délai
            time.sleep(random.uniform(0.5, 1.5))
            
            mock_response = find_response(user_input)
            
            response = {
                "action": mock_response["action"],
                "explanation": mock_response["explanation"],
                "execution_status": execution_mode,
                "token_usage": {
                    "prompt_tokens": random.randint(50, 100),
                    "completion_tokens": random.randint(100, 200),
                    "total_tokens": random.randint(150, 300),
                    "remaining_balance": random.randint(5000, 10000)
                }
            }
            
            if execution_mode == "supervised":
                response["output"] = f"[SIMULATION] Commande exécutée:\n{mock_response['action']}\n\nRésultat: Opération terminée avec succès"
            
            self.send_json_response(response)
        
        else:
            self.send_error_response(404, "Not found")
    
    def check_auth(self):
        """Vérifie l'authentification"""
        auth_header = self.headers.get('Authorization')
        return auth_header and auth_header.startswith('Bearer ')
    
    def send_json_response(self, data, status=200):
        """Envoie une réponse JSON"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def send_error_response(self, status, message):
        """Envoie une réponse d'erreur"""
        self.send_json_response({"error": message}, status)
    
    def do_OPTIONS(self):
        """Gère les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log des requêtes"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {format % args}")

def start_server():
    """Démarre le serveur de test"""
    with socketserver.TCPServer(("", PORT), CloudyaTestHandler) as httpd:
        print(f"🚀 Serveur de test Cloudya démarré sur http://localhost:{PORT}")
        print(f"📚 Endpoints disponibles:")
        print(f"   GET  /health - Vérification de santé")
        print(f"   POST /api/auth/login - Connexion")
        print(f"   POST /api/command - Commandes")
        print(f"   GET  /api/tokens/info - Info token")
        print(f"🔧 Configurez votre CLI avec: cloudya configure --api-url http://localhost:{PORT}")
        print("🔴 Appuyez sur Ctrl+C pour arrêter")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Serveur arrêté")

if __name__ == "__main__":
    start_server()