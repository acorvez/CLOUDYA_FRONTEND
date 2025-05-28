#!/bin/bash
echo "🚀 Démarrage de l'environnement de test Cloudya"

# Vérifier si Python est disponible
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé"
    exit 1
fi

# Démarrer le serveur en arrière-plan
echo "📡 Démarrage du serveur de test..."
python simple_test_server.py &
SERVER_PID=$!

# Fonction de nettoyage
cleanup() {
    echo "🛑 Arrêt du serveur..."
    kill $SERVER_PID 2>/dev/null
    exit
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Attendre que le serveur démarre
echo "⏳ Attente du démarrage du serveur..."
sleep 3

# Configurer l'environnement
echo "⚙️  Configuration de l'environnement de test..."
python ../setup_test.py

# Lancer les tests
echo "🧪 Tests de l'API..."
python test_simple.py

echo ""
echo "✅ Environnement prêt!"
echo "💡 Commandes à tester:"
echo "   cloudya ask 'Déployer sur AWS'"
echo "   cloudya ask 'Créer un cluster Kubernetes'"
echo "   cloudya chat"
echo ""
echo "🔴 Appuyez sur Ctrl+C pour arrêter le serveur"

# Garder le serveur en marche
wait $SERVER_PID