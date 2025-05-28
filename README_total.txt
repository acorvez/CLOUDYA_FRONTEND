# api/routes/commands.py - Route principale IA
from fastapi import APIRouter, Depends, HTTPException, Request
from api.models.requests import CommandRequest
from api.models.responses import CommandResponse
from api.middleware.auth import get_current_user
from ai.core.ai_engine import AIEngine
import time
import structlog

router = APIRouter()
logger = structlog.get_logger()

@router.post("/", response_model=CommandResponse)
async def process_command(
    request: CommandRequest,
    http_request: Request,
    current_user = Depends(get_current_user)
):
    """
    Traite une commande utilisateur avec l'IA
    Point d'entrée principal de l'API
    """
    start_time = time.time()

    try:
        logger.info(
            "Traitement commande IA",
            user_id=current_user["id"],
            user_input=request.user_input[:100],  # Log partiel pour la sécurité
            execution_mode=request.execution_mode
        )

        # Initialiser le moteur IA
        ai_engine = AIEngine()

        # Traiter la commande
        result = await ai_engine.process_command(
            user_input=request.user_input,
            execution_mode=request.execution_mode,
            user_tier=current_user["tier"],
            user_id=current_user["id"],
            context=request.context or {}
        )

        processing_time = time.time() - start_time
        result["processing_time"] = processing_time

        logger.info(
            "Commande traitée avec succès",
            user_id=current_user["id"],
            processing_time=processing_time,
            tokens_used=result["token_usage"]["total_tokens"]
        )

        return result

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Erreur traitement commande",
            user_id=current_user["id"],
            error=str(e),
            processing_time=processing_time
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la commande: {str(e)}"
        )

@router.get("/providers")
async def list_providers(current_user = Depends(get_current_user)):
    """Liste les providers IA disponibles selon l'abonnement utilisateur"""

    user_tier = current_user["tier"]

    providers = {
        "free": [
            {"name": "ollama", "model": "llama3.1:8b", "description": "Modèle local gratuit"}
        ],
        "starter": [
            {"name": "openai", "model": "gpt-4o-mini", "description": "GPT-4o Mini optimisé"},
            {"name": "ollama", "model": "llama3.1:8b", "description": "Modèle local gratuit"}
        ],
        "pro": [
            {"name": "anthropic", "model": "claude-3-5-sonnet", "description": "Claude 3.5 Sonnet premium"},
            {"name": "openai", "model": "gpt-4o", "description": "GPT-4o complet"},
            {"name": "openai", "model": "gpt-4o-mini", "description": "GPT-4o Mini optimisé"}
        ],
        "enterprise": [
            {"name": "anthropic", "model": "claude-3-5-sonnet", "description": "Claude 3.5 Sonnet premium"},
            {"name": "openai", "model": "gpt-4o", "description": "GPT-4o complet"},
            {"name": "openai", "model": "gpt-4o-mini", "description": "GPT-4o Mini optimisé"}
        ]
    }

    return {
        "user_tier": user_tier,
        "available_providers": providers.get(user_tier, providers["free"])
    }

# ===== api/routes/auth.py - Authentification =====
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from api.models.requests import LoginRequest, RegisterRequest
from api.models.responses import AuthResponse, UserInfo
from api.database import get_db
from api.models.database import User
from config.settings import settings

router = APIRouter()

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""

    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )

    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(request.password)

    new_user = User(
        email=request.email,
        name=request.name,
        hashed_password=hashed_password,
        tier="free",  # Commencer avec le plan gratuit
        token_balance=1000,  # 1000 tokens gratuits
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),
            "email": new_user.email,
            "tier": new_user.tier
        },
        expires_delta=access_token_expires
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "tier": new_user.tier
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur existant"""

    # Trouver l'utilisateur
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé"
        )

    # Mettre à jour la dernière connexion
    user.last_login = datetime.utcnow()
    db.commit()

    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "tier": user.tier
        },
        expires_delta=access_token_expires
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "tier": user.tier
        }
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Informations sur l'utilisateur actuel"""

    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return UserInfo(
        id=user.id,
        email=user.email,
        name=user.name,
        tier=user.tier,
        created_at=user.created_at,
        token_balance=user.token_balance,
        subscription_status=user.subscription_status or "free"
    )

