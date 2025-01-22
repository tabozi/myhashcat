"""
Module d'interface avec Hashcat
"""
import subprocess
from pathlib import Path
from typing import Optional, List


class HashcatInterface:
    """Classe pour interagir avec Hashcat"""

    def __init__(self, hashcat_path: str = "hashcat"):
        """
        Initialise l'interface Hashcat

        Args:
            hashcat_path (str): Chemin vers l'exécutable hashcat
        """
        self.hashcat_path = hashcat_path
        self._validate_hashcat()

    def _validate_hashcat(self) -> None:
        """Vérifie que Hashcat est disponible et fonctionnel"""
        try:
            result = subprocess.run(
                [self.hashcat_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            if "hashcat" not in result.stdout.lower():
                raise RuntimeError("Version de Hashcat non reconnue")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de l'exécution de Hashcat: {e}")
        except FileNotFoundError:
            raise RuntimeError(f"Hashcat non trouvé à l'emplacement: {self.hashcat_path}")

    def start_attack(
        self,
        hash_file: Path,
        attack_mode: int,
        hash_type: int,
        dictionary: Optional[Path] = None,
        rules: Optional[List[Path]] = None,
        session: Optional[str] = None
    ) -> subprocess.Popen:
        """
        Lance une attaque Hashcat

        Args:
            hash_file (Path): Fichier contenant le hash à cracker
            attack_mode (int): Mode d'attaque Hashcat
            hash_type (int): Type de hash
            dictionary (Path, optional): Chemin vers le dictionnaire
            rules (List[Path], optional): Liste des fichiers de règles
            session (str, optional): Nom de la session

        Returns:
            subprocess.Popen: Process Hashcat
        """
        # TODO: Implémenter la logique de lancement d'attaque
        raise NotImplementedError("Méthode à implémenter") 