#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn
import os
import json
import random
import time

# Ajoutez cette section au début de test_server.py
import openai

# Configurez votre clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_REAL_AI = OPENAI_API_KEY is not None

if USE_REAL_AI:
    openai.api_key = OPENAI_API_KEY

async def get_ai_response(user_input: str):
    """Obtient une réponse de l'IA réelle ou simulée"""
    if USE_REAL_AI:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en infrastructure cloud."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return {
                "explanation": response.choices[0].message.content,
                "action": "# Commande générée par IA\necho 'Commande adaptée à votre demande'",
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            print(f"Erreur OpenAI: {e}")
            return find_mock_response(user_input)
    else:
        return find_mock_response(user_input)

# Puis modifiez l'endpoint /api/command pour utiliser cette fonction

app = FastAPI(title="Cloudya Test Server")

# Modèles de données
class CommandRequest(BaseModel):
    user_input: str
    execution_mode: str = "dry_run"

class CommandResponse(BaseModel):
    action: str
    explanation: str
    output: str = None
    execution_status: str
    token_usage: dict

# Base de réponses simulées pour les tests
MOCK_RESPONSES = {
    "aws": {
        "explanation": "Pour déployer sur AWS, je recommande d'utiliser AWS CLI avec les bonnes pratiques de sécurité.",
        "action": "aws s3 mb s3://my-test-bucket --region eu-west-3",
        "tokens": 150
    },
    "kubernetes": {
        "explanation": "Kubernetes permet d'orchestrer vos conteneurs. Voici comment créer un déploiement basique.",
        "action": "kubectl create deployment nginx --image=nginx:latest\nkubectl expose deployment nginx --port=80 --type=LoadBalancer",
        "tokens": 200
    },
    "terraform": {
        "explanation": "Terraform vous permet de gérer votre infrastructure comme du code. Voici un exemple de configuration.",
        "action": """resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "HelloWorld"
  }
}""",
        "tokens": 180
    },
    "docker": {
        "explanation": "Docker permet de conteneuriser vos applications. Voici comment créer et lancer un conteneur.",
        "action": "docker build -t myapp .\ndocker run -d -p 8080:80 myapp",
        "tokens": 120
    }
}

def find_mock_response(query: str):
    """Trouve une réponse simulée basée sur les mots-clés"""
    query_lower = query.lower()
    
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in query_lower:
            return response
    
    # Réponse par défaut
    return {
        "explanation": f"Je vais vous aider avec '{query}'. Voici une suggestion générique pour votre demande d'infrastructure cloud.",
        "action": f"# Commande suggérée pour: {query}\necho 'Cette commande serait adaptée à votre demande spécifique'",
        "tokens": 100
    }

@app.post("/api/command", response_model=CommandResponse)
async def handle_command(
    request: CommandRequest,
    authorization: str = Header(None)
):
    # Simuler une vérification d'authentification
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token d'authentification requis")
    
    # Simuler un délai de traitement
    time.sleep(random.uniform(0.5, 2.0))
    
    # Trouver une réponse appropriée
    mock_response = find_mock_response(request.user_input)
    
    # Construire la réponse
    response = CommandResponse(
        action=mock_response["action"],
        explanation=mock_response["explanation"],
        execution_status=request.execution_mode,
        token_usage={
            "prompt_tokens": random.randint(50, 100),
            "completion_tokens": random.randint(100, 200),
            "total_tokens": mock_response["tokens"],
            "remaining_balance": random.randint(5000, 10000)
        }
    )
    
    # Simuler l'exécution si demandée
    if request.execution_mode == "supervised":
        response.output = f"[SIMULATION] Commande exécutée avec succès:\n{mock_response['action']}\n\nRésultat: Opération terminée"
    
    return response

@app.post("/api/auth/login")
async def login(credentials: dict):
    """Endpoint de connexion simulé"""
    email = credentials.get("email")
    password = credentials.get("password")
    
    # Accepter n'importe quels identifiants pour les tests
    if email and password:
        return {
            "token": "test-token-123456789",
            "user_id": "test-user",
            "email": email
        }
    else:
        raise HTTPException(status_code=400, detail="Email et mot de passe requis")

@app.get("/api/tokens/info")
async def token_info(authorization: str = Header(None)):
    """Informations sur le token simulées"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requis")
    
    return {
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
    }

@app.get("/health")
async def health_check():
    """Endpoint de santé"""
    return {"status": "ok", "message": "Cloudya Test Server is running"}

@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "message": "Cloudya Test Server",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/command - Envoyer une commande",
            "POST /api/auth/login - Se connecter",
            "GET /api/tokens/info - Info du token",
            "GET /health - Vérification de santé"
        ]
    }

if __name__ == "__main__":
    print("🚀 Démarrage du serveur de test Cloudya...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔧 Pour tester: cloudya configure --api-url http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)