"""
Exemples d'utilisation de MyHashcat
"""
from pathlib import Path
from time import sleep
from src.myhashcat import MyHashcat


def exemple_basique():
    """Exemple d'utilisation basique"""
    print("=== Exemple Basique ===")
    
    # Initialisation
    hashcat = MyHashcat()
    
    # Création d'une session simple
    session_id = hashcat.create_attack_session(
        name="test_simple",
        hash_file=Path("hashes/md5.txt"),
        hash_type=0,  # MD5
        word_length=6,
        charset={'a', 'b', 'c', '1', '2', '3'}
    )
    
    # Suivi du statut
    for _ in range(3):
        status = hashcat.get_session_status(session_id)
        print(f"Statut: {status['status']}")
        sleep(1)
    
    # Arrêt et nettoyage
    hashcat.stop_session(session_id)
    hashcat.cleanup()


def exemple_avance():
    """Exemple avec configuration avancée"""
    print("\n=== Exemple Avancé ===")
    
    # Initialisation avec chemins personnalisés
    hashcat = MyHashcat(
        hashcat_path="/usr/local/bin/hashcat",
        sessions_dir=Path("mes_sessions"),
        work_dir=Path("temp_work")
    )
    
    # Session avec règles et options
    session_id = hashcat.create_attack_session(
        name="crack_ntlm",
        hash_file=Path("hashes/ntlm.txt"),
        hash_type=1000,  # NTLM
        word_length=8,
        charset={'A', 'B', 'C', '1', '2', '3', '@', '#'},
        attack_mode="straight",
        rules=[Path("rules/best64.rule")],
        options={
            "workload-profile": 3,
            "optimized-kernel-enable": True
        }
    )
    
    # Suivi détaillé
    status = hashcat.get_session_status(session_id)
    print(f"Configuration: {status.get('options', {})}")
    print(f"Règles utilisées: {status.get('rules', [])}")
    
    # Nettoyage
    hashcat.cleanup()


def exemple_multiple_sessions():
    """Exemple de gestion de plusieurs sessions"""
    print("\n=== Exemple Multi-Sessions ===")
    
    hashcat = MyHashcat()
    sessions = []
    
    # Création de plusieurs sessions
    for i in range(3):
        session_id = hashcat.create_attack_session(
            name=f"session_{i}",
            hash_file=Path(f"hashes/hash_{i}.txt"),
            hash_type=0,
            word_length=5 + i,
            charset={'a', 'b', 'c', str(i)}
        )
        sessions.append(session_id)
    
    # Suivi des sessions
    for session_id in sessions:
        status = hashcat.get_session_status(session_id)
        print(f"Session {session_id}: {status['status']}")
    
    # Arrêt de toutes les sessions
    for session_id in sessions:
        hashcat.stop_session(session_id)
    
    # Nettoyage final
    hashcat.cleanup()


if __name__ == "__main__":
    # Exécution des exemples
    try:
        exemple_basique()
        exemple_avance()
        exemple_multiple_sessions()
    except Exception as e:
        print(f"Erreur lors de l'exécution des exemples: {e}") 