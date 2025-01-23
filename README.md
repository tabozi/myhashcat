# MyHashcat 🔒

Un outil puissant combinant une interface Python pour Hashcat avec une génération intelligente de dictionnaires et une gestion avancée des sessions d'attaque.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table des matières

- [Fonctionnalités principales](#-fonctionnalités-principales)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Guide d'utilisation](#-guide-dutilisation)
  - [Commandes de base](#commandes-de-base)
  - [Options avancées](#options-avancées)
  - [Exemples d'utilisation](#exemples-dutilisation)
- [Types de Hash supportés](#-types-de-hash-supportés)
- [Conversion WPA3](#-conversion-wpa3)
- [Architecture](#-architecture)
- [Contribution](#-contribution)
- [Licence](#-licence)

## ✨ Fonctionnalités principales

- 🎯 **Génération intelligente de dictionnaires**
  - Longueur fixe de 18 caractères
  - Génération séquentielle sans doublons
  - Suivi de l'index de génération entre les sessions

- 🔍 **Détection automatique des hashs**
  - Support des formats courants (MD5, SHA1, SHA256, etc.)
  - Configuration manuelle possible

- 📊 **Gestion avancée des sessions**
  - Suivi du statut et des PID
  - Continuation automatique des attaques
  - Mode verbeux pour le débogage

## 🛠 Prérequis

- Python 3.8 ou supérieur
- Hashcat installé et accessible dans le PATH
- pip (gestionnaire de paquets Python)
- venv (module de gestion d'environnements virtuels Python)

## 📥 Installation

1. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

2. Installez le package :
```bash
./install.sh
```

## 📖 Guide d'utilisation

### Commandes de base

```bash
# Démarrer une nouvelle attaque
myhashcat start <nom> <fichier_hash> [options]

# Continuer une attaque existante
myhashcat continue <session_id>

# Vérifier le statut
myhashcat status <session_id>

# Lister les sessions actives
myhashcat list

# Arrêter une session
myhashcat stop <session_id>

# Nettoyer les ressources
myhashcat cleanup
```

### Options avancées

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `--hash-type` | Type de hash | Auto-détection |
| `--word-length` | Longueur des mots | 18 caractères |
| `--charset` | Jeu de caractères | A-Z0-9 |
| `--rules` | Fichier de règles | Aucun |
| `--skip` | Mots à sauter | 0 |
| `--auto-continue` | Continuation auto | Désactivé |
| `-v, --verbose` | Mode verbeux | Désactivé |

### Exemples d'utilisation

```bash
# Attaque simple avec détection automatique
myhashcat start test1 hash.txt

# Attaque avec options avancées
myhashcat start crack1 hash.txt --hash-type 1400 --charset "abcABC123" --auto-continue -v

# Reprise d'une session existante
myhashcat continue test1_20250122_223713
```

## 🔑 Types de Hash supportés

### Détection automatique

MyHashcat détecte automatiquement les types de hash suivants :

| Type | ID | Description |
|------|-----|-------------|
| MD5 | 0 | Hash MD5 standard |
| SHA1 | 100 | Hash SHA1 |
| SHA256 | 1400 | Hash SHA2-256 |
| SHA512 | 1700 | Hash SHA2-512 |
| BCrypt | 3200 | Hash BCrypt |
| SHA256 Unix | 7400 | Hash SHA256 Unix |
| SHA512 Unix | 1800 | Hash SHA512 Unix |
| PHPass | 400 | Hash PHPass |

Pour voir tous les types supportés :
```bash
hashcat --help | grep -i "hash modes"
```

## 📡 Conversion WPA3

### Installation de hcxpcaptool

```bash
git clone https://github.com/ZerBea/hcxtools.git
cd hcxtools
make
sudo make install
```

### Conversion du fichier .cap

```bash
hcxpcaptool -o output.22000 input.cap
```

### Utilisation avec Hashcat

```bash
hashcat -m 22000 -a 3 output.22000 ?a?a?a?a?a?a?a?a
```

## 🏗 Architecture

```
~/.myhashcat/
├── sessions/      # Configuration des sessions (YAML)
├── work/         # Fichiers temporaires
│   └── dictionaries/  # Dictionnaires générés
└── logs/         # Journaux d'exécution
```

## 🤝 Contribution

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus d'informations. 