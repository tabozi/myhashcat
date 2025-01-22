# MyHashcat

MyHashcat est un outil qui combine la génération de dictionnaires personnalisés avec la puissance de Hashcat pour le crackage de mots de passe.

## Prérequis

- Python 3.8+
- Hashcat installé et accessible dans le PATH
- pip (gestionnaire de paquets Python)
- venv (module de gestion d'environnements virtuels Python)

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/myhashcat.git
cd myhashcat

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Installer l'outil
pip install -e .
```

## Types de Hash

Le paramètre `hash_type` correspond à l'identifiant numérique utilisé par Hashcat pour identifier le type de hash. Voici les types les plus courants :

```bash
0     # MD5
100   # SHA1
1400  # SHA2-256
1700  # SHA2-512
3200  # BCRYPT
```

### Détection Automatique du Type de Hash

MyHashcat peut maintenant détecter automatiquement le type de hash, ce qui simplifie l'utilisation de l'outil :

```python
# Création d'une session avec détection automatique du type de hash
session_id = hashcat.create_attack_session(
    name="test_crack",
    hash_file=Path("hashes.txt"),  # Le type sera détecté automatiquement
    word_length=8,
    charset={'a', 'b', 'c', '1', '2', '3'}
)
```

En ligne de commande :
```bash
# Création d'une session avec détection automatique
myhashcat start test_session hashes.txt

# Le type de hash sera affiché lors du démarrage
# Exemple : "Type de hash détecté : MD5 (ID: 0)"
```

Types de hash supportés pour la détection automatique :
- MD5 (ID: 0)
- SHA1 (ID: 100)
- SHA256 (ID: 1400)
- SHA512 (ID: 1700)
- BCrypt (ID: 3200)
- SHA256 Unix (ID: 7400)
- SHA512 Unix (ID: 1800)
- PHPass (ID: 400)

Si la détection automatique échoue, vous pouvez toujours spécifier manuellement le type de hash :
```bash
myhashcat start test_session hashes.txt 1400  # Force SHA256
```

Pour une liste complète des types de hash supportés :
```bash
hashcat --help | grep -i "hash modes"
```

## Utilisation

### Exemple de base

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
print(f"Statut: {status['status']}")
```

### En ligne de commande

```bash
# Démarrer une attaque
myhashcat start test_session hash.txt 0

# Vérifier le statut
myhashcat status <session_id>

# Arrêter une session
myhashcat stop <session_id>
```

### Options avancées

```bash
# Utilisation de règles
myhashcat start test hash.txt 0 --rules rules/best64.rule

# Configuration du workload
myhashcat start test hash.txt 0 --options '{"workload-profile": 3}'
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
  word_length: 18
  charset: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  attack_mode: "mask"
```

### Modes d'attaque

- `mask`: Attaque par masque (force brute)
- `straight`: Attaque par dictionnaire classique
- `combination`: Attaque par combinaison

### Gestion des Sessions

MyHashcat utilise un système de sessions pour gérer les attaques de mots de passe. Une session représente une instance d'attaque avec sa configuration et son état.

### Caractéristiques des Sessions

- **Identification** : Chaque session est identifiée par un ID unique composé du nom de la session et d'un horodatage.
- **État** : Une session peut être dans l'un des états suivants :
  - `created` : Session nouvellement créée
  - `running` : Attaque en cours d'exécution
  - `stopped` : Attaque arrêtée manuellement
  - `finished` : Attaque terminée

### Configuration d'une Session

Une session stocke les informations suivantes :
- Fichier de hash à cracker
- Type de hash (format hashcat)
- Mode d'attaque (straight, rules, mask)
- Configuration du générateur de dictionnaire
  - Longueur des mots
  - Jeu de caractères
- Règles de transformation (optionnel)
- Options supplémentaires

### Contraintes et Limitations

1. **Stockage** :
   - Les sessions sont stockées dans `~/.myhashcat/sessions/`
   - Chaque session crée son propre fichier de dictionnaire

2. **Ressources** :
   - Une session active maintient un processus hashcat
   - Les dictionnaires générés occupent de l'espace disque
   - Il est recommandé de nettoyer régulièrement les sessions terminées

3. **Gestion du Cycle de Vie** :
   - Les sessions doivent être explicitement arrêtées avec `stop`
   - Le nettoyage avec `cleanup` est nécessaire pour libérer les ressources
   - Les sessions arrêtées ou terminées sont supprimées lors du cleanup

### Commandes de Gestion

```bash
# Créer une nouvelle session
myhashcat start <nom_session> <fichier_hash> <type_hash> [options]

# Vérifier le statut d'une session
myhashcat status <session_id>

# Lister toutes les sessions
myhashcat list

# Arrêter une session
myhashcat stop <session_id>

# Nettoyer les sessions terminées et les ressources
myhashcat cleanup
```

### Bonnes Pratiques

1. Toujours vérifier le statut des sessions avec `list`
2. Arrêter les sessions inutilisées avec `stop`
3. Exécuter régulièrement `cleanup` pour libérer les ressources
4. Utiliser des noms de session explicites pour faciliter leur identification

## Nettoyage des ressources

MyHashcat gère automatiquement :
- L'arrêt des processus actifs
- La suppression des fichiers temporaires
- Le nettoyage des sessions terminées

## Bonnes pratiques

1. Toujours utiliser un environnement virtuel Python
2. Activer l'environnement avant d'utiliser l'outil
3. Utiliser la méthode `cleanup()` après utilisation
4. Vérifier régulièrement le statut des sessions
5. Utiliser des charset adaptés à vos besoins
6. Configurer les options Hashcat selon votre matériel

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## Licence

Ce projet est sous licence MIT.

> **Note** : La détection automatique du type de hash sera implémentée dans une version future de MyHashcat. 