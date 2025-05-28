#!/bin/bash
echo "🚀 Démarrage de l'environnement de développement Cloudya"

# Démarrer le serveur en arrière-plan
python test_server.py &
SERVER_PID=$!

# Attendre que le serveur démarre
echo "⏳ Attente du démarrage du serveur..."
sleep 3

# Configurer l'environnement
python setup_test.py

# Lancer les tests
echo "🧪 Lancement des tests..."
python test_cloudya.py

echo "✅ Environnement prêt!"
echo "💡 Vous pouvez maintenant utiliser:"
echo "   cloudya ask 'votre question'"
echo "   cloudya chat"

# Garder le serveur en marche
echo "🔴 Appuyez sur Ctrl+C pour arrêter le serveur"
wait $SERVER_PID