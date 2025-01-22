"""
Module de génération de dictionnaire pour MyHashcat
"""
import string
from typing import List, Set


class DictionaryGenerator:
    """Classe pour générer des dictionnaires de mots de passe à la volée"""

    def __init__(
        self,
        length: int = 18,
        charset: Set[str] = None,
    ):
        """
        Initialise le générateur de dictionnaire

        Args:
            length (int): Longueur des mots à générer
            charset (Set[str]): Ensemble des caractères à utiliser
        """
        self.length = length
        self.charset = charset or set(string.ascii_uppercase + string.digits)
        self._validate_params()

    def _validate_params(self) -> None:
        """Valide les paramètres du générateur"""
        if self.length < 1:
            raise ValueError("La longueur doit être supérieure à 0")
        if not self.charset:
            raise ValueError("Le charset ne peut pas être vide")

    def generate_batch(self, batch_size: int = 1000) -> List[str]:
        """
        Génère un lot de mots

        Args:
            batch_size (int): Nombre de mots à générer

        Returns:
            List[str]: Liste des mots générés
        """
        # TODO: Implémenter la logique de génération
        raise NotImplementedError("Méthode à implémenter") 