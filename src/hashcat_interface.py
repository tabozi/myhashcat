"""
Module d'interface avec Hashcat
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import time
import threading
import queue
import logging


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
        self.logger = logging.getLogger('myhashcat.hashcat')
        self.logger.info(f"Initialisation de l'interface Hashcat avec: {hashcat_path}")
        self.version = self._validate_hashcat()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="myhashcat_"))
        self.logger.debug(f"Répertoire temporaire créé: {self.temp_dir}")

    def _validate_hashcat(self) -> str:
        """
        Vérifie que Hashcat est disponible et fonctionnel

        Returns:
            str: Version de Hashcat

        Raises:
            RuntimeError: Si Hashcat n'est pas disponible ou ne fonctionne pas
        """
        try:
            self.logger.debug("Vérification de la version de Hashcat")
            result = subprocess.run(
                [self.hashcat_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            version = result.stdout.strip()
            if not version:
                self.logger.error("Hashcat n'a retourné aucune version")
                raise RuntimeError("Hashcat n'a retourné aucune version")
            
            if not any(c.isdigit() for c in version):
                self.logger.error(f"Version de Hashcat non reconnue: {version}")
                raise RuntimeError(f"Version de Hashcat non reconnue: {version}")
            
            self.logger.info(f"Version de Hashcat validée: {version}")
            return version
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            self.logger.error(f"Erreur lors de l'exécution de Hashcat: {error_msg}")
            raise RuntimeError(f"Erreur lors de l'exécution de Hashcat: {error_msg}")
        except FileNotFoundError:
            self.logger.error(f"Hashcat non trouvé à l'emplacement: {self.hashcat_path}")
            raise RuntimeError(f"Hashcat non trouvé à l'emplacement: {self.hashcat_path}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la vérification de Hashcat: {str(e)}")
            raise RuntimeError(f"Erreur inattendue lors de la vérification de Hashcat: {str(e)}")

    def start_attack(
        self,
        hash_file: Path,
        attack_mode: str = "straight",
        hash_type: Optional[int] = None,
        dictionary: Optional[Path] = None,
        rules: Optional[List[Path]] = None,
        mask: Optional[str] = None,
        session: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        skip: Optional[int] = None,
        verbose: bool = False
    ) -> subprocess.Popen:
        """
        Lance une attaque Hashcat

        Args:
            hash_file (Path): Fichier contenant le hash
            attack_mode (str): Mode d'attaque (straight, rules, mask)
            hash_type (Optional[int]): Type de hash
            dictionary (Optional[Path]): Fichier dictionnaire
            rules (Optional[List[Path]]): Liste des fichiers de règles
            mask (Optional[str]): Masque pour l'attaque
            session (Optional[str]): Identifiant de session
            options (Dict[str, Any]): Options supplémentaires
            skip (Optional[int]): Nombre de mots à sauter dans le dictionnaire
            verbose (bool): Affiche la sortie de hashcat
        """
        self.logger.info(f"Démarrage d'une attaque Hashcat sur {hash_file}")
        self.logger.debug(f"Paramètres: mode={attack_mode}, type={hash_type}, dict={dictionary}, rules={rules}")

        # Création du répertoire temporaire
        self.temp_dir = tempfile.mkdtemp(prefix="myhashcat_")
        cracked_file = Path(self.temp_dir) / "cracked.txt"

        # Construction de la commande
        cmd = [
            self.hashcat_path,
            "--force",
            "--status",
            "--status-timer", "1",
            "--outfile", str(cracked_file)
        ]

        if hash_type is not None:
            cmd.extend(["-m", str(hash_type)])

        if attack_mode == "straight":
            cmd.extend(["-a", "0"])
        elif attack_mode == "rules":
            cmd.extend(["-a", "0"])
        elif attack_mode == "mask":
            cmd.extend(["-a", "3"])

        cmd.append(str(hash_file))

        if dictionary:
            cmd.append(str(dictionary))

        if rules:
            for rule in rules:
                cmd.extend(["-r", str(rule)])

        if mask:
            cmd.append(mask)

        if session:
            cmd.extend(["--session", session])

        # Ajout de l'option skip si spécifiée
        if skip is not None:
            cmd.extend(["--skip", str(skip)])

        # Ajout des options supplémentaires
        if options:
            for key, value in options.items():
                if isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                else:
                    cmd.extend([f"--{key}", str(value)])

        self.logger.debug(f"Commande Hashcat: {' '.join(cmd)}")

        if verbose:
            print("Démarrage d'une attaque Hashcat...")
            print(f"- Fichier hash: {hash_file}")
            print(f"- Mode d'attaque: {attack_mode}")
            print(f"- Type de hash: {hash_type}")
            print(f"- Dictionnaire: {dictionary}")
            print(f"- Règles: {rules}")
            if skip:
                print(f"- Skip: {skip} mots")
            print(f"Commande Hashcat: {' '.join(cmd)}")

        # Lancement du processus avec redirection de la sortie
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
            universal_newlines=True
        )

        self.logger.info(f"Processus Hashcat démarré avec PID {process.pid}")
        if verbose:
            print(f"Processus Hashcat démarré avec PID {process.pid}")

        return process

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
            self.logger.info(f"Arrêt du processus Hashcat PID {process.pid}")
            process.terminate()
            try:
                process.wait(timeout=5)
                self.logger.info("Processus terminé normalement")
            except subprocess.TimeoutExpired:
                self.logger.warning("Le processus ne répond pas, utilisation de kill")
                process.kill()
                self.logger.info("Processus tué")

    def cleanup(self) -> None:
        """Nettoie les fichiers temporaires"""
        self.logger.info("Nettoyage des fichiers temporaires")
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                try:
                    file.unlink()
                    self.logger.debug(f"Fichier supprimé: {file}")
                except OSError as e:
                    self.logger.error(f"Erreur lors de la suppression de {file}: {e}")
            try:
                self.temp_dir.rmdir()
                self.logger.info("Répertoire temporaire supprimé")
            except OSError as e:
                self.logger.error(f"Erreur lors de la suppression du répertoire temporaire: {e}") 