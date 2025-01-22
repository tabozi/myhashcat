# Cahier des Charges - MyHashcat

## Description du Projet
MyHashcat est un outil en Python conçu pour automatiser et optimiser l'utilisation de Hashcat en générant des dictionnaires à la volée.

## État d'Avancement

### Tâches Complétées ✅
1. **Setup Initial**
   - Structure du projet créée
   - Configuration Git mise en place
   - Fichiers de base créés (README.md, requirements.txt, .gitignore)
   - Structure des modules Python établie

2. **Développement Core - Initial**
   - Classes de base créées :
     - `DictionaryGenerator` : Implémentation complète et testée
     - `HashcatInterface` : Implémentation complète et testée
     - `SessionManager` : système de gestion des sessions implémenté

3. **Tests**
   - Tests unitaires complets pour le générateur de dictionnaire
   - Tests unitaires complets pour l'interface Hashcat :
     - Validation de l'installation
     - Gestion des modes d'attaque
     - Lancement et suivi des attaques
     - Gestion des erreurs
     - Nettoyage des ressources
   - Tous les tests passent avec succès

### Tâches Restantes 📝
1. **Développement Core**
   - Intégration des composants ensemble
   - Tests d'intégration

2. **Tests et Documentation**
   - Documenter l'utilisation de l'outil
   - Ajouter des exemples d'utilisation

3. **Optimisation**
   - Tests de performance
   - Optimisation du code
   - Gestion de la mémoire pour les grands dictionnaires

## Objectifs Principaux
1. Créer une interface Python pour Hashcat
2. Générer des dictionnaires dynamiquement
3. Gérer des sessions de cracking
4. Intégrer une gestion de version avec Git

## Spécifications Techniques

### 1. Génération de Dictionnaire
- Longueur par défaut : 18 caractères
- Charset par défaut : 
  - Lettres majuscules (A-Z)
  - Chiffres (0-9)
- Possibilité de personnaliser les paramètres
- Fonctionnalités implémentées :
  - Génération aléatoire de lots de mots uniques
  - Génération séquentielle à partir d'un index
  - Estimation de l'utilisation mémoire
  - Validation des paramètres d'entrée
  - Gestion des limites de combinaisons

### 2. Interface Hashcat
- Modes d'attaque supportés :
  - `straight` (0) : Attaque en ligne droite
  - `combination` (1) : Attaque par combinaison
  - `bruteforce` (3) : Attaque par force brute avec masque
  - `hybrid` (6) : Attaque hybride dict + mask
- Fonctionnalités implémentées :
  - Validation de l'installation de Hashcat
  - Gestion des fichiers de dictionnaire et règles
  - Support des masques pour force brute
  - Suivi de la progression des attaques
  - Gestion propre des processus
  - Nettoyage automatique des fichiers temporaires

### 3. Gestion des Sessions
- Sauvegarde de l'état d'avancement
- Reprise possible des sessions interrompues
- Historique des tentatives

### 4. Configuration Git
- Structure du projet
- Fichiers à ignorer (.gitignore)
- Convention de commits

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