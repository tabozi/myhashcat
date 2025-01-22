# Cahier des Charges - MyHashcat

## Description du Projet
MyHashcat est un outil en Python conçu pour automatiser et optimiser l'utilisation de Hashcat en générant des dictionnaires à la volée.

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

### 2. Gestion des Sessions
- Sauvegarde de l'état d'avancement
- Reprise possible des sessions interrompues
- Historique des tentatives

### 3. Configuration Git
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