"""
Tests unitaires pour le générateur de dictionnaire
"""
import pytest
from src.generator import DictionaryGenerator


def test_init_default_params():
    """Test l'initialisation avec les paramètres par défaut"""
    generator = DictionaryGenerator()
    assert generator.length == 18
    assert len(generator.charset) == 36  # 26 lettres majuscules + 10 chiffres


def test_init_custom_params():
    """Test l'initialisation avec des paramètres personnalisés"""
    generator = DictionaryGenerator(length=5, charset={'A', 'B', '1', '2'})
    assert generator.length == 5
    assert generator.charset == {'A', 'B', '1', '2'}
    assert generator._total_combinations == 4 ** 5


def test_validate_params_invalid():
    """Test la validation des paramètres invalides"""
    with pytest.raises(ValueError, match="La longueur doit être supérieure à 0"):
        DictionaryGenerator(length=0)
    
    with pytest.raises(ValueError, match="Le charset ne peut pas être vide"):
        DictionaryGenerator(charset=set())


def test_generate_batch_basic():
    """Test la génération d'un lot basique"""
    generator = DictionaryGenerator(length=3, charset={'A', 'B'})
    batch = generator.generate_batch(batch_size=4)
    
    assert len(batch) == 4
    assert all(len(word) == 3 for word in batch)
    assert all(all(c in {'A', 'B'} for c in word) for word in batch)
    assert len(set(batch)) == 4  # Vérifie l'unicité


def test_generate_batch_invalid_size():
    """Test la génération avec une taille invalide"""
    generator = DictionaryGenerator()
    with pytest.raises(ValueError, match="La taille du lot doit être supérieure à 0"):
        generator.generate_batch(batch_size=0)


def test_generate_batch_exceeding_combinations():
    """Test la génération avec une taille dépassant le nombre de combinaisons possibles"""
    generator = DictionaryGenerator(length=2, charset={'A', 'B'})  # 4 combinaisons possibles
    batch = generator.generate_batch(batch_size=10)
    
    assert len(batch) == 4  # Doit être limité au nombre total de combinaisons
    assert set(batch) == {'AA', 'AB', 'BA', 'BB'}


def test_generate_sequential_basic():
    """Test la génération séquentielle basique"""
    generator = DictionaryGenerator(length=2, charset={'A', 'B'})
    words = generator.generate_sequential(start_index=0, count=4)
    
    assert words == ['AA', 'AB', 'BA', 'BB']


def test_generate_sequential_with_start():
    """Test la génération séquentielle avec un index de départ"""
    generator = DictionaryGenerator(length=2, charset={'A', 'B'})
    words = generator.generate_sequential(start_index=2, count=2)
    
    assert words == ['BA', 'BB']


def test_generate_sequential_invalid_params():
    """Test la génération séquentielle avec des paramètres invalides"""
    generator = DictionaryGenerator(length=2, charset={'A', 'B'})
    
    with pytest.raises(ValueError, match="L'index de départ doit être positif ou nul"):
        generator.generate_sequential(start_index=-1)
    
    with pytest.raises(ValueError, match="Le nombre de mots à générer doit être supérieur à 0"):
        generator.generate_sequential(count=0)
    
    with pytest.raises(ValueError, match="L'index de départ dépasse le nombre total de combinaisons possibles"):
        generator.generate_sequential(start_index=4)


def test_memory_usage_estimation():
    """Test l'estimation de l'utilisation mémoire"""
    generator = DictionaryGenerator(length=10)
    memory = generator.estimate_memory_usage(batch_size=1000)
    
    assert memory == 1000 * (10 + 49)  # (longueur + overhead) * batch_size
    assert memory > 0 