# MyHashcat

Interface Python pour Hashcat avec génération de dictionnaires intégrée et gestion avancée des sessions.

## Prérequis

- Python 3.8+
- Hashcat installé et accessible dans le PATH
- pip (gestionnaire de paquets Python)
- venv (module de gestion d'environnements virtuels Python)

## Conversion des fichiers .cap WPA3 pour Hashcat

Pour cracker un réseau WPA3, vous devez d'abord convertir le fichier `.cap` en un format utilisable par Hashcat. Voici comment procéder :

### Étapes de conversion

1. **Installer hcxpcaptool** :
   - Clonez le dépôt `hcxtools` depuis GitHub :
     ```bash
     git clone https://github.com/ZerBea/hcxtools.git
     ```
   - Accédez au répertoire cloné :
     ```bash
     cd hcxtools
     ```
   - Compilez et installez les outils :
     ```bash
     make
     sudo make install
     ```

2. **Convertir le fichier .cap** :
   - Utilisez la commande suivante pour convertir votre fichier `.cap` en un format compatible avec Hashcat (mode 22000) :
     ```bash
     hcxpcaptool -o output.22000 input.cap
     ```
   - Remplacez `input.cap` par le chemin de votre fichier `.cap` et `output.22000` par le nom de fichier souhaité pour la sortie.

3. **Utiliser Hashcat** :
   - Une fois le fichier converti, utilisez Hashcat avec le mode 22000 pour tenter de cracker le mot de passe :
     ```bash
     hashcat -m 22000 -a 3 output.22000 ?a?a?a?a?a?a?a?a
     ```
   - Remplacez `output.22000` par le nom de votre fichier converti et ajustez le masque `?a?a?a?a?a?a?a?a` selon vos besoins.

### Remarques
- Assurez-vous que votre version de Hashcat supporte le mode 22000.
- Le processus de conversion et de cracking peut nécessiter des ressources importantes en fonction de la complexité du mot de passe et de la puissance de votre matériel.

Cette procédure vous permettra de préparer vos fichiers de capture WPA3 pour une utilisation avec Hashcat.

## Installation

1. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Installez le package :
```bash
./install.sh
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

### Commandes Disponibles

- `myhashcat start <nom> <fichier_hash> [options]` : Démarre une nouvelle attaque
  - Options :
    - `--hash-type <type>` : Type de hash (détection automatique par défaut)
    - `--word-length <longueur>` : Longueur des mots (fixée à 18 caractères)
    - `--charset <charset>` : Jeu de caractères (A-Z0-9 par défaut)
    - `--rules <fichier>` : Fichier de règles à utiliser
    - `--skip <n>` : Nombre de mots à sauter dans le dictionnaire
    - `--auto-continue` : Continue automatiquement avec un nouveau dictionnaire
    - `-v, --verbose` : Mode verbeux

- `myhashcat continue <session_id>` : Continue une attaque avec un nouveau dictionnaire
  - Options :
    - `-v, --verbose` : Mode verbeux

- `myhashcat status <session_id>` : Affiche le statut d'une session
- `myhashcat stop <session_id>` : Arrête une session
- `myhashcat list` : Liste toutes les sessions avec leur PID
- `myhashcat cleanup` : Nettoie les ressources

### Exemples

```bash
# Démarrer une attaque avec détection automatique du hash
myhashcat start test1 hash.txt

# Démarrer une attaque en sautant les 1000 premiers mots
myhashcat start test1 hash.txt --skip 1000

# Démarrer une attaque avec auto-continue
myhashcat start test1 hash.txt --auto-continue

# Continuer une attaque spécifique
myhashcat continue test1_20250122_223713

# Vérifier le statut d'une session
myhashcat status test1_20250122_223713

# Lister les sessions actives (avec PID)
myhashcat list
```

## Structure des Fichiers

```
~/.myhashcat/
  ├── sessions/      # Sessions YAML
  ├── work/         # Fichiers temporaires
  │   └── dictionaries/
  └── logs/         # Fichiers de logs
```

## Fonctionnalités

- Génération de dictionnaires avec longueur fixe de 18 caractères
- Charset limité aux majuscules (A-Z) et chiffres (0-9)
- Détection automatique du type de hash
- Gestion des sessions avec statut et PID
- Continuation automatique des attaques
- Nettoyage intelligent des ressources
- Système de logging détaillé
- Mode verbeux pour le débogage

## Développement

Pour contribuer au projet :

1. Clonez le dépôt
2. Créez une branche pour votre fonctionnalité
3. Soumettez une pull request

## Licence

Ce projet est sous licence MIT. 