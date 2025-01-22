## Détection Automatique des Hash

### Description
Le système intègre maintenant une fonctionnalité de détection automatique du type de hash, permettant une utilisation plus simple et intuitive de l'outil.

### Fonctionnalités
- Détection des types de hash courants (MD5, SHA1, SHA256, SHA512, BCrypt, etc.)
- Analyse basée sur la longueur et le format du hash
- Support des formats Unix (SHA256/512 avec salt)
- Intégration transparente avec la création de session

### Types de Hash Supportés
| Type | ID Hashcat | Description |
|------|------------|-------------|
| MD5 | 0 | Hash de 32 caractères hexadécimaux |
| SHA1 | 100 | Hash de 40 caractères hexadécimaux |
| SHA256 | 1400 | Hash de 64 caractères hexadécimaux |
| SHA512 | 1700 | Hash de 128 caractères hexadécimaux |
| BCrypt | 3200 | Format $2[abxy]$... |
| SHA256 Unix | 7400 | Format $5$... |
| SHA512 Unix | 1800 | Format $6$... |
| PHPass | 400 | Format $P$... ou $H$... |

### Implémentation
- Classe `HashDetector` dédiée à la détection
- Utilisation d'expressions régulières pour l'analyse
- Tests unitaires complets
- Documentation détaillée

### Limitations
- Certains types de hash peuvent avoir des formats similaires
- La détection se base sur le premier hash valide trouvé dans le fichier
- Les hash modifiés ou corrompus peuvent ne pas être détectés 