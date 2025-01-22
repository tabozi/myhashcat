"""Tests pour le module de détection automatique des hash"""
import pytest
from pathlib import Path
import sys
import os

# Ajout du répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.hash_detector import HashDetector


def test_detect_md5():
    """Test de détection d'un hash MD5"""
    hash_str = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 de chaîne vide
    result = HashDetector.detect_hash_type(hash_str)
    assert result is not None
    assert result["name"] == "MD5"
    assert result["id"] == 0


def test_detect_sha1():
    """Test de détection d'un hash SHA1"""
    hash_str = "da39a3ee5e6b4b0d3255bfef95601890afd80709"  # SHA1 de chaîne vide
    result = HashDetector.detect_hash_type(hash_str)
    assert result is not None
    assert result["name"] == "SHA1"
    assert result["id"] == 100


def test_detect_sha256():
    """Test de détection d'un hash SHA256"""
    # SHA256 de chaîne vide
    hash_str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    result = HashDetector.detect_hash_type(hash_str)
    assert result is not None
    assert result["name"] == "SHA256"
    assert result["id"] == 1400


def test_detect_bcrypt():
    """Test de détection d'un hash BCrypt"""
    hash_str = "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LffR0WR/UX5X5HF.O"
    result = HashDetector.detect_hash_type(hash_str)
    assert result is not None
    assert result["name"] == "BCRYPT"
    assert result["id"] == 3200


def test_detect_unknown_hash():
    """Test avec un hash non reconnu"""
    hash_str = "invalid_hash"
    result = HashDetector.detect_hash_type(hash_str)
    assert result is None


def test_detect_from_file(tmp_path):
    """Test de détection à partir d'un fichier"""
    # Création d'un fichier temporaire avec un hash
    hash_file = tmp_path / "test_hash.txt"
    hash_file.write_text("d41d8cd98f00b204e9800998ecf8427e\n")

    result = HashDetector.detect_from_file(hash_file)
    assert result is not None
    assert result["name"] == "MD5"
    assert result["id"] == 0


def test_detect_from_empty_file(tmp_path):
    """Test avec un fichier vide"""
    hash_file = tmp_path / "empty.txt"
    hash_file.write_text("")

    result = HashDetector.detect_from_file(hash_file)
    assert result is None


def test_detect_from_nonexistent_file():
    """Test avec un fichier inexistant"""
    with pytest.raises(FileNotFoundError):
        HashDetector.detect_from_file(Path("nonexistent.txt")) 