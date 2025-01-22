"""
MyHashcat - Outil de génération de dictionnaires et d'interface avec Hashcat
"""

from .myhashcat import MyHashcat
from .generator import DictionaryGenerator
from .hashcat_interface import HashcatInterface
from .session_manager import SessionManager

__version__ = "0.1.0"
__all__ = ["MyHashcat", "DictionaryGenerator", "HashcatInterface", "SessionManager"] 