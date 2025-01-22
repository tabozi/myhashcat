"""
Module principal de MyHashcat intégrant tous les composants
"""
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .generator import DictionaryGenerator
from .hashcat_interface import HashcatInterface
from .session_manager import SessionManager
from .hash_detector import HashDetector


class MyHashcat:
    """Classe principale intégrant le générateur de dictionnaire avec Hashcat"""

    def __init__(
        self,
        hashcat_path: str = "hashcat",
        sessions_dir: Optional[Path] = None,
        work_dir: Optional[Path] = None
    ):
        """
        Initialise MyHashcat

        Args:
            hashcat_path (str): Chemin vers l'exécutable hashcat
            sessions_dir (Path, optional): Répertoire pour les sessions
            work_dir (Path, optional): Répertoire de travail
        """
        # Configuration des chemins par défaut
        default_base_dir = Path.home() / ".myhashcat"
        self.work_dir = work_dir or default_base_dir / "work"
        self.sessions_dir = sessions_dir or default_base_dir / "sessions"
        
        # Initialisation des composants
        self.hashcat = HashcatInterface(hashcat_path=hashcat_path)
        self.session_manager = SessionManager(sessions_dir=self.sessions_dir)
        self._active_processes = {}  # Stockage des processus actifs
        
        # Création des répertoires nécessaires
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.dict_dir = self.work_dir / "dictionaries"
        self.dict_dir.mkdir(exist_ok=True)

    def create_attack_session(
        self,
        name: str,
        hash_file: Path,
        hash_type: Optional[int] = None,
        word_length: int = 18,
        charset: Optional[set] = None,
        attack_mode: str = "straight",
        rules: Optional[List[Path]] = None,
        mask: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crée et démarre une nouvelle session d'attaque

        Args:
            name (str): Nom de la session
            hash_file (Path): Fichier contenant le hash à cracker
            hash_type (Optional[int]): Type de hash (voir --help de hashcat). Si non spécifié, détection automatique
            word_length (int): Longueur des mots à générer
            charset (set, optional): Ensemble des caractères à utiliser
            attack_mode (str): Mode d'attaque
            rules (List[Path], optional): Liste des fichiers de règles
            mask (str, optional): Masque pour les attaques par force brute
            options (Dict[str, Any], optional): Options supplémentaires

        Returns:
            str: Identifiant de la session

        Raises:
            ValueError: Si le type de hash n'est pas spécifié et n'a pas pu être détecté
        """
        # Détection automatique du type de hash si non spécifié
        if hash_type is None:
            detected = HashDetector.detect_from_file(hash_file)
            if detected:
                hash_type = detected["id"]
                print(f"Type de hash détecté : {detected['name']} (ID: {detected['id']})")
            else:
                raise ValueError("Impossible de détecter automatiquement le type de hash. Veuillez le spécifier manuellement.")

        # Configuration de la session
        config = {
            "hash_file": str(hash_file),
            "hash_type": hash_type,
            "word_length": word_length,
            "charset": list(charset) if charset else None,
            "attack_mode": attack_mode,
            "rules": [str(r) for r in rules] if rules else None,
            "mask": mask,
            "options": options,
            "start_time": datetime.now().isoformat()
        }

        # Création de la session
        session_id = self.session_manager.create_session(name, config)

        # Initialisation du générateur
        generator = DictionaryGenerator(length=word_length, charset=charset)

        # Création du dictionnaire initial
        dict_file = self.dict_dir / f"{session_id}_initial.txt"
        self._generate_dictionary(generator, dict_file)

        # Lancement de l'attaque
        process = self.hashcat.start_attack(
            hash_file=hash_file,
            attack_mode=attack_mode,
            hash_type=hash_type,
            dictionary=dict_file,
            rules=rules,
            mask=mask,
            session=session_id,
            options=options
        )

        # Stockage du processus
        self._active_processes[session_id] = process
        print(f"Processus enregistré pour la session {session_id}: PID {process.pid}")

        # Mise à jour de la session
        self.session_manager.update_session(session_id, {
            "process_pid": process.pid,
            "dictionary_file": str(dict_file),
            "status": "running",
            "rules": [str(r) for r in rules] if rules else None
        })

        return session_id

    def _generate_dictionary(
        self,
        generator: DictionaryGenerator,
        output_file: Path,
        batch_size: int = 10000
    ) -> None:
        """
        Génère un dictionnaire et l'écrit dans un fichier

        Args:
            generator (DictionaryGenerator): Générateur à utiliser
            output_file (Path): Fichier de sortie
            batch_size (int): Taille du lot de mots à générer
        """
        words = generator.generate_batch(batch_size=batch_size)
        with output_file.open("w") as f:
            for word in words:
                f.write(f"{word}\n")

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
                print(f"Vérification du processus pour la session {session_id}: PID {process.pid}")
                # Vérification si le processus est toujours en cours d'exécution
                if process.poll() is None:
                    progress = self.hashcat.get_progress(process)
                    session.update(progress)
                else:
                    print(f"Le processus pour la session {session_id} est déjà terminé.")
                    session["status"] = "finished"
                    self.session_manager.update_session(session_id, {"status": "finished"})
                    self._active_processes.pop(session_id, None)
            else:
                print(f"Aucun processus trouvé dans _active_processes pour la session {session_id}")
                # Mise à jour du statut pour refléter l'absence de processus
                session["status"] = "finished"
                self.session_manager.update_session(session_id, {"status": "finished"})

        return session

    def stop_session(self, session_id: str) -> None:
        """
        Arrête une session en cours

        Args:
            session_id (str): Identifiant de la session
        """
        session = self.session_manager.load_session(session_id)
        if not session:
            raise ValueError(f"Session non trouvée: {session_id}")

        process = self._active_processes.get(session_id)
        if process:
            # Vérification si le processus est toujours en cours d'exécution
            if process.poll() is None:
                print(f"Arrêt du processus pour la session: {session_id}")
                self.hashcat.stop_attack(process)
            self._active_processes.pop(session_id, None)

        # Mise à jour du statut de la session
        self.session_manager.update_session(session_id, {"status": "stopped"})
        print(f"Session {session_id} arrêtée")

    def cleanup(self) -> None:
        """Nettoie les ressources temporaires"""
        # Arrêt des processus actifs
        active_sessions = list(self._active_processes.keys())  # Copie des clés
        for session_id in active_sessions:
            try:
                self.stop_session(session_id)
            except Exception as e:
                print(f"Erreur lors de l'arrêt de la session {session_id}: {e}")
        self._active_processes.clear()

        # Nettoyage de l'interface Hashcat
        self.hashcat.cleanup()

        # Suppression des sessions terminées ou arrêtées
        for session_id in self.session_manager.list_sessions():
            session = self.session_manager.load_session(session_id)
            if session and (session.get("status") in ["finished", "stopped"]):
                try:
                    self.session_manager.delete_session(session_id)
                    print(f"Session {session_id} supprimée.")
                except Exception as e:
                    print(f"Erreur lors de la suppression de la session {session_id}: {e}")

        # Suppression des dictionnaires
        if self.dict_dir.exists():
            for file in self.dict_dir.glob("*"):
                try:
                    file.unlink()
                except OSError as e:
                    print(f"Erreur lors de la suppression du fichier {file}: {e}")
            try:
                self.dict_dir.rmdir()
            except OSError as e:
                print(f"Erreur lors de la suppression du répertoire {self.dict_dir}: {e}")

        # Suppression du répertoire de travail
        if self.work_dir.exists():
            try:
                self.work_dir.rmdir()
            except OSError as e:
                print(f"Erreur lors de la suppression du répertoire {self.work_dir}: {e}") 