# ===== api/routes/tokens.py - Gestion des tokens =====
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.models.database import User, TokenUsage
from api.middleware.auth import get_current_user
import structlog

router = APIRouter()
logger = structlog.get_logger()

@router.get("/info")
async def get_token_info(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Informations sur les tokens de l'utilisateur"""

    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Statistiques d'usage du mois en cours
    from datetime import datetime, timedelta
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_usage = db.query(TokenUsage).filter(
        TokenUsage.user_id == user.id,
        TokenUsage.timestamp >= start_of_month
    ).all()

    total_used_this_month = sum(usage.tokens_used for usage in monthly_usage)

    return {
        "user_id": user.id,
        "email": user.email,
        "plan": user.tier,
        "remaining_tokens": user.token_balance,
        "tokens_used_this_month": total_used_this_month,
        "subscription_status": user.subscription_status or "free",
        "daily_trend": [
            {
                "date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "tokens": sum(u.tokens_used for u in monthly_usage 
                             if u.timestamp.date() == (datetime.utcnow() - timedelta(days=i)).date())
            }
            for i in range(7)  # 7 derniers jours
        ]
    }

# ===== api/models/database.py - Modèles SQLAlchemy =====
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    tablename = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Abonnement
    tier = Column(String, default="free")  # free, starter, pro, enterprise
    token_balance = Column(Integer, default=1000)
    subscription_status = Column(String, default="free")

    # Métadonnées
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relations
    token_usages = relationship("TokenUsage", back_populates="user")
    ai_requests = relationship("AIRequest", back_populates="user")

class TokenUsage(Base):
    tablename = "token_usages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    tokens_used = Column(Integer, nullable=False)
    cost_credits = Column(Integer, default=0)
    action_type = Column(String, default="ai_command")  # ai_command, api_call

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="token_usages")

class AIRequest(Base):
    tablename = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Requête
    user_input = Column(Text, nullable=False)
    execution_mode = Column(String, default="dry_run")
    context = Column(Text)  # JSON string

    # Réponse IA
    generated_command = Column(Text)
    explanation = Column(Text)
    provider_used = Column(String)
    model_used = Column(String)

    # Métriques
    processing_time = Column(Float)
    tokens_used = Column(Integer)
    cost_credits = Column(Integer)

    # Sécurité
    security_level = Column(String)  # safe, warning, dangerous, forbidden
    was_executed = Column(Boolean, default=False)
    execution_output = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="ai_requests")

class Subscription(Base):
    tablename = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Stripe
    stripe_subscription_id = Column(String)
    stripe_customer_id = Column(String)

    # Plan
    plan_name = Column(String, nullable=False)  # starter, pro, enterprise
    status = Column(String, default="active")  # active, canceled, past_due

    # Dates
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    canceled_at = Column(DateTime)

# ===== api/database.py - Configuration base de données =====
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config.settings import settings
import structlog

logger = structlog.get_logger()

# Création du moteur SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug  # Log SQL en mode debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erreur base de données: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialise la base de données"""
    from api.models.database import Base
    logger.info("Création des tables de base de données...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès!")

# ===== scripts/setup_db.py - Script d'initialisation DB =====
#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(file))))

