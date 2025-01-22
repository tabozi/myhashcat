#!/bin/bash

# Script d'installation de MyHashcat

echo "Installation de MyHashcat..."

# Création des répertoires
echo "Création des répertoires..."
mkdir -p ~/.myhashcat/{work,sessions,rules}

# Copie des fichiers de configuration
echo "Configuration..."
cp config.yaml ~/.myhashcat/

# Vérification de hashcat
if ! command -v hashcat &> /dev/null; then
    echo "ATTENTION: hashcat n'est pas installé."
    echo "Sur Ubuntu/Debian: sudo apt install hashcat"
    echo "Sur CentOS/RHEL: sudo yum install hashcat"
    echo "Sur macOS: brew install hashcat"
fi

# Installation des dépendances Python
echo "Installation des dépendances Python..."
python3 -m pip install -r requirements.txt

# Installation du package en mode développement
echo "Installation du package MyHashcat..."
python3 -m pip install -e .

# Rendre le CLI exécutable
chmod +x src/cli.py

# Création d'un lien symbolique
echo "Création du lien symbolique..."
sudo ln -sf "$(pwd)/src/cli.py" /usr/local/bin/myhashcat

echo "
Installation terminée !

Utilisation:
  myhashcat                            # Afficher l'usage
  myhashcat --help                     # Afficher l'aide détaillée

Exemples:
  myhashcat start test1 hash.txt 0     # Démarrer une attaque MD5
  myhashcat status <session_id>        # Vérifier le statut
  myhashcat list                       # Lister les sessions
  myhashcat stop <session_id>          # Arrêter une session
  myhashcat cleanup                    # Nettoyer les ressources

Configuration: ~/.myhashcat/config.yaml" 