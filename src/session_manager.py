"""
Module de gestion des sessions pour MyHashcat
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class SessionManager:
    """Gestionnaire de sessions pour MyHashcat"""

    def __init__(self, sessions_dir: Path = Path("sessions")):
        """
        Initialise le gestionnaire de sessions

        Args:
            sessions_dir (Path): Répertoire de stockage des sessions
        """
        self.sessions_dir = sessions_dir
        self._ensure_sessions_dir()

    def _ensure_sessions_dir(self) -> None:
        """Crée le répertoire des sessions s'il n'existe pas"""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, name: str, config: Dict[str, Any]) -> str:
        """
        Crée une nouvelle session

        Args:
            name (str): Nom de la session
            config (Dict[str, Any]): Configuration de la session

        Returns:
            str: Identifiant de la session
        """
        session_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_data = {
            "id": session_id,
            "name": name,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "progress": 0
        }
        
        self._save_session(session_id, session_data)
        return session_id

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Charge une session existante

        Args:
            session_id (str): Identifiant de la session

        Returns:
            Optional[Dict[str, Any]]: Données de la session ou None si non trouvée
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with session_file.open("r") as f:
            return json.load(f)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """
        Met à jour une session existante

        Args:
            session_id (str): Identifiant de la session
            updates (Dict[str, Any]): Mises à jour à appliquer

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return False

        session_data.update(updates)
        session_data["updated_at"] = datetime.now().isoformat()
        self._save_session(session_id, session_data)
        return True

    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Liste toutes les sessions existantes

        Returns:
            Dict[str, Dict[str, Any]]: Dictionnaire des sessions avec leur ID comme clé
        """
        sessions = {}
        for session_file in self.sessions_dir.glob("*.json"):
            session_id = session_file.stem
            session_data = self.load_session(session_id)
            if session_data:
                sessions[session_id] = session_data
        return sessions

    def _save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Sauvegarde les données d'une session

        Args:
            session_id (str): Identifiant de la session
            data (Dict[str, Any]): Données à sauvegarder
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        with session_file.open("w") as f:
            json.dump(data, f, indent=2)

    def delete_session(self, session_id: str) -> bool:
        """
        Supprime une session existante

        Args:
            session_id (str): Identifiant de la session

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            try:
                session_file.unlink()
                return True
            except OSError as e:
                print(f"Erreur lors de la suppression du fichier de session {session_id}: {e}")
                return False
        return False 