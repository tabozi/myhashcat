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
        self.work_dir = work_dir or Path(tempfile.mkdtemp(prefix="myhashcat_"))
        self.hashcat = HashcatInterface(hashcat_path=hashcat_path)
        self.session_manager = SessionManager(sessions_dir=sessions_dir or self.work_dir / "sessions")
        self._active_processes = {}  # Stockage des processus actifs
        
        # Création des répertoires nécessaires
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.dict_dir = self.work_dir / "dictionaries"
        self.dict_dir.mkdir(exist_ok=True)

    def create_attack_session(
        self,
        name: str,
        hash_file: Path,
        hash_type: int,
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
            hash_type (int): Type de hash (voir --help de hashcat)
            word_length (int): Longueur des mots à générer
            charset (set, optional): Ensemble des caractères à utiliser
            attack_mode (str): Mode d'attaque
            rules (List[Path], optional): Liste des fichiers de règles
            mask (str, optional): Masque pour les attaques par force brute
            options (Dict[str, Any], optional): Options supplémentaires

        Returns:
            str: Identifiant de la session
        """
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
                try:
                    with open(f"/proc/{session['process_pid']}/status") as f:
                        if "running" in session["status"].lower():
                            progress = self.hashcat.get_progress(process)
                            session.update(progress)
                except FileNotFoundError:
                    session["status"] = "finished"
                    self.session_manager.update_session(session_id, {"status": "finished"})
                    self._active_processes.pop(session_id, None)

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
        if process and session["status"] == "running":
            self.hashcat.stop_attack(process)
            self.session_manager.update_session(session_id, {"status": "stopped"})
            self._active_processes.pop(session_id, None)

    def cleanup(self) -> None:
        """Nettoie les ressources temporaires"""
        # Arrêt des processus actifs
        active_sessions = list(self._active_processes.keys())  # Copie des clés
        for session_id in active_sessions:
            try:
                self.stop_session(session_id)
            except:
                pass
        self._active_processes.clear()

        # Nettoyage de l'interface Hashcat
        self.hashcat.cleanup()

        # Suppression des dictionnaires
        if self.dict_dir.exists():
            for file in self.dict_dir.glob("*"):
                try:
                    file.unlink()
                except OSError:
                    pass
            try:
                self.dict_dir.rmdir()
            except OSError:
                pass

        # Suppression du répertoire de travail
        if self.work_dir.exists():
            try:
                self.work_dir.rmdir()
            except OSError:
                pass 