"""
Tests unitaires pour l'interface Hashcat
"""
import pytest
from pathlib import Path
import subprocess
from unittest.mock import Mock, patch
from src.hashcat_interface import HashcatInterface


@pytest.fixture
def hashcat_interface():
    """Fixture pour créer une instance de HashcatInterface avec un mock de hashcat"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "v6.2.6 hashcat mock"
        mock_run.return_value.stderr = ""
        interface = HashcatInterface()
        yield interface


@pytest.fixture
def mock_temp_dir(tmp_path):
    """Fixture pour créer un répertoire temporaire"""
    with patch('tempfile.mkdtemp', return_value=str(tmp_path)):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "v6.2.6 hashcat mock"
            mock_run.return_value.stderr = ""
            interface = HashcatInterface()
            interface.temp_dir = tmp_path
            yield tmp_path, interface


def test_init_default(hashcat_interface):
    """Test l'initialisation avec les paramètres par défaut"""
    assert hashcat_interface.hashcat_path == "hashcat"
    assert "hashcat" in hashcat_interface.version.lower()


def test_init_custom_path():
    """Test l'initialisation avec un chemin personnalisé"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "v6.2.6 hashcat mock"
        interface = HashcatInterface(hashcat_path="/usr/local/bin/hashcat")
        assert interface.hashcat_path == "/usr/local/bin/hashcat"


def test_validate_hashcat_not_found():
    """Test la validation quand hashcat n'est pas trouvé"""
    with pytest.raises(RuntimeError, match="Hashcat non trouvé"):
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            HashcatInterface()


def test_validate_hashcat_error():
    """Test la validation quand hashcat retourne une erreur"""
    with pytest.raises(RuntimeError, match="Erreur lors de l'exécution"):
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "hashcat")):
            HashcatInterface()


def test_validate_hashcat_invalid_version():
    """Test la validation avec une version non reconnue"""
    with pytest.raises(RuntimeError, match="Version de Hashcat non reconnue"):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "invalid version"
            HashcatInterface()


def test_start_attack_basic(hashcat_interface, tmp_path):
    """Test le lancement d'une attaque basique"""
    hash_file = tmp_path / "hash.txt"
    hash_file.touch()
    
    with patch('subprocess.Popen') as mock_popen:
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        process = hashcat_interface.start_attack(
            hash_file=hash_file,
            attack_mode="straight",
            hash_type=0
        )
        
        assert process == mock_process
        mock_popen.assert_called_once()
        cmd = mock_popen.call_args[0][0]
        assert "--quiet" in cmd
        assert "-m" in cmd
        assert "-a" in cmd
        assert str(hash_file) in cmd


def test_start_attack_with_dictionary(hashcat_interface, tmp_path):
    """Test le lancement d'une attaque avec dictionnaire"""
    hash_file = tmp_path / "hash.txt"
    dict_file = tmp_path / "dict.txt"
    hash_file.touch()
    dict_file.touch()
    
    with patch('subprocess.Popen') as mock_popen:
        hashcat_interface.start_attack(
            hash_file=hash_file,
            attack_mode="straight",
            hash_type=0,
            dictionary=dict_file
        )
        
        cmd = mock_popen.call_args[0][0]
        assert str(dict_file) in cmd


def test_start_attack_invalid_files(hashcat_interface, tmp_path):
    """Test le lancement avec des fichiers invalides"""
    non_existent = tmp_path / "non_existent.txt"
    
    with pytest.raises(ValueError, match="Fichier de hash non trouvé"):
        hashcat_interface.start_attack(
            hash_file=non_existent,
            attack_mode="straight",
            hash_type=0
        )


def test_start_attack_invalid_mode(hashcat_interface, tmp_path):
    """Test le lancement avec un mode invalide"""
    hash_file = tmp_path / "hash.txt"
    hash_file.touch()
    
    with pytest.raises(ValueError, match="Mode d'attaque invalide"):
        hashcat_interface.start_attack(
            hash_file=hash_file,
            attack_mode="invalid_mode",
            hash_type=0
        )


def test_get_progress_finished(hashcat_interface):
    """Test la récupération de la progression d'une attaque terminée"""
    mock_process = Mock()
    mock_process.poll.return_value = 0
    mock_process.returncode = 0
    
    progress = hashcat_interface.get_progress(mock_process)
    assert progress["status"] == "finished"
    assert progress["return_code"] == 0


def test_get_progress_running(hashcat_interface):
    """Test la récupération de la progression d'une attaque en cours"""
    mock_process = Mock()
    mock_process.poll.return_value = None
    
    progress = hashcat_interface.get_progress(mock_process)
    assert progress["status"] == "running"
    assert "timestamp" in progress


def test_stop_attack(hashcat_interface):
    """Test l'arrêt d'une attaque"""
    mock_process = Mock()
    mock_process.poll.return_value = None
    
    hashcat_interface.stop_attack(mock_process)
    mock_process.terminate.assert_called_once()


def test_cleanup(mock_temp_dir):
    """Test le nettoyage des fichiers temporaires"""
    temp_dir, interface = mock_temp_dir
    test_file = temp_dir / "test.txt"
    test_file.touch()
    
    interface.cleanup()
    assert not test_file.exists()
    assert not temp_dir.exists() 