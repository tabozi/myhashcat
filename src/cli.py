#!/usr/bin/env python3
"""
Interface en ligne de commande pour MyHashcat
"""
import argparse
from pathlib import Path
from typing import Optional, Set
from src.myhashcat import MyHashcat


def parse_charset(charset_str: str) -> Set[str]:
    """Convertit une chaîne de caractères en ensemble"""
    return set(charset_str)


def print_usage():
    """Affiche un message d'usage détaillé"""
    print("""
MyHashcat - Outil de crackage de mots de passe

USAGE:
    myhashcat <commande> [options]

COMMANDES:
    start <nom> <hash_file> <hash_type>  Démarrer une nouvelle session
        options:
            --word-length <n>            Longueur des mots (défaut: 8)
            --charset <chars>            Caractères à utiliser
            --attack-mode <mode>         Mode d'attaque (straight/combination/mask)
            --rules <fichier>            Fichier de règles à utiliser

    status <session_id>                  Vérifier le statut d'une session
    stop <session_id>                    Arrêter une session
    list                                 Lister toutes les sessions
    cleanup                             Nettoyer les ressources

EXEMPLES:
    # Démarrer une attaque MD5 basique
    myhashcat start test1 hash.txt 0

    # Attaque avec charset personnalisé
    myhashcat start test2 hash.txt 1000 --charset "ABC123@#" --word-length 6

    # Utiliser des règles
    myhashcat start test3 hash.txt 0 --rules rules/best64.rule

    # Vérifier une session
    myhashcat status 2023-12-01_test1

    # Lister les sessions actives
    myhashcat list

Pour plus d'informations: myhashcat --help
""")


def main():
    parser = argparse.ArgumentParser(
        description="MyHashcat - Outil de crackage de mots de passe",
        usage="%(prog)s <commande> [options]"
    )
    
    # Arguments généraux
    parser.add_argument("--hashcat-path", default="hashcat", help="Chemin vers l'exécutable hashcat")
    parser.add_argument("--work-dir", type=Path, help="Répertoire de travail")
    parser.add_argument("--sessions-dir", type=Path, help="Répertoire des sessions")
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande: start
    start_parser = subparsers.add_parser("start", help="Démarrer une nouvelle session")
    start_parser.add_argument("name", help="Nom de la session")
    start_parser.add_argument("hash_file", type=Path, help="Fichier contenant le hash")
    start_parser.add_argument("hash_type", type=int, help="Type de hash (voir --help de hashcat)")
    start_parser.add_argument("--word-length", type=int, default=8, help="Longueur des mots à générer")
    start_parser.add_argument("--charset", default="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                            help="Caractères à utiliser pour la génération")
    start_parser.add_argument("--attack-mode", default="straight", choices=["straight", "combination", "mask"],
                            help="Mode d'attaque")
    start_parser.add_argument("--rules", type=Path, nargs="+", help="Fichiers de règles à utiliser")
    
    # Commande: status
    status_parser = subparsers.add_parser("status", help="Vérifier le statut d'une session")
    status_parser.add_argument("session_id", help="Identifiant de la session")
    
    # Commande: stop
    stop_parser = subparsers.add_parser("stop", help="Arrêter une session")
    stop_parser.add_argument("session_id", help="Identifiant de la session")
    
    # Commande: list
    subparsers.add_parser("list", help="Lister toutes les sessions")
    
    # Commande: cleanup
    subparsers.add_parser("cleanup", help="Nettoyer les ressources")
    
    args = parser.parse_args()
    
    # Afficher l'usage si aucune commande n'est spécifiée
    if not args.command:
        print_usage()
        return
    
    # Initialisation de MyHashcat
    hashcat = MyHashcat(
        hashcat_path=args.hashcat_path,
        sessions_dir=args.sessions_dir,
        work_dir=args.work_dir
    )
    
    try:
        if args.command == "start":
            # Démarrage d'une nouvelle session
            session_id = hashcat.create_attack_session(
                name=args.name,
                hash_file=args.hash_file,
                hash_type=args.hash_type,
                word_length=args.word_length,
                charset=parse_charset(args.charset),
                attack_mode=args.attack_mode,
                rules=args.rules
            )
            print(f"Session créée avec l'ID: {session_id}")
            
        elif args.command == "status":
            # Vérification du statut
            status = hashcat.get_session_status(args.session_id)
            print("\nStatut de la session:")
            for key, value in status.items():
                print(f"{key}: {value}")
                
        elif args.command == "stop":
            # Arrêt d'une session
            hashcat.stop_session(args.session_id)
            print(f"Session {args.session_id} arrêtée")
            
        elif args.command == "list":
            # Liste des sessions
            sessions = hashcat.session_manager.list_sessions()
            if not sessions:
                print("Aucune session trouvée")
            else:
                print("\nSessions disponibles:")
                for session_id, session in sessions.items():
                    status = session.get("status", "inconnu")
                    name = session.get("name", "sans nom")
                    print(f"- {session_id}: {name} ({status})")
                    
        elif args.command == "cleanup":
            # Nettoyage
            hashcat.cleanup()
            print("Nettoyage effectué")
            
    except Exception as e:
        print(f"Erreur: {str(e)}")
        exit(1)
    
    
if __name__ == "__main__":
    main() 