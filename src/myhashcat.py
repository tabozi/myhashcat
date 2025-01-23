"""
Module principal de MyHashcat intégrant tous les composants
"""
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import string
import logging
import os
import psutil

from .generator import DictionaryGenerator
from .hashcat_interface import HashcatInterface
from .session_manager import SessionManager
from .hash_detector import HashDetector


def setup_logging(log_dir: Path) -> logging.Logger:
    """Configure le système de logging"""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Création du logger
    logger = logging.getLogger('myhashcat')
    logger.setLevel(logging.DEBUG)
    
    # Format détaillé pour le fichier
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour le fichier de log
    log_file = log_dir / "myhashcat.log"
    # Création du répertoire des logs si nécessaire
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    return logger


class MyHashcat:
    """Classe principale intégrant le générateur de dictionnaire avec Hashcat"""

    def __init__(
        self,
        hashcat_path: str = "hashcat",
        sessions_dir: Optional[Path] = None,
        work_dir: Optional[Path] = None,
        verbose: bool = False
    ):
        """
        Initialise MyHashcat

        Args:
            hashcat_path (str): Chemin vers l'exécutable hashcat
            sessions_dir (Path, optional): Répertoire pour les sessions
            work_dir (Path, optional): Répertoire de travail
            verbose (bool): Affiche les détails de l'exécution
        """
        # Configuration des chemins par défaut
        default_base_dir = Path.home() / ".myhashcat"
        self.work_dir = work_dir or default_base_dir / "work"
        self.sessions_dir = sessions_dir or default_base_dir / "sessions"
        self.log_dir = Path.home() / "work/myhashcat/logs"
        
        # Configuration du logging
        self.logger = setup_logging(self.log_dir)
        self.logger.info("Initialisation de MyHashcat")
        
        # Initialisation des composants
        self.hashcat = HashcatInterface(hashcat_path=hashcat_path)
        self.session_manager = SessionManager(sessions_dir=self.sessions_dir)
        self._active_processes = {}  # Stockage des processus actifs
        
        # Création des répertoires nécessaires
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.dict_dir = self.work_dir / "dictionaries"
        self.dict_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Répertoires initialisés: work_dir={self.work_dir}, sessions_dir={self.sessions_dir}")
        self.logger.info(f"Version de Hashcat: {self.hashcat.version}")

    def create_attack_session(
        self,
        name: str,
        hash_file: Path,
        hash_type: Optional[int] = None,
        word_length: Optional[int] = None,
        charset: Optional[set] = None,
        attack_mode: str = "straight",
        rules: Optional[List[Path]] = None,
        mask: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        auto_continue: bool = False,
        verbose: bool = False
    ) -> str:
        """
        Crée et démarre une nouvelle session d'attaque
        """
        try:
            self.logger.info(f"Création d'une nouvelle session d'attaque: {name}")
            self.logger.debug(f"Paramètres: hash_file={hash_file}, hash_type={hash_type}, word_length={word_length}")

            # Vérification du fichier de hash
            if not hash_file.exists():
                error_msg = f"Fichier de hash non trouvé: {hash_file}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            # Détection automatique du type de hash si non spécifié
            if hash_type is None:
                try:
                    detected = HashDetector.detect_from_file(hash_file)
                    if detected:
                        hash_type = detected["id"]
                        self.logger.info(f"Type de hash détecté: {detected['name']} (ID: {detected['id']})")
                        if verbose:
                            print(f"Type de hash détecté : {detected['name']} (ID: {detected['id']})")
                    else:
                        error_msg = "Impossible de détecter automatiquement le type de hash"
                        self.logger.error(error_msg)
                        raise ValueError(f"{error_msg}. Veuillez le spécifier manuellement.")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la détection du type de hash: {str(e)}")
                    raise ValueError(f"Erreur lors de la détection du type de hash: {str(e)}")

            # Définition de la longueur par défaut
            if word_length is None:
                word_length = 18  # Longueur par défaut
                self.logger.debug(f"Utilisation de la longueur par défaut: {word_length}")
            elif word_length != 18:
                self.logger.warning(f"Longueur spécifiée ({word_length}) ignorée, utilisation de 18 caractères")
                if verbose:
                    print(f"Attention : La longueur des mots est fixée à 18 caractères selon les spécifications.")
                word_length = 18

            # Configuration du charset par défaut (A-Z, 0-9)
            if charset is None:
                charset = set(string.ascii_uppercase + string.digits)
                self.logger.debug(f"Utilisation du charset par défaut: {''.join(sorted(charset))}")
            else:
                # Force le charset à n'utiliser que des majuscules et des chiffres
                old_charset = charset
                charset = set(c.upper() for c in charset if c.upper() in string.ascii_uppercase + string.digits)
                if charset != old_charset:
                    self.logger.warning(f"Charset modifié pour n'inclure que les majuscules et chiffres: {''.join(sorted(charset))}")

            # Ajustements spécifiques pour WPA
            if hash_type == 22000:  # WPA-PBKDF2-PMKID+EAPOL
                self.logger.info("Configuration optimisée pour WPA détectée")
                if verbose:
                    print("Configuration optimisée pour WPA détectée")
                
                # Ajout des règles de mutation si non spécifiées
                if not rules:
                    hashcat_dir = Path("/usr/share/hashcat")
                    rules_file = hashcat_dir / "rules/best64.rule"
                    if rules_file.exists():
                        rules = [rules_file]
                        self.logger.info("Ajout automatique des règles de mutation best64.rule")
                        if verbose:
                            print("Ajout automatique des règles de mutation best64.rule")
                    else:
                        self.logger.warning("Fichier de règles best64.rule non trouvé")

            # Configuration de la session
            config = {
                "name": name,
                "hash_file": str(hash_file.resolve()),  # Chemin absolu du fichier de hash
                "hash_type": hash_type,
                "word_length": word_length,
                "charset": list(charset),
                "attack_mode": attack_mode,
                "rules": [str(r) for r in rules] if rules else None,
                "mask": mask,
                "options": options,
                "start_time": datetime.now().isoformat()
            }

            # Création de la session
            try:
                # Vérification que le fichier de hash est bien dans la config
                if "hash_file" not in config or not config["hash_file"]:
                    raise ValueError("Le fichier de hash n'est pas spécifié dans la configuration")
                
                session_id = self.session_manager.create_session(name, config)
                self.logger.info(f"Session créée avec l'ID: {session_id}")
                self.logger.debug(f"Configuration de la session: {config}")
                
                # Vérification immédiate que la session a été créée avec le bon fichier de hash
                created_session = self.session_manager.load_session(session_id)
                if not created_session.get("hash_file"):
                    raise ValueError("Le fichier de hash n'a pas été enregistré dans la session")
                self.logger.debug(f"Fichier de hash vérifié dans la session: {created_session['hash_file']}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la création de la session: {str(e)}")
                raise RuntimeError(f"Erreur lors de la création de la session: {str(e)}")

            # Initialisation du générateur avec les paramètres spécifiés
            try:
                generator = DictionaryGenerator(length=word_length, charset=charset)
                if verbose:
                    print(f"\nConfiguration du générateur :")
                    print(f"- Longueur des mots : {word_length} caractères")
                    print(f"- Charset : {''.join(sorted(charset))}")
                    if rules:
                        print(f"- Règles : {', '.join(str(r) for r in rules)}")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'initialisation du générateur: {str(e)}")
                raise RuntimeError(f"Erreur lors de l'initialisation du générateur: {str(e)}")

            # Création du dictionnaire initial
            try:
                dict_file = self.dict_dir / f"{session_id}_initial.txt"
                self._generate_dictionary(generator, dict_file, verbose=verbose)
                self.logger.info(f"Dictionnaire généré: {dict_file}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la génération du dictionnaire: {str(e)}")
                raise RuntimeError(f"Erreur lors de la génération du dictionnaire: {str(e)}")

            # Lancement de l'attaque
            try:
                process = self.hashcat.start_attack(
                    hash_file=hash_file,
                    attack_mode=attack_mode,
                    hash_type=hash_type,
                    dictionary=dict_file,
                    rules=rules,
                    mask=mask,
                    session=session_id,
                    options={
                        "status-timer": 10,  # Mise à jour toutes les 10 secondes
                        **(options or {})
                    }
                )
                self.logger.info(f"Attaque démarrée avec le PID {process.pid}")
            except Exception as e:
                self.logger.error(f"Erreur lors du lancement de l'attaque: {str(e)}")
                raise RuntimeError(f"Erreur lors du lancement de l'attaque: {str(e)}")

            # Stockage du processus
            self._active_processes[session_id] = process
            if verbose:
                print(f"Processus enregistré pour la session {session_id}: PID {process.pid}")

            # Mise à jour de la session
            try:
                self.session_manager.update_session(session_id, {
                    "process_pid": process.pid,
                    "dictionary_file": str(dict_file),
                    "status": "running",
                    "rules": [str(r) for r in rules] if rules else None
                })
                self.logger.info(f"Session mise à jour avec le PID {process.pid}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la mise à jour de la session: {str(e)}")
                raise RuntimeError(f"Erreur lors de la mise à jour de la session: {str(e)}")

            # Vérification immédiate du statut
            if process.poll() is not None:
                self.logger.warning("Le processus s'est terminé immédiatement")
                if verbose:
                    print("Le processus s'est terminé immédiatement")
                self.session_manager.update_session(session_id, {"status": "finished"})
                self._active_processes.pop(session_id, None)

            return session_id

        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la session d'attaque: {str(e)}", exc_info=True)
            raise

    def _generate_dictionary(
        self,
        generator: DictionaryGenerator,
        output_file: Path,
        batch_size: int = 1_000_000,
        verbose: bool = False
    ) -> None:
        """
        Génère un dictionnaire et l'écrit dans un fichier

        Args:
            generator (DictionaryGenerator): Générateur à utiliser
            output_file (Path): Fichier de sortie
            batch_size (int): Taille du lot de mots à générer (par défaut : 1 million)
            verbose (bool): Affiche les détails de l'exécution
        """
        if verbose:
            print(f"Génération d'un dictionnaire de {batch_size} mots...")
        words = generator.generate_batch(batch_size=batch_size)
        with output_file.open("w") as f:
            for word in words:
                f.write(f"{word}\n")
        if verbose:
            print(f"Dictionnaire généré avec succès : {output_file}")

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère l'état d'une session

        Args:
            session_id (str): Identifiant de la session

        Returns:
            Dict[str, Any]: État de la session
        """
        session = self.session_manager.load_session(session_id)
        if not session:
            raise ValueError(f"Session non trouvée: {session_id}")

        # Mise à jour du statut si un processus est en cours
        if session.get("process_pid"):
            process = self._active_processes.get(session_id)
            if process:
                # Vérification si le processus est toujours en cours d'exécution
                if process.poll() is None:
                    # Lecture de la sortie sans l'afficher
                    if process.stdout:
                        while True:
                            line = process.stdout.readline()
                            if not line:
                                break
                            # Analyse des lignes importantes
                            if "Recovered" in line:
                                recovered = line.split(":")[1].strip().split("/")[0]
                                if int(recovered) > 0:
                                    session["recovered"] = int(recovered)
                                    session["status"] = "finished"
                                    self.session_manager.update_session(session_id, {
                                        "status": "finished",
                                        "recovered": int(recovered)
                                    })
                                    return session
                            elif "Progress" in line:
                                progress = line.split(":")[1].strip().split("/")[0]
                                session["progress"] = progress
                    
                    # Si le processus est toujours en cours
                    session["status"] = "running"
                else:
                    session["status"] = "finished"
                    self.session_manager.update_session(session_id, {"status": "finished"})
                    self._active_processes.pop(session_id, None)
            else:
                # Mise à jour du statut pour refléter l'absence de processus
                session["status"] = "finished"
                self.session_manager.update_session(session_id, {"status": "finished"})

        return session

    def stop_session(self, session_id: str) -> None:
        """Arrête une session en cours d'exécution."""
        self.logger.info(f"Tentative d'arrêt de la session {session_id}")
        
        try:
            session = self.session_manager.load_session(session_id)
            if not session:
                self.logger.error(f"Session {session_id} non trouvée")
                raise ValueError(f"Session {session_id} non trouvée")

            # Récupérer le PID du processus
            pid = session.get("process_pid")
            if not pid:
                self.logger.warning(f"Aucun PID trouvé pour la session {session_id}")
                return

            # Tenter d'arrêter le processus principal
            try:
                parent = psutil.Process(pid)
                # Arrêter tous les processus enfants
                children = parent.children(recursive=True)
                for child in children:
                    self.logger.debug(f"Tentative d'arrêt du processus enfant {child.pid}")
                    child.kill()
                # Arrêter le processus parent
                self.logger.debug(f"Tentative d'arrêt du processus parent {pid}")
                parent.kill()
            except psutil.NoSuchProcess:
                self.logger.warning(f"Processus {pid} déjà terminé")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'arrêt du processus {pid}: {str(e)}")

            # Mettre à jour le statut de la session
            session["status"] = "stopped"
            self.session_manager.update_session(session_id, session)
            
            # Supprimer le processus de la liste des processus actifs
            if session_id in self._active_processes:
                del self._active_processes[session_id]
            
            self.logger.info(f"Session {session_id} arrêtée avec succès")

        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt de la session {session_id}: {str(e)}")
            raise

    def cleanup(self) -> None:
        """
        Nettoie les ressources temporaires et les sessions
        
        Cette méthode va :
        1. Lister toutes les sessions actives
        2. Arrêter les processus en cours
        3. Supprimer les sessions terminées
        4. Nettoyer les fichiers temporaires
        """
        print("\n=== Nettoyage de MyHashcat ===")
        
        # 1. Liste et arrêt des processus actifs
        if self._active_processes:
            print("\n1. Sessions actives trouvées :")
            active_sessions = list(self._active_processes.keys())
            for session_id in active_sessions:
                session = self.session_manager.load_session(session_id)
                if session:
                    print(f"   - {session_id} (PID: {session.get('process_pid')})")
                    try:
                        print(f"     → Arrêt de la session {session_id}...")
                        self.stop_session(session_id)
                        print(f"     → Session arrêtée avec succès")
                    except Exception as e:
                        print(f"     → Erreur lors de l'arrêt : {e}")
        else:
            print("\n1. Aucune session active trouvée")

        # 2. Nettoyage de l'interface Hashcat
        print("\n2. Nettoyage des ressources Hashcat...")
        try:
            self.hashcat.cleanup()
            print("   → Ressources Hashcat nettoyées")
        except Exception as e:
            print(f"   → Erreur lors du nettoyage Hashcat : {e}")

        # 3. Suppression des sessions terminées
        print("\n3. Nettoyage des sessions...")
        sessions = self.session_manager.list_sessions()
        if sessions:
            for session_id in sessions:
                session = self.session_manager.load_session(session_id)
                if session:
                    status = session.get("status", "unknown")
                    print(f"   - Session {session_id} ({status})")
                    if status in ["finished", "stopped"]:
                        try:
                            self.session_manager.delete_session(session_id)
                            print(f"     → Supprimée")
                        except Exception as e:
                            print(f"     → Erreur lors de la suppression : {e}")
                    else:
                        print(f"     → Conservée (statut: {status})")
        else:
            print("   → Aucune session trouvée")

        # 4. Nettoyage des fichiers temporaires
        print("\n4. Nettoyage des fichiers temporaires...")
        
        # Nettoyage des dictionnaires
        if self.dict_dir.exists():
            try:
                files_count = len(list(self.dict_dir.glob("*")))
                for file in self.dict_dir.glob("*"):
                    try:
                        file.unlink()
                    except OSError as e:
                        print(f"   → Erreur lors de la suppression de {file.name}: {e}")
                print(f"   → {files_count} fichiers dictionnaire(s) supprimé(s)")
                
                self.dict_dir.rmdir()
                print("   → Répertoire des dictionnaires supprimé")
            except OSError as e:
                print(f"   → Erreur lors de la suppression du répertoire des dictionnaires : {e}")

        # Nettoyage du répertoire de travail
        if self.work_dir.exists():
            try:
                self.work_dir.rmdir()
                print("   → Répertoire de travail supprimé")
            except OSError as e:
                print("   → Le répertoire de travail contient encore des fichiers, il sera conservé")

        print("\n=== Nettoyage terminé ===\n") 

    def continue_attack(self, session_id: str, verbose: bool = False) -> str:
        """
        Continue une attaque avec un nouveau dictionnaire

        Args:
            session_id (str): Identifiant de la session à continuer
            verbose (bool): Affiche les détails de l'exécution

        Returns:
            str: ID de la nouvelle session
        """
        self.logger.info(f"Continuation de l'attaque pour la session {session_id}")

        # Chargement de la session
        session = self.session_manager.load_session(session_id)
        if not session:
            error_msg = f"Session non trouvée: {session_id}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Vérification que la session est terminée
        if session.get("status") != "finished":
            error_msg = f"La session {session_id} n'est pas terminée"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Récupération des paramètres de la session avec valeurs par défaut
        try:
            hash_file = session.get("hash_file")
            if not hash_file:
                error_msg = "Fichier de hash non spécifié dans la session"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            hash_file = Path(hash_file)
            if not hash_file.exists():
                error_msg = f"Fichier de hash non trouvé: {hash_file}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            self.logger.debug(f"Fichier de hash trouvé: {hash_file}")
        except Exception as e:
            error_msg = f"Erreur lors de la récupération du fichier de hash: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        word_length = session.get("word_length", 18)  # Valeur par défaut : 18
        charset = set(session.get("charset", list(string.ascii_uppercase + string.digits)))  # Valeur par défaut : A-Z0-9
        rules = [Path(r) for r in session["rules"]] if session.get("rules") else None
        hash_type = session.get("hash_type")
        
        if hash_type is None:
            error_msg = "Type de hash non spécifié dans la session"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.debug(f"Paramètres récupérés: hash_file={hash_file}, hash_type={hash_type}, word_length={word_length}")
        
        # Création d'un nouveau dictionnaire avec un suffixe incrémenté
        base_name = session_id.rsplit("_", 2)[0]  # Retire le timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_session_id = f"{base_name}_{timestamp}"
        
        # Initialisation du générateur avec les mêmes paramètres
        try:
            generator = DictionaryGenerator(length=word_length, charset=charset)
            dict_file = self.dict_dir / f"{new_session_id}_initial.txt"
            
            if verbose:
                print(f"\nContinuation de l'attaque avec un nouveau dictionnaire:")
                print(f"- Fichier hash : {hash_file}")
                print(f"- Type de hash : {hash_type}")
                print(f"- Longueur des mots : {word_length} caractères")
                print(f"- Charset : {''.join(sorted(charset))}")
                if rules:
                    print(f"- Règles : {', '.join(str(r) for r in rules)}")
            
            # Création de la nouvelle session
            new_config = {
                "name": session["name"],
                "hash_file": str(hash_file.resolve()),  # Chemin absolu du fichier de hash
                "hash_type": hash_type,
                "word_length": word_length,
                "charset": list(charset),
                "attack_mode": session.get("attack_mode", "straight"),
                "rules": [str(r) for r in rules] if rules else None,
                "mask": session.get("mask"),
                "options": session.get("options"),
                "start_time": datetime.now().isoformat(),
                "previous_session": session_id,
                "status": "created"
            }
            
            # Création de la session avant de lancer l'attaque
            self.session_manager.create_session(session["name"], new_config)
            self.logger.info(f"Nouvelle session créée: {new_session_id}")
            
            # Génération du nouveau dictionnaire
            self._generate_dictionary(generator, dict_file, verbose=verbose)
            self.logger.info(f"Nouveau dictionnaire généré: {dict_file}")
            
            # Lancement de l'attaque
            process = self.hashcat.start_attack(
                hash_file=hash_file,
                attack_mode=session.get("attack_mode", "straight"),
                hash_type=hash_type,
                dictionary=dict_file,
                rules=rules,
                session=new_session_id,
                options={
                    "status-timer": 10,
                    **(session.get("options") or {})
                }
            )
            self.logger.info(f"Nouvelle attaque démarrée avec PID {process.pid}")

            # Stockage du processus
            self._active_processes[new_session_id] = process
            if verbose:
                print(f"Nouvelle attaque démarrée avec la session {new_session_id}")
                print(f"Processus enregistré: PID {process.pid}")

            # Mise à jour du statut
            self.session_manager.update_session(new_session_id, {
                "process_pid": process.pid,
                "dictionary_file": str(dict_file),
                "status": "running"
            })

            return new_session_id

        except Exception as e:
            self.logger.error(f"Erreur lors de la continuation de l'attaque: {str(e)}", exc_info=True)
            raise RuntimeError(f"Erreur lors de la continuation de l'attaque: {str(e)}") 