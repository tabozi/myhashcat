"""
Module de génération de dictionnaire pour MyHashcat
"""
import string
import random
import math
from typing import List, Set, Iterator, Tuple
from itertools import product


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
        self.charset = charset if charset is not None else set(string.ascii_uppercase + string.digits)
        self._validate_params()
        self._charset_list = sorted(list(self.charset))  # Pour assurer un ordre constant
        self._total_combinations = len(self.charset) ** self.length

    def _validate_params(self) -> None:
        """Valide les paramètres du générateur"""
        if self.length < 1:
            raise ValueError("La longueur doit être supérieure à 0")
        if not self.charset:
            raise ValueError("Le charset ne peut pas être vide")

    def generate_batch(self, batch_size: int = 1000) -> List[str]:
        """
        Génère un lot de mots uniques

        Args:
            batch_size (int): Nombre de mots à générer

        Returns:
            List[str]: Liste des mots générés
        """
        if batch_size < 1:
            raise ValueError("La taille du lot doit être supérieure à 0")

        # Si on demande plus de mots que possible, on limite à la taille maximale
        batch_size = min(batch_size, self._total_combinations)
        
        # Génération aléatoire de mots uniques
        words = set()
        while len(words) < batch_size:
            word = ''.join(random.choices(self._charset_list, k=self.length))
            words.add(word)
        
        return sorted(list(words))

    def generate_sequential(self, start_index: int = 0, count: int = 1000) -> List[str]:
        """
        Génère un lot de mots séquentiellement à partir d'un index donné

        Args:
            start_index (int): Index de départ dans la séquence
            count (int): Nombre de mots à générer

        Returns:
            List[str]: Liste des mots générés
        """
        if start_index < 0:
            raise ValueError("L'index de départ doit être positif ou nul")
        if count < 1:
            raise ValueError("Le nombre de mots à générer doit être supérieur à 0")
        if start_index >= self._total_combinations:
            raise ValueError("L'index de départ dépasse le nombre total de combinaisons possibles")

        # Limite le compte au nombre de combinaisons restantes
        count = min(count, self._total_combinations - start_index)
        
        words = []
        for i in range(start_index, start_index + count):
            word = self._index_to_word(i)
            words.append(word)
        
        return words

    def _index_to_word(self, index: int) -> str:
        """
        Convertit un index en mot selon le charset

        Args:
            index (int): Index à convertir

        Returns:
            str: Mot généré
        """
        base = len(self._charset_list)
        word = []
        
        for _ in range(self.length):
            index, remainder = divmod(index, base)
            word.append(self._charset_list[remainder])
            
        return ''.join(reversed(word))

    def estimate_memory_usage(self, batch_size: int) -> int:
        """
        Estime l'utilisation mémoire pour un lot donné

        Args:
            batch_size (int): Taille du lot

        Returns:
            int: Estimation en octets
        """
        # Estimation approximative : chaque caractère = 1 octet + overhead Python
        return batch_size * (self.length + 49)  # 49 octets = overhead approximatif par string

    def estimate_dictionaries_needed(self, batch_size: int = 1_000_000) -> Tuple[int, float]:
        """
        Estime le nombre de dictionnaires nécessaires pour couvrir toutes les combinaisons possibles

        Args:
            batch_size (int): Nombre de mots par dictionnaire

        Returns:
            Tuple[int, float]: (nombre de dictionnaires, pourcentage de couverture)
        """
        if batch_size < 1:
            raise ValueError("La taille du lot doit être supérieure à 0")

        # Calcul du nombre de dictionnaires nécessaires
        dictionaries_needed = math.ceil(self._total_combinations / batch_size)
        
        # Calcul du pourcentage de couverture
        total_words = min(dictionaries_needed * batch_size, self._total_combinations)
        coverage = (total_words / self._total_combinations) * 100

        return dictionaries_needed, coverage

    def get_charset_info(self) -> Tuple[int, int, float]:
        """
        Retourne des informations sur le charset et les combinaisons possibles

        Returns:
            Tuple[int, int, float]: (taille du charset, nombre total de combinaisons, taille estimée en To)
        """
        charset_size = len(self.charset)
        total_combinations = self._total_combinations
        # Estimation de la taille totale en octets (longueur + overhead par mot)
        total_size_bytes = total_combinations * (self.length + 49)
        total_size_tb = total_size_bytes / (1024**4)  # Conversion en téraoctets
        
        return charset_size, total_combinations, total_size_tb 