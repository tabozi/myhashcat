"""
Module de détection automatique des types de hash
"""
import re
from typing import Optional, List, Dict, Any
from pathlib import Path


class HashDetector:
    """Détecteur automatique de types de hash"""

    # Définition des types de hash courants
    HASH_TYPES = {
        "MD5": {
            "id": 0,
            "length": 32,
            "pattern": r"^[a-fA-F0-9]{32}$"
        },
        "SHA1": {
            "id": 100,
            "length": 40,
            "pattern": r"^[a-fA-F0-9]{40}$"
        },
        "SHA256": {
            "id": 1400,
            "length": 64,
            "pattern": r"^[a-fA-F0-9]{64}$"
        },
        "SHA512": {
            "id": 1700,
            "length": 128,
            "pattern": r"^[a-fA-F0-9]{128}$"
        },
        "BCRYPT": {
            "id": 3200,
            "length": 60,
            "pattern": r"^\$2[abxy]\$\d+\$[a-zA-Z0-9./]{53}$"
        },
        "SHA256_UNIX": {
            "id": 7400,
            "pattern": r"^\$5\$.{1,16}\$[a-zA-Z0-9./]{43}$"
        },
        "SHA512_UNIX": {
            "id": 1800,
            "pattern": r"^\$6\$.{1,16}\$[a-zA-Z0-9./]{86}$"
        },
        "PHPASS": {
            "id": 400,
            "pattern": r"^\$[HP]\$[a-zA-Z0-9./]{31}$"
        },
        "WPA": {
            "id": 22000,
            "pattern": r"^WPA\*\d+\*[a-fA-F0-9]+\*[a-fA-F0-9]+\*[a-fA-F0-9]+$"
        }
    }

    @classmethod
    def detect_hash_type(cls, hash_str: str) -> Optional[Dict[str, Any]]:
        """
        Détecte le type d'un hash

        Args:
            hash_str (str): Hash à analyser

        Returns:
            Optional[Dict[str, Any]]: Informations sur le type de hash détecté ou None si non reconnu
        """
        # Nettoyage du hash
        hash_str = hash_str.strip()

        # Vérification de chaque type de hash
        for hash_name, hash_info in cls.HASH_TYPES.items():
            # Vérification de la longueur si spécifiée
            if "length" in hash_info and len(hash_str) != hash_info["length"]:
                continue

            # Vérification du pattern
            if re.match(hash_info["pattern"], hash_str):
                return {
                    "name": hash_name,
                    "id": hash_info["id"],
                    "description": f"Hash de type {hash_name}"
                }

        return None

    @classmethod
    def detect_from_file(cls, hash_file: Path) -> Optional[Dict[str, Any]]:
        """
        Détecte le type de hash à partir d'un fichier

        Args:
            hash_file (Path): Chemin vers le fichier contenant le(s) hash

        Returns:
            Optional[Dict[str, Any]]: Informations sur le type de hash détecté ou None si non reconnu
        """
        if not hash_file.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {hash_file}")

        # Vérifier d'abord si c'est un fichier au format 22000 (WPA/WPA2/WPA3)
        if hash_file.name.endswith('.22000'):
            return {
                "name": "WPA",
                "id": 22000,
                "description": "Hash de type WPA/WPA2/WPA3 (EAPOL)"
            }

        # Lecture de la première ligne non vide du fichier en mode binaire
        with hash_file.open("rb") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        # Tentative de décodage en UTF-8
                        decoded_line = line.decode('utf-8')
                        return cls.detect_hash_type(decoded_line)
                    except UnicodeDecodeError:
                        # Ignorer les lignes qui ne peuvent pas être décodées
                        continue

        return None 