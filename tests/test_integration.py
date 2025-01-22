"""
Tests d'intégration pour MyHashcat
"""
import pytest
from pathlib import Path
import subprocess
from unittest.mock import Mock, patch, ANY, mock_open
from src.myhashcat import MyHashcat


@pytest.fixture
def mock_hashcat():
    """Mock pour hashcat"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "v6.2.6 hashcat mock"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_process():
    """Mock pour le processus hashcat"""
    mock = Mock()
    mock.pid = 12345
    mock.poll.return_value = None
    mock.returncode = None
    return mock


@pytest.fixture
def myhashcat(tmp_path, mock_hashcat):
    """Fixture pour créer une instance de MyHashcat avec des répertoires temporaires"""
    work_dir = tmp_path / "work"
    sessions_dir = tmp_path / "sessions"
    instance = MyHashcat(
        hashcat_path="hashcat",
        work_dir=work_dir,
        sessions_dir=sessions_dir
    )
    yield instance
    instance.cleanup()


def test_init_directories(myhashcat):
    """Test la création des répertoires au démarrage"""
    assert myhashcat.work_dir.exists()
    assert myhashcat.dict_dir.exists()
    assert myhashcat.session_manager.sessions_dir.exists()


def test_create_attack_session(myhashcat, tmp_path, mock_process):
    """Test la création et le démarrage d'une session d'attaque"""
    # Préparation des fichiers
    hash_file = tmp_path / "hash.txt"
    hash_file.write_text("hash_to_crack")
    
    with patch('subprocess.Popen', return_value=mock_process):
        session_id = myhashcat.create_attack_session(
            name="test_session",
            hash_file=hash_file,
            hash_type=0,
            word_length=5,
            charset={'A', 'B', '1', '2'}
        )
        
        # Vérification de la session
        assert session_id is not None
        session = myhashcat.session_manager.load_session(session_id)
        assert session is not None
        assert session["status"] == "running"
        assert session["process_pid"] == mock_process.pid
        
        # Vérification du dictionnaire généré
        dict_file = Path(session["dictionary_file"])
        assert dict_file.exists()
        content = dict_file.read_text()
        assert len(content.splitlines()) > 0
        assert all(len(line) == 5 for line in content.splitlines())
        assert all(all(c in "AB12" for c in line) for line in content.splitlines())


def test_create_attack_session_with_rules(myhashcat, tmp_path, mock_process):
    """Test la création d'une session avec des règles"""
    hash_file = tmp_path / "hash.txt"
    rule_file = tmp_path / "rule.txt"
    hash_file.touch()
    rule_file.touch()
    
    with patch('subprocess.Popen', return_value=mock_process):
        session_id = myhashcat.create_attack_session(
            name="test_with_rules",
            hash_file=hash_file,
            hash_type=0,
            rules=[rule_file]
        )
        
        session = myhashcat.session_manager.load_session(session_id)
        assert session["rules"] == [str(rule_file)]


def test_get_session_status_running(myhashcat, tmp_path, mock_process):
    """Test la récupération du statut d'une session en cours"""
    hash_file = tmp_path / "hash.txt"
    hash_file.touch()
    
    with patch('subprocess.Popen', return_value=mock_process):
        session_id = myhashcat.create_attack_session(
            name="test_status",
            hash_file=hash_file,
            hash_type=0
        )
        
        with patch('builtins.open', mock_open(read_data="Name: test\nStatus: running")):
            status = myhashcat.get_session_status(session_id)
            assert status["status"] == "running"


def test_get_session_status_finished(myhashcat, tmp_path, mock_process):
    """Test la récupération du statut d'une session terminée"""
    hash_file = tmp_path / "hash.txt"
    hash_file.touch()
    
    with patch('subprocess.Popen', return_value=mock_process):
        session_id = myhashcat.create_attack_session(
            name="test_finished",
            hash_file=hash_file,
            hash_type=0
        )
        
        # Simuler un processus terminé
        with patch('builtins.open', side_effect=FileNotFoundError):
            status = myhashcat.get_session_status(session_id)
            assert status["status"] == "finished"


def test_stop_session(myhashcat, tmp_path, mock_process):
    """Test l'arrêt d'une session"""
    hash_file = tmp_path / "hash.txt"
    hash_file.touch()
    
    with patch('subprocess.Popen', return_value=mock_process):
        session_id = myhashcat.create_attack_session(
            name="test_stop",
            hash_file=hash_file,
            hash_type=0
        )
        
        myhashcat.stop_session(session_id)
        mock_process.terminate.assert_called_once()
        
        session = myhashcat.session_manager.load_session(session_id)
        assert session["status"] == "stopped"


def test_cleanup(myhashcat, tmp_path):
    """Test le nettoyage des ressources"""
    # Création de fichiers de test
    test_file = myhashcat.dict_dir / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.touch()
    
    myhashcat.cleanup()
    
    assert not test_file.exists()
    assert not myhashcat.dict_dir.exists()
    assert not myhashcat.work_dir.exists()


def test_invalid_session_id(myhashcat):
    """Test la gestion des sessions invalides"""
    with pytest.raises(ValueError, match="Session non trouvée"):
        myhashcat.get_session_status("invalid_session")
    
    with pytest.raises(ValueError, match="Session non trouvée"):
        myhashcat.stop_session("invalid_session") 