from api.database import init_db, SessionLocal
from api.models.database import User
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Crée un utilisateur administrateur par défaut"""
    db = SessionLocal()

    try:
        # Vérifier si l'admin existe déjà
        admin = db.query(User).filter(User.email == "admin@cloudya.ai").first()
        if admin:
            print("✅ Utilisateur admin existe déjà")
            return

        # Créer l'admin
        admin_user = User(
            email="admin@cloudya.ai",
            name="Cloudya Admin",
            hashed_password=pwd_context.hash("cloudya2024!"),
            tier="enterprise",
            token_balance=100000,  # 100k tokens pour l'admin
            subscription_status="enterprise",
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(admin_user)
        db.commit()

        print("✅ Utilisateur admin créé:")
        print("   Email: admin@cloudya.ai")
        print("   Password: cloudya2024!")
        print("   Tier: enterprise")

    except Exception as e:
        print(f"❌ Erreur création admin: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🗄️ Initialisation de la base de données Cloudya...")

    # Créer les tables
    init_db()

    # Créer l'utilisateur admin
    create_admin_user()

    print("✅ Base de données initialisée avec succès!")
    print("\n🚀 Prochaines étapes:")
    print("   1. Démarrez les services: docker-compose up -d")
    print("   2. Lancez l'API: uvicorn api.main:app --reload")
    print("   3. Testez: curl http://localhost:8000/health")

if name == "main":
    main()

# ===== alembic.ini - Configuration Alembic =====
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = postgresql://postgres:password@localhost:5432/cloudya

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

Maintenant créons le script d'installation final et le guide de démarrage :

#!/bin/bash
# scripts/quick_start.sh - Installation et démarrage rapide

set -e

echo "🚀 Installation et Démarrage Rapide - Cloudya Backend"
echo "=================================================="

# Vérifications préliminaires
echo "🔍 Vérification des prérequis..."

# Python 3.8+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis. Installez Python 3.8+ et recommencez."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION détecté"

# Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker requis. Installez Docker et recommencez."
    exit 1
fi
echo "✅ Docker détecté"

# Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose requis."
    exit 1
fi
echo "✅ Docker Compose détecté"

echo ""
echo "📦 Installation de l'environnement..."

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "🐍 Création de l'environnement virtuel Python..."
    python3 -m venv venv
else
    echo "✅ Environnement virtuel existant détecté"
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le fichier .env
if [ ! -f ".env" ]; then
    echo "⚙️ Création du fichier de configuration..."
    cp .env.example .env

    # Générer une clé JWT aléatoire
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/your-super-secret-jwt-key-change-in-production/$JWT_SECRET/g" .env

    echo "✅ Fichier .env créé avec clé JWT sécurisée"
else
    echo "✅ Fichier .env existant détecté"
fi

echo ""
echo "🐳 Démarrage des services Docker..."

# Démarrer PostgreSQL, Redis et Ollama
docker-compose up -d postgres redis ollama

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
until docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 2
done
echo "✅ PostgreSQL prêt"

# Attendre que Ollama soit prêt
echo "⏳ Attente d'Ollama..."
sleep 5
until curl -s http://localhost:11434/api/version > /dev/null; do
    sleep 2
done
echo "✅ Ollama prêt"

echo ""
echo "🗄️ Initialisation de la base de données..."

# Initialiser la base de données
python scripts/setup_db.py

echo ""
echo "🤖 Installation du modèle Ollama (peut prendre quelques minutes)..."

# Télécharger le modèle Llama 3.1 8B
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.1:8b"; then
    echo "📥 Téléchargement du modèle Llama 3.1 8B..."
    docker-compose exec ollama ollama pull llama3.1:8b
    echo "✅ Modèle Llama 3.1 8B installé"
else
    echo "✅ Modèle Llama 3.1 8B déjà installé"
fi

echo ""
echo "🧪 Test des services..."

# Test PostgreSQL
if docker-compose exec postgres psql -U postgres -d cloudya -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Connexion OK"
else
    echo "❌ PostgreSQL: Problème de connexion"
fi

# Test Redis
if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis: Connexion OK"
else
    echo "❌ Redis: Problème de connexion"
fi

# Test Ollama
if curl -s http://localhost:11434/api/tags | grep -q "llama3.1"; then
    echo "✅ Ollama: Modèle disponible"
else
    echo "❌ Ollama: Modèle non disponible"
fi

echo ""
echo "🚀 Démarrage de l'API Cloudya..."

# Démarrer l'API en arrière-plan
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > api.log 2>&1 &
API_PID=$!

# Attendre que l'API soit prête
echo "⏳ Attente de l'API..."
sleep 5

# Test de l'API
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API: Démarrée et accessible"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API: Timeout de démarrage"
        echo "📋 Consultez les logs: tail -f api.log"
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!"
echo "====================================="
echo ""
echo "📡 Services disponibles:"
echo "   • API Cloudya:     http://localhost:8000"
echo "   • Documentation:   http://localhost:8000/docs"
echo "   • Health Check:    http://localhost:8000/health"
echo "   • PostgreSQL:      localhost:5432"
echo "   • Redis:           localhost:6379"
echo "   • Ollama:          http://localhost:11434"
echo ""
echo "👤 Compte administrateur créé:"
echo "   • Email:    admin@cloudya.ai"
echo "   • Password: cloudya2024!"
echo "   • Tier:     enterprise"
echo ""
echo "🧪 Tests rapides:"
echo "   curl http://localhost:8000/health"
echo "   curl -X POST http://localhost:8000/api/auth/login \\"
echo "        -H \"Content-Type: application/json\" \\"
echo "        -d '{\"email\":\"admin@cloudya.ai\",\"password\":\"cloudya2024!\"}'"
echo ""
echo "📋 Logs de l'API: tail -f api.log"
echo "🛑 Arrêter tout: ./scripts/stop.sh"
echo ""
echo "🔗 Configuration de votre CLI:"
echo "   cd ../votre-cli-cloudya"
echo "   cloudya configure --api-url http://localhost:8000"
echo "   cloudya login"
echo ""

# Créer le script d'arrêt
cat > scripts/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt des services Cloudya..."

# Arrêter l'API
pkill -f "uvicorn api.main:app" || true

# Arrêter Docker Compose
docker-compose down

echo "✅ Services arrêtés"
EOF

chmod +x scripts/stop.sh

echo "✨ Prêt à utiliser Cloudya Backend!"

# ===== Test automatisé - scripts/test_installation.sh =====
#!/bin/bash
# Test automatisé de l'installation

set -e

echo "🧪 Test automatisé de l'installation Cloudya"
echo "==========================================="

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo "🏥 Test 1: Health Check"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ Health Check: OK"
else
    echo "❌ Health Check: FAILED"
    echo "Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test 2: Login Admin
echo "👤 Test 2: Login Administrateur"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@cloudya.ai","password":"cloudya2024!"}')

if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
    echo "✅ Login Admin: OK"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ Login Admin: FAILED"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 3: Requête IA
echo "🤖 Test 3: Requête IA"
AI_RESPONSE=$(curl -s -X POST "$BASE_URL/api/command/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"user_input":"créer une instance EC2","execution_mode":"dry_run"}')

if echo "$AI_RESPONSE" | grep -q '"action"'; then
    echo "✅ Requête IA: OK"
else
    echo "❌ Requête IA: FAILED"
    echo "Response: $AI_RESPONSE"
    exit 1
fi

# Test 4: Providers disponibles
echo "🔧 Test 4: Providers disponibles"
PROVIDERS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/command/providers" \
    -H "Authorization: Bearer $TOKEN")

if echo "$PROVIDERS_RESPONSE" | grep -q '"available_providers"'; then
    echo "✅ Providers: OK"
else
    echo "❌ Providers: FAILED"
    echo "Response: $PROVIDERS_RESPONSE"
    exit 1
fi

# Test 5: Informations tokens
echo "🎫 Test 5: Informations tokens"
TOKENS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/tokens/info" \
    -H "Authorization: Bearer $TOKEN")

if echo "$TOKENS_RESPONSE" | grep -q '"remaining_tokens"'; then
    echo "✅ Tokens Info: OK"
else
    echo "❌ Tokens Info: FAILED"
    echo "Response: $TOKENS_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS!"
echo "=================================="
echo ""
echo "📊 Résumé des tests:"
echo "   ✅ Health Check"
echo "   ✅ Login Administrateur"
echo "   ✅ Requête IA"
echo "   ✅ Providers disponibles"
echo "   ✅ Informations tokens"
echo ""
echo "🚀 Votre backend Cloudya est opérationnel!"

# ===== README.md - Guide utilisateur =====
# Cloudya Backend - Installation et Utilisation

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- Docker & Docker Compose
- 4GB RAM minimum
- 10GB espace disque

### Installation automatique
```bash
# Cloner et configurer
git clone <votre-repo> cloudya-backend
cd cloudya-backend

# Installation et démarrage automatique
./scripts/quick_start.sh
```

### Vérification
```bash
# Test automatisé
./scripts/test_installation.sh

# Test manuel
curl http://localhost:8000/health
```

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# Base de données
DATABASE_URL=postgresql://postgres:password@localhost:5432/cloudya

# IA (optionnel pour commencer)
OPENAI_API_KEY=sk-your-key      # Pour les plans payants
ANTHROPIC_API_KEY=your-key      # Pour le plan Pro

# Sécurité
JWT_SECRET_KEY=generated-automatically

# Stripe (pour la facturation)
STRIPE_API_KEY=sk_test_your-key
```

## 🎯 Utilisation

### Connexion avec votre CLI
```bash
# Configurer l'URL
cloudya configure --api-url http://localhost:8000

# Se connecter
cloudya login
# Email: admin@cloudya.ai
# Password: cloudya2024!

# Tester
cloudya ask "créer une instance EC2"
```

### API Endpoints
- POST /api/auth/login - Connexion
- POST /api/command/ - Commande IA
- GET /api/tokens/info - Info tokens
- GET /health - Health check

## 🔄 Administration

### Gestion des services
```bash
# Voir les logs
tail -f api.log

# Redémarrer l'API
pkill -f uvicorn
uvicorn api.main:app --reload

# Arrêter tout
./scripts/stop.sh
```

### Base de données
```bash
# Connexion PostgreSQL
docker-compose exec postgres psql -U postgres -d cloudya

# Reset complet
docker-compose down -v
./scripts/quick_start.sh
```

## 🧪 Développement

### Structure du projet

cloudya-backend/
├── api/           # FastAPI + routes
├── ai/            # Moteur IA + providers
├── knowledge/     # Base de connaissances
├── billing/       # Système de facturation
└── scripts/       # Scripts utilitaires

### Ajout d'un nouveau provider IA
1. Créer ai/providers/votre_provider.py
2. Hériter de BaseLLMProvider
3. Ajouter dans ai/core/llm_manager.py

### Tests
```bash
# Tests unitaires
python -m pytest tests/

# Test d'intégration
./scripts/test_installation.sh
```

## 🐛 Dépannage

### Problèmes courants
1. Port 8000 occupé: Changer le port dans .env
2. Ollama ne démarre pas: Vérifier Docker et mémoire
3. API ne répond pas: Vérifier les logs avec tail -f api.log

### Logs utiles
```bash
# API
tail -f api.log

# PostgreSQL
docker-compose logs postgres

# Ollama
docker-compose logs ollama
```

Parfait ! 🎉 L'architecture backend complète est maintenant prête !

## ✅ Récapitulatif de ce qu'on vient de créer

### 🏗️ Architecture Complète
- ✅ FastAPI avec routes auth, commands, tokens, health
- ✅ Base de données PostgreSQL avec modèles SQLAlchemy
- ✅ Authentification JWT complète avec middleware
- ✅ Rate limiting et sécurité
- ✅ Docker Compose pour développement local
- ✅ Scripts d'installation automatisés

### 📁 Structure Backend Créée

cloudya-backend/
├── api/                    # ✅ FastAPI routes & models
├── ai/                     # 🔄 Prêt pour l'intégration Ollama
├── knowledge/              # 🔄 Prêt pour la base de connaissances
├── billing/                # ✅ Structure pour Stripe
├── config/                 # ✅ Configuration centralisée
├── scripts/                # ✅ Installation & tests automatisés
└── docker-compose.yml      # ✅ Services PostgreSQL + Redis + Ollama

