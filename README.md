# MyHashcat

MyHashcat est un outil qui combine la génération de dictionnaires personnalisés avec la puissance de Hashcat pour le crackage de mots de passe.

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/myhashcat.git
cd myhashcat

# Lancer le script d'installation
chmod +x install.sh
./install.sh
```

Le script d'installation :
- Crée les répertoires nécessaires
- Configure l'environnement
- Installe les dépendances
- Rend l'outil accessible via la commande `myhashcat`

## Prérequis

- Python 3.8+
- Hashcat installé et accessible dans le PATH

## Utilisation

### Interface en ligne de commande

```bash
# Afficher l'aide
myhashcat --help

# Démarrer une nouvelle session
myhashcat start test_session hash.txt 0 --word-length 8 --charset "abc123"

# Vérifier le statut d'une session
myhashcat status <session_id>

# Lister toutes les sessions
myhashcat list

# Arrêter une session
myhashcat stop <session_id>

# Nettoyer les ressources
myhashcat cleanup
```

### Utilisation en Python

```python
from pathlib import Path
from myhashcat import MyHashcat

# Initialisation
hashcat = MyHashcat()

# Création d'une session d'attaque
session_id = hashcat.create_attack_session(
    name="test_crack",
    hash_file=Path("hashes.txt"),
    hash_type=0,  # MD5
    word_length=8,
    charset={'a', 'b', 'c', '1', '2', '3'}
)

# Vérification du statut
status = hashcat.get_session_status(session_id)
print(f"Statut de la session: {status['status']}")

# Arrêt de la session
hashcat.stop_session(session_id)

# Nettoyage
hashcat.cleanup()
```

## Configuration

Le fichier de configuration `~/.myhashcat/config.yaml` permet de personnaliser :

```yaml
# Chemins
paths:
  hashcat: "hashcat"
  work_dir: "~/.myhashcat/work"
  sessions_dir: "~/.myhashcat/sessions"
  rules_dir: "~/.myhashcat/rules"

# Paramètres par défaut
defaults:
  word_length: 8
  charset: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  attack_mode: "straight"
```

### Modes d'attaque

- `straight`: Attaque par dictionnaire classique
- `combination`: Attaque par combinaison
- `mask`: Attaque par masque (force brute)

### Options avancées

```bash
# Utilisation de règles
myhashcat start test hash.txt 0 --rules rules/best64.rule

# Configuration du workload
myhashcat start test hash.txt 0 --options '{"workload-profile": 3}'
```

## Gestion des sessions

Chaque session d'attaque est identifiée par un ID unique et contient :
- Configuration de l'attaque
- État actuel
- Dictionnaire généré
- Résultats

## Nettoyage des ressources

MyHashcat gère automatiquement :
- L'arrêt des processus actifs
- La suppression des fichiers temporaires
- Le nettoyage des sessions terminées

## Bonnes pratiques

1. Toujours utiliser la méthode `cleanup()` après utilisation
2. Vérifier régulièrement le statut des sessions
3. Utiliser des charset adaptés à vos besoins
4. Configurer les options Hashcat selon votre matériel

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## Licence

Ce projet est sous licence MIT. 