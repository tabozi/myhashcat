# Cahier des Charges - MyHashcat

## État d'Avancement

### Composants Implémentés

1. **HashcatInterface**
   - Implémentation complète
   - Gestion des processus Hashcat
   - Validation des paramètres
   - Détection automatique du type de hash
   - Optimisations pour WPA

2. **DictionaryGenerator**
   - Implémentation complète
   - Génération de mots de longueur fixe (18 caractères)
   - Charset limité (A-Z0-9)
   - Gestion efficace de la mémoire

3. **SessionManager**
   - Implémentation complète
   - Stockage YAML des sessions
   - Gestion du cycle de vie des sessions
   - Suivi des PID et statuts

4. **MyHashcat**
   - Implémentation complète
   - Interface en ligne de commande
   - Mode silencieux par défaut avec option verbose
   - Système de logging détaillé
   - Continuation automatique des attaques

### Fonctionnalités Complétées

- [x] Génération de dictionnaires optimisée
- [x] Détection automatique du type de hash
- [x] Gestion avancée des sessions
- [x] Suivi des processus avec PID
- [x] Continuation automatique des attaques
- [x] Nettoyage intelligent des ressources
- [x] Système de logging complet
- [x] Mode verbeux pour débogage

## Spécifications Techniques

### Structure des Fichiers

```
~/.myhashcat/
  ├── sessions/      # Sessions YAML
  ├── work/         # Fichiers temporaires
  │   └── dictionaries/
  └── logs/         # Fichiers de logs
```

### Format des Sessions

```yaml
session_id:
  name: string
  hash_file: string (chemin absolu)
  hash_type: int
  word_length: int (18)
  charset: string (A-Z0-9)
  attack_mode: string
  rules: string (optionnel)
  status: string (created|running|stopped|finished)
  process_pid: int
  start_time: datetime
```

### Paramètres par Défaut

- Longueur des mots : 18 caractères (fixe)
- Charset : A-Z0-9
- Mode d'attaque : straight
- Taille du dictionnaire : 1 million de mots

## Tâches Restantes

1. **Tests**
   - Tests d'intégration complets
   - Tests de performance
   - Tests de charge

2. **Documentation**
   - Guide de contribution
   - Documentation API
   - Exemples d'utilisation avancée

3. **Améliorations Futures**
   - Interface graphique
   - Support de modes d'attaque supplémentaires
   - Statistiques d'attaque détaillées
   - Optimisations de performance

## Objectif

Développer un outil Python qui combine la génération de dictionnaires personnalisés avec Hashcat pour le crackage de mots de passe.

## Composants

### 1. Générateur de Dictionnaire
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Génération de mots selon des critères spécifiés
  - Personnalisation du charset
  - Gestion de la longueur des mots
  - Génération par lots pour optimiser la mémoire

### 2. Interface Hashcat
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Validation de l'installation de Hashcat
  - Gestion des différents modes d'attaque
  - Support des règles personnalisées
  - Suivi des processus Hashcat
  - Nettoyage des ressources

### 3. Gestionnaire de Sessions
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Création et suivi des sessions
  - Stockage des configurations
  - Persistance des résultats
  - Gestion des états des sessions

### 4. Interface en Ligne de Commande
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Commandes intuitives (start, status, stop, list, cleanup)
  - Arguments avec valeurs par défaut
  - Messages d'aide détaillés
  - Gestion des erreurs
  - Compatibilité avec les scripts shell

### 5. Configuration
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Fichier de configuration YAML
  - Paramètres par défaut personnalisables
  - Chemins configurables
  - Options Hashcat préconfigurées
  - Liste de règles recommandées

### 6. Installation
- **État**: Implémentation complète
- **Fonctionnalités**:
  - Script d'installation automatique
  - Vérification des prérequis
  - Configuration de l'environnement
  - Installation des dépendances
  - Création des raccourcis système

## Tests

### Tests Unitaires
- Tests du générateur de dictionnaire
- Tests de l'interface Hashcat
- Tests du gestionnaire de sessions
- Couverture de code > 80%

### Tests d'Intégration
- Tests des interactions entre composants
- Tests de l'interface en ligne de commande
- Tests des scénarios d'utilisation complets

## Documentation

### Documentation Technique
- Architecture du projet
- Description des composants
- Diagrammes de classes
- Guide de contribution

### Documentation Utilisateur
- Guide d'installation
- Guide d'utilisation
- Exemples de commandes
- Bonnes pratiques

## Tâches Restantes

1. **Optimisation**:
   - Optimisation de la génération de dictionnaires
   - Amélioration des performances des attaques
   - Réduction de l'utilisation mémoire

2. **Fonctionnalités Avancées**:
   - Support de modes d'attaque supplémentaires
   - Intégration de nouvelles règles
   - Statistiques avancées

3. **Interface Graphique**:
   - Développement d'une interface web
   - Visualisation des résultats
   - Tableau de bord des sessions

## Contraintes Techniques

- Python 3.8+
- Hashcat installé sur le système
- Gestion efficace de la mémoire
- Support multi-plateforme (Linux, Windows, macOS)

## Sécurité

- Validation des entrées utilisateur
- Gestion sécurisée des fichiers temporaires
- Protection contre les injections de commandes
- Nettoyage automatique des ressources sensibles

## Maintenance

- Tests automatisés
- Intégration continue
- Gestion des versions
- Suivi des bugs
- Documentation à jour

## Étapes de Développement

1. **Phase 1 : Setup Initial**
   - Configuration de l'environnement Python
   - Mise en place de Git
   - Création de la structure du projet

2. **Phase 2 : Développement Core**
   - Implémentation du générateur de dictionnaire
   - Interface avec Hashcat
   - Système de gestion des sessions

3. **Phase 3 : Tests et Optimisation**
   - Tests unitaires
   - Tests de performance
   - Optimisation du code

## Dépendances
- Python 3.x
- Hashcat
- Bibliothèques Python (à définir)

## Structure du Projet
```
myhashcat/
├── src/
│   ├── __init__.py
│   ├── generator.py
│   ├── hashcat_interface.py
│   └── session_manager.py
├── tests/
├── requirements.txt
├── README.md
├── .gitignore
└── cdc.md
```

Ce document sera mis à jour au fur et à mesure de l'avancement du projet. 