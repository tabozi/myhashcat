"""
Module d'interface avec Hashcat
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class HashcatInterface:
    """Classe pour interagir avec Hashcat"""

    ATTACK_MODES = {
        'straight': 0,    # Attaque en ligne droite
        'combination': 1, # Attaque par combinaison
        'bruteforce': 3,  # Attaque par force brute avec masque
        'hybrid': 6      # Attaque hybride dict + mask
    }

    def __init__(self, hashcat_path: str = "hashcat"):
        """
        Initialise l'interface Hashcat

        Args:
            hashcat_path (str): Chemin vers l'exécutable hashcat
        """
        self.hashcat_path = hashcat_path
        self.version = self._validate_hashcat()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="myhashcat_"))

    def _validate_hashcat(self) -> str:
        """
        Vérifie que Hashcat est disponible et fonctionnel

        Returns:
            str: Version de Hashcat

        Raises:
            RuntimeError: Si Hashcat n'est pas disponible ou ne fonctionne pas
        """
        try:
            result = subprocess.run(
                [self.hashcat_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            if "hashcat" not in version.lower():
                raise RuntimeError("Version de Hashcat non reconnue")
            return version
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de l'exécution de Hashcat: {e}")
        except FileNotFoundError:
            raise RuntimeError(f"Hashcat non trouvé à l'emplacement: {self.hashcat_path}")

    def start_attack(
        self,
        hash_file: Path,
        attack_mode: str,
        hash_type: int,
        dictionary: Optional[Path] = None,
        rules: Optional[List[Path]] = None,
        session: Optional[str] = None,
        mask: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> subprocess.Popen:
        """
        Lance une attaque Hashcat

        Args:
            hash_file (Path): Fichier contenant le hash à cracker
            attack_mode (str): Mode d'attaque ('straight', 'combination', 'bruteforce', 'hybrid')
            hash_type (int): Type de hash (voir --help de hashcat)
            dictionary (Path, optional): Chemin vers le dictionnaire
            rules (List[Path], optional): Liste des fichiers de règles
            session (str, optional): Nom de la session
            mask (str, optional): Masque pour les attaques par force brute
            options (Dict[str, Any], optional): Options supplémentaires pour hashcat

        Returns:
            subprocess.Popen: Process Hashcat

        Raises:
            ValueError: Si les paramètres sont invalides
            RuntimeError: Si l'attaque ne peut pas être lancée
        """
        if not hash_file.exists():
            raise ValueError(f"Fichier de hash non trouvé: {hash_file}")

        if attack_mode not in self.ATTACK_MODES:
            raise ValueError(f"Mode d'attaque invalide: {attack_mode}")

        if dictionary is not None and not dictionary.exists():
            raise ValueError(f"Dictionnaire non trouvé: {dictionary}")

        if rules:
            for rule in rules:
                if not rule.exists():
                    raise ValueError(f"Fichier de règles non trouvé: {rule}")

        # Construction de la commande
        cmd = [
            self.hashcat_path,
            "--quiet",
            "--status",
            "--status-timer", "1",
            "--outfile", str(self.temp_dir / "cracked.txt"),
            "-m", str(hash_type),
            "-a", str(self.ATTACK_MODES[attack_mode]),
            str(hash_file)
        ]

        # Ajout du dictionnaire si nécessaire
        if dictionary:
            cmd.append(str(dictionary))

        # Ajout du masque si nécessaire
        if mask:
            if attack_mode in ['bruteforce', 'hybrid']:
                cmd.append(mask)
            else:
                raise ValueError("Le masque n'est utilisable qu'en mode bruteforce ou hybrid")

        # Ajout des règles
        if rules:
            for rule in rules:
                cmd.extend(["-r", str(rule)])

        # Ajout du nom de session
        if session:
            cmd.extend(["--session", session])

        # Ajout des options supplémentaires
        if options:
            for key, value in options.items():
                if len(key) == 1:
                    cmd.append(f"-{key}")
                else:
                    cmd.append(f"--{key}")
                if value is not None:
                    cmd.append(str(value))

        try:
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Erreur lors du lancement de l'attaque: {e}")

    def get_progress(self, process: subprocess.Popen) -> Dict[str, Any]:
        """
        Récupère la progression d'une attaque en cours

        Args:
            process (subprocess.Popen): Process Hashcat en cours

        Returns:
            Dict[str, Any]: Informations sur la progression
        """
        if process.poll() is not None:
            return {"status": "finished", "return_code": process.returncode}

        # Lecture de la sortie standard
        progress = {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "speed": None,
            "progress": None,
            "estimated_completion": None,
            "recovered_hashes": None
        }

        return progress

    def stop_attack(self, process: subprocess.Popen) -> None:
        """
        Arrête une attaque en cours

        Args:
            process (subprocess.Popen): Process Hashcat à arrêter
        """
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    def cleanup(self) -> None:
        """Nettoie les fichiers temporaires"""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                try:
                    file.unlink()
                except OSError:
                    pass
            try:
                self.temp_dir.rmdir()
            except OSError:
                pass 