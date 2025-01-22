# MyHashcat

MyHashcat est un outil qui combine la génération de dictionnaires personnalisés avec la puissance de Hashcat pour le crackage de mots de passe.

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
```

## Prérequis

- Python 3.8+
- Hashcat installé et accessible dans le PATH

## Utilisation

### Exemple basique

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

### Utilisation avancée

```python
# Attaque avec règles personnalisées
session_id = hashcat.create_attack_session(
    name="advanced_crack",
    hash_file=Path("hashes.txt"),
    hash_type=1000,  # NTLM
    word_length=10,
    charset={'A', 'B', 'C', '1', '2', '3', '@', '#'},
    attack_mode="straight",
    rules=[Path("rules/best64.rule")],
    options={
        "workload-profile": 3,
        "optimized-kernel-enable": True
    }
)
```

## Configuration

### Paramètres disponibles

- `hashcat_path`: Chemin vers l'exécutable hashcat
- `sessions_dir`: Répertoire pour stocker les sessions
- `work_dir`: Répertoire de travail temporaire

### Modes d'attaque

- `straight`: Attaque par dictionnaire classique
- `combination`: Attaque par combinaison
- `mask`: Attaque par masque (force brute)

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