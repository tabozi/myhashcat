#!/usr/bin/env python3
"""
Interface en ligne de commande pour MyHashcat
"""
import argparse
from pathlib import Path
from typing import Optional, Set
from src.myhashcat import MyHashcat
import sys
import os
import time
import logging


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
    start <nom> <hash_file> [hash_type]  Démarrer une nouvelle session
        options:
            --word-length <n>            Longueur des mots (défaut: 18)
            --charset <chars>            Caractères à utiliser (défaut: A-Z0-9)
            --rules <fichier>            Fichier de règles à utiliser

    continue <session_id>                Continuer une attaque avec un nouveau dictionnaire
    status <session_id>                  Vérifier le statut d'une session
    stop <session_id>                    Arrêter une session
    list                                 Lister toutes les sessions
    cleanup                             Nettoyer les ressources

EXEMPLES:
    # Démarrer une attaque avec détection automatique du type de hash
    myhashcat start test1 hash.txt

    # Continuer une attaque avec un nouveau dictionnaire
    myhashcat continue test1_20250122_223713

    # Vérifier une session
    myhashcat status test1_20250122_223713

    # Lister les sessions actives
    myhashcat list

Pour plus d'informations: myhashcat --help
""")


def main():
    """Point d'entrée principal du CLI"""
    parser = argparse.ArgumentParser(description="Interface en ligne de commande pour MyHashcat")
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # Configuration du logging
    logger = logging.getLogger('myhashcat.cli')
    
    try:
        # Commande start
        start_parser = subparsers.add_parser("start", help="Démarre une nouvelle attaque")
        start_parser.add_argument("name", help="Nom de la session")
        start_parser.add_argument("hash_file", type=Path, help="Fichier contenant le hash")
        start_parser.add_argument("--hash-type", type=int, help="Type de hash (voir --help de hashcat)")
        start_parser.add_argument("--word-length", type=int, help="Longueur des mots à générer")
        start_parser.add_argument("--charset", help="Ensemble des caractères à utiliser")
        start_parser.add_argument("--rules", type=Path, nargs="+", help="Fichiers de règles à utiliser")
        start_parser.add_argument("--auto-continue", action="store_true", help="Continue automatiquement avec de nouveaux dictionnaires")
        start_parser.add_argument("-v", "--verbose", action="store_true", help="Affiche les détails de l'exécution")

        # Commande continue
        continue_parser = subparsers.add_parser("continue", help="Continue une attaque avec un nouveau dictionnaire")
        continue_parser.add_argument("session_id", help="ID de la session à continuer")
        continue_parser.add_argument("-v", "--verbose", action="store_true", help="Affiche les détails de l'exécution")

        # Commande status
        status_parser = subparsers.add_parser("status", help="Affiche le statut d'une session")
        status_parser.add_argument("session_id", help="ID de la session")
        status_parser.add_argument("-v", "--verbose", action="store_true", help="Affiche les détails de l'exécution")

        # Commande stop
        stop_parser = subparsers.add_parser("stop", help="Arrête une session")
        stop_parser.add_argument("session_id", help="ID de la session")

        # Commande list
        list_parser = subparsers.add_parser("list", help="Liste les sessions")

        # Commande cleanup
        cleanup_parser = subparsers.add_parser("cleanup", help="Nettoie les ressources")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        logger.debug(f"Commande reçue: {args.command}")
        logger.debug(f"Arguments: {vars(args)}")

        hashcat = MyHashcat()

        if args.command == "start":
            try:
                # Conversion du charset si spécifié
                charset = set(args.charset) if args.charset else None
                
                # Création de la session
                session_id = hashcat.create_attack_session(
                    name=args.name,
                    hash_file=args.hash_file,
                    hash_type=args.hash_type,
                    word_length=args.word_length,
                    charset=charset,
                    rules=args.rules,
                    auto_continue=args.auto_continue,
                    verbose=args.verbose
                )
                
                print(f"Session créée: {session_id}")
                logger.info(f"Session créée avec succès: {session_id}")
                
                # Si auto-continue est activé, on surveille la session
                if args.auto_continue:
                    if args.verbose:
                        print("Mode auto-continue activé. Surveillance de la session...")
                    logger.info(f"Mode auto-continue activé pour la session {session_id}")
                    while True:
                        try:
                            status = hashcat.get_session_status(session_id)
                            if status.get("status") == "finished" and status.get("recovered", 0) == 0:
                                if args.verbose:
                                    print("\nDictionnaire épuisé, génération d'un nouveau dictionnaire...")
                                logger.info(f"Dictionnaire épuisé pour la session {session_id}, continuation...")
                                session_id = hashcat.continue_attack(session_id)
                                print(f"Nouvelle session: {session_id}")
                            elif status.get("recovered", 0) > 0:
                                print("\nHash craqué !")
                                logger.info(f"Hash craqué dans la session {session_id}")
                                break
                            time.sleep(10)
                        except Exception as e:
                            logger.error(f"Erreur pendant la surveillance de la session: {str(e)}", exc_info=True)
                            print(f"Erreur pendant la surveillance: {str(e)}")
                            break

            except Exception as e:
                logger.error(f"Erreur lors du démarrage de la session: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        elif args.command == "continue":
            try:
                hashcat.continue_attack(args.session_id, verbose=args.verbose)
                logger.info(f"Session {args.session_id} continuée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la continuation de la session: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        elif args.command == "status":
            try:
                status = hashcat.get_session_status(args.session_id)
                if args.verbose:
                    print("\nStatut détaillé de la session:")
                    for key, value in status.items():
                        print(f"- {key}: {value}")
                else:
                    print(f"Session {args.session_id}: {status.get('status', 'unknown')}")
                    if status.get("recovered", 0) > 0:
                        print("Hash craqué !")
                logger.info(f"Statut récupéré pour la session {args.session_id}: {status.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du statut: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        elif args.command == "stop":
            try:
                hashcat.stop_session(args.session_id)
                print(f"Session {args.session_id} arrêtée")
                logger.info(f"Session {args.session_id} arrêtée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'arrêt de la session: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        elif args.command == "list":
            try:
                sessions = hashcat.session_manager.list_sessions()
                if sessions:
                    print("\nSessions:")
                    for session_id in sessions:
                        session = hashcat.session_manager.load_session(session_id)
                        if session:
                            pid = session.get("process_pid")
                            pid_exists = pid and os.path.exists(f"/proc/{pid}")
                            
                            if not pid_exists and session.get("status") == "running":
                                session["status"] = "finished"
                                hashcat.session_manager.update_session(session_id, {"status": "finished"})
                            
                            status = session.get("status", "unknown")
                            name = session.get("name", "Sans nom")
                            name_display = f"\033[91m{name}\033[0m" if not pid_exists else name
                            pid_display = f"PID: {pid}" if pid_exists else "\033[91mAucun PID\033[0m"
                            print(f"- {session_id} ({name_display}): {status} [{pid_display}]")
                    logger.info(f"Liste des sessions affichée ({len(sessions)} sessions)")
                else:
                    print("Aucune session trouvée")
                    logger.info("Aucune session trouvée")
            except Exception as e:
                logger.error(f"Erreur lors de la liste des sessions: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        elif args.command == "cleanup":
            try:
                hashcat.cleanup()
                logger.info("Nettoyage effectué avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage: {str(e)}", exc_info=True)
                print(f"Erreur: {str(e)}")
                return 1

        else:
            parser.print_help()
            return 1

    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}", exc_info=True)
        print(f"Erreur inattendue: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main()) 