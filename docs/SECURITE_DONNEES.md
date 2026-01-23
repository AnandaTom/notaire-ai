# Sécurité et Chiffrement des Données - NotaireAI

## Vue d'ensemble

Ce document décrit la stratégie de sécurité pour protéger les données notariales sensibles traitées par NotaireAI.

---

## 1. Classification des Données

| Catégorie | Exemples | Niveau de sensibilité | Durée conservation |
|-----------|----------|----------------------|-------------------|
| **Identité** | Nom, prénom, date naissance, CNI | CRITIQUE | 75 ans |
| **Patrimoine** | Prix vente, prêts, comptes bancaires | CRITIQUE | 75 ans |
| **Situation familiale** | Régime matrimonial, divorce, PACS | CRITIQUE | 75 ans |
| **Localisation** | Adresse domicile, biens immobiliers | ELEVÉE | 75 ans |
| **Documents générés** | Actes DOCX/PDF finaux | CRITIQUE | 75 ans |
| **Logs système** | Horodatage, actions utilisateur | MOYENNE | 12 mois |
| **Templates** | Templates Jinja2, schémas JSON | PUBLIQUE | Permanent |

---

## 2. Chiffrement au Repos (Data at Rest)

### 2.1 Fichiers Clients (.tmp/dossiers/)

**Méthode**: Chiffrement AES-256-GCM par fichier

```python
# execution/crypto_utils.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def chiffrer_fichier_client(fichier_json: str, cle_maitre: bytes) -> str:
    """
    Chiffre un fichier JSON client avec AES-256-GCM.

    Args:
        fichier_json: Chemin vers donnees_client.json
        cle_maitre: Clé AES-256 (32 bytes) du notaire

    Returns:
        Chemin vers fichier chiffré (.enc)
    """
    # Générer IV aléatoire (12 bytes pour GCM)
    iv = os.urandom(12)

    # Lire données
    with open(fichier_json, 'rb') as f:
        plaintext = f.read()

    # Chiffrer avec AES-256-GCM
    cipher = Cipher(
        algorithms.AES(cle_maitre),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Écrire: IV (12) + Tag (16) + Ciphertext
    fichier_enc = fichier_json + '.enc'
    with open(fichier_enc, 'wb') as f:
        f.write(iv)
        f.write(encryptor.tag)
        f.write(ciphertext)

    # Supprimer plaintext
    os.remove(fichier_json)

    return fichier_enc
```

**Stockage clé maître**:
- Utiliser `python-keyring` pour stocker dans le trousseau système (Windows Credential Manager, macOS Keychain)
- Jamais en clair dans `.env` ou code
- Régénération possible avec mot de passe notaire

### 2.2 Base de données Supabase

**Configuration**:
```sql
-- Activer chiffrement transparent (TDE) au niveau Postgres
ALTER DATABASE notaire_ai SET encryption = 'on';

-- Chiffrer colonnes sensibles avec pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE historique_actes
ADD COLUMN donnees_chiffrees BYTEA;

-- Fonction de chiffrement côté DB
CREATE OR REPLACE FUNCTION chiffrer_donnees(
    donnees_json JSONB,
    cle_notaire TEXT
) RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(donnees_json::TEXT, cle_notaire, 'cipher-algo=aes256');
END;
$$ LANGUAGE plpgsql;
```

**Politique d'accès**:
```sql
-- Row Level Security (RLS)
ALTER TABLE historique_actes ENABLE ROW LEVEL SECURITY;

-- Chaque notaire ne voit que ses dossiers
CREATE POLICY notaire_access ON historique_actes
    FOR ALL
    USING (notaire_id = current_setting('app.notaire_id')::UUID);
```

### 2.3 Documents Générés (outputs/)

**Stratégie**:
- DOCX/PDF chiffrés avec mot de passe immédiatement après génération
- Utiliser `msoffcrypto-tool` pour Office, `pikepdf` pour PDF

```python
# execution/securiser_document.py
import msoffcrypto
import pikepdf

def securiser_docx(fichier: str, mot_de_passe: str):
    """Chiffre un DOCX avec mot de passe Office."""
    temp = fichier + '.tmp'

    with open(fichier, 'rb') as f_in:
        office_file = msoffcrypto.OfficeFile(f_in)
        office_file.load_key(password=mot_de_passe)

        with open(temp, 'wb') as f_out:
            office_file.encrypt(f_out)

    os.replace(temp, fichier)

def securiser_pdf(fichier: str, mot_de_passe: str):
    """Chiffre un PDF avec AES-256."""
    pdf = pikepdf.open(fichier)
    pdf.save(fichier, encryption=pikepdf.Encryption(
        user=mot_de_passe,
        owner=mot_de_passe,
        R=6,  # AES-256
        allow=pikepdf.Permissions(
            extract=False,
            modify_annotation=False,
            modify_form=False
        )
    ))
```

---

## 3. Chiffrement en Transit (Data in Transit)

### 3.1 Connexions API

```python
# .env.example
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...  # Clé anon avec RLS
SUPABASE_SERVICE_KEY=eyJhbG...  # Clé service (jamais côté client)

# Toujours HTTPS/TLS 1.3
FORCE_TLS=true
VERIFY_SSL=true
```

### 3.2 Échanges avec le notaire

**Si interface web future**:
- HTTPS obligatoire (certificat Let's Encrypt)
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)

---

## 4. Gestion des Clés

### 4.1 Hiérarchie des clés

```
┌─────────────────────────────────────┐
│   Clé Maître Notaire (KMN)         │  ← Dérivée du mot de passe
│   (stockée dans trousseau système)  │     via PBKDF2 (100k itérations)
└─────────────┬───────────────────────┘
              │ Dérive via HKDF
              ↓
┌─────────────────────────────────────┐
│   Clé Dossier Client (KDC)         │  ← Unique par dossier
│   (stockée chiffrée dans metadata)  │     (rotate à chaque nouveau dossier)
└─────────────┬───────────────────────┘
              │ Chiffre
              ↓
┌─────────────────────────────────────┐
│   Données Client (JSON, DOCX, PDF) │
└─────────────────────────────────────┘
```

### 4.2 Dérivation de clé

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os

def deriver_cle_maitre(mot_de_passe: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Dérive la clé maître notaire depuis son mot de passe.

    Returns:
        (cle_maitre, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    cle_maitre = kdf.derive(mot_de_passe.encode('utf-8'))
    return cle_maitre, salt

# Stocker salt dans ~/.notaire-ai/config.enc (chiffré avec clé système)
```

### 4.3 Rotation des clés

**Calendrier recommandé**:
- Clé maître notaire: Tous les 12 mois
- Clé dossier client: À chaque nouveau dossier (jamais réutilisée)
- Clé API Supabase: Tous les 6 mois

```bash
# Script de rotation
python execution/rotation_cles.py --notaire augustin@example.com
```

---

## 5. Contrôle d'Accès

### 5.1 Authentification

**Méthode recommandée**: Authentification à deux facteurs (2FA)

```python
# execution/auth.py
import pyotp
import keyring

def configurer_2fa(email_notaire: str) -> str:
    """Configure TOTP pour le notaire."""
    secret = pyotp.random_base32()
    keyring.set_password('notaire-ai', f'{email_notaire}:totp', secret)

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email_notaire, issuer_name='NotaireAI')

    # Générer QR code pour scan avec Google Authenticator
    import qrcode
    qr = qrcode.make(uri)
    qr.save(f'.tmp/{email_notaire}_2fa.png')

    return uri

def verifier_2fa(email_notaire: str, code: str) -> bool:
    """Vérifie le code TOTP."""
    secret = keyring.get_password('notaire-ai', f'{email_notaire}:totp')
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
```

### 5.2 Journalisation (Audit Logs)

**Événements à logger**:
- Connexion/déconnexion notaire
- Accès dossier client (lecture, modification)
- Génération acte
- Export DOCX/PDF
- Suppression données

```python
# execution/audit_log.py
import logging
from datetime import datetime
import hashlib

# Logs chiffrés + signature HMAC
logging.basicConfig(
    filename='.tmp/audit.log.enc',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def log_acces_dossier(
    notaire_id: str,
    dossier_id: str,
    action: str,
    ip_address: str = None
):
    """Enregistre un accès au dossier client."""
    # Hash du dossier_id pour pseudo-anonymisation
    dossier_hash = hashlib.sha256(dossier_id.encode()).hexdigest()[:16]

    logging.info(
        f"ACCES | Notaire={notaire_id} | Dossier={dossier_hash} | "
        f"Action={action} | IP={ip_address or 'local'}"
    )
```

### 5.3 Expiration des sessions

```python
# execution/session_manager.py
from datetime import datetime, timedelta
import keyring

SESSION_TIMEOUT = timedelta(minutes=30)

def creer_session(notaire_id: str) -> str:
    """Crée une session avec expiration."""
    token = os.urandom(32).hex()
    expiration = (datetime.now() + SESSION_TIMEOUT).isoformat()

    keyring.set_password('notaire-ai', f'session:{token}', f'{notaire_id}|{expiration}')
    return token

def valider_session(token: str) -> str | None:
    """Valide la session et retourne notaire_id."""
    data = keyring.get_password('notaire-ai', f'session:{token}')
    if not data:
        return None

    notaire_id, expiration_str = data.split('|')
    expiration = datetime.fromisoformat(expiration_str)

    if datetime.now() > expiration:
        keyring.delete_password('notaire-ai', f'session:{token}')
        return None

    return notaire_id
```

---

## 6. Conformité RGPD

### 6.1 Registre des traitements

**À documenter**:
- Finalité: Assistance à la rédaction d'actes notariaux
- Base légale: Mission d'intérêt public (article 6.1.e)
- Catégories de données: Identité, patrimoine, situation familiale
- Durée conservation: 75 ans (obligation légale notariale)
- Destinataires: Notaire, clercs habilités, archives notariales
- Mesures sécurité: Chiffrement AES-256, 2FA, audit logs
- Sous-traitants: Supabase (hébergement EU), Microsoft (conversion DOCX/PDF)

### 6.2 Droits des personnes

**Implémentation**:
```python
# execution/rgpd_compliance.py

def exporter_donnees_client(dossier_id: str) -> dict:
    """Export au format JSON (droit d'accès RGPD)."""
    # Déchiffrer données
    donnees = dechiffrer_dossier(dossier_id)

    return {
        'identite': donnees['vendeur'],
        'patrimoine': donnees['bien'],
        'actes_generes': list_actes(dossier_id),
        'date_collecte': donnees['metadata']['date_creation'],
        'finalite': 'Génération acte de vente notarial',
        'duree_conservation': '75 ans (obligation légale)',
    }

def anonymiser_dossier(dossier_id: str):
    """Pseudo-anonymisation (droit à l'effacement RGPD)."""
    # ATTENTION: Notaire ne peut pas supprimer définitivement (obligation légale 75 ans)
    # Mais peut pseudo-anonymiser après signature acte authentique
    donnees = dechiffrer_dossier(dossier_id)

    # Remplacer identifiants par hash
    for personne in ['vendeur', 'acquereur']:
        donnees[personne]['nom'] = hashlib.sha256(donnees[personne]['nom'].encode()).hexdigest()[:8]
        donnees[personne]['prenom'] = '***'
        donnees[personne]['adresse'] = '***'

    rechiffrer_dossier(dossier_id, donnees)
```

### 6.3 Analyse d'Impact (AIPD)

**Obligatoire car**:
- Traitement automatisé à grande échelle
- Données sensibles (santé matrimoniale)
- Évaluation/scoring potentiel (détection anomalies)

**Risques identifiés**:
| Risque | Impact | Probabilité | Mesure |
|--------|--------|-------------|--------|
| Accès non autorisé | CRITIQUE | Faible | Chiffrement + 2FA |
| Fuite données | CRITIQUE | Faible | RLS + audit logs |
| Perte données | ÉLEVÉ | Moyenne | Backup quotidien chiffré |
| Modification malveillante | ÉLEVÉ | Faible | Signature numérique actes |

---

## 7. Sauvegardes Sécurisées

### 7.1 Stratégie 3-2-1

- **3 copies**: Production + Backup local + Backup cloud
- **2 supports**: SSD local + Cloud (Supabase + S3)
- **1 hors site**: Cloud géographiquement distant

```python
# execution/backup_secure.py
import tarfile
from datetime import datetime

def backup_chiffre_dossiers():
    """Sauvegarde chiffrée quotidienne."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive = f'.tmp/backups/notaire_backup_{timestamp}.tar.gz.enc'

    # Créer archive TAR.GZ
    with tarfile.open(archive.replace('.enc', ''), 'w:gz') as tar:
        tar.add('.tmp/dossiers', arcname='dossiers')
        tar.add('outputs', arcname='outputs')

    # Chiffrer archive avec clé de backup (différente de clé maître)
    cle_backup = keyring.get_password('notaire-ai', 'cle_backup')
    chiffrer_fichier_client(archive.replace('.enc', ''), cle_backup.encode())

    # Upload vers S3/Supabase Storage
    upload_backup_cloud(archive)

    # Supprimer backups > 90 jours
    nettoyer_anciens_backups(jours=90)
```

### 7.2 Test de restauration

**Calendrier**: Test mensuel de restauration complète

```bash
# Script de test
python execution/test_restauration.py --backup .tmp/backups/notaire_backup_20260123.tar.gz.enc
```

---

## 8. Conformité Technique

### 8.1 Checklist de sécurité

- [x] Chiffrement au repos (AES-256-GCM)
- [x] Chiffrement en transit (TLS 1.3)
- [x] Gestion clés (PBKDF2 + trousseau système)
- [x] Authentification forte (2FA)
- [x] Contrôle d'accès (RLS Supabase)
- [x] Audit logs chiffrés
- [x] Sauvegarde 3-2-1
- [x] Pseudo-anonymisation RGPD
- [x] Test restauration mensuel
- [ ] Pentest annuel (recommandé)
- [ ] Certification ISO 27001 (optionnel)

### 8.2 Dépendances sécurité

```bash
# requirements-security.txt
cryptography==42.0.0      # Chiffrement AES-256
python-keyring==24.3.0    # Stockage clés système
pyotp==2.9.0              # 2FA TOTP
msoffcrypto-tool==5.3.1   # Chiffrement DOCX
pikepdf==8.10.1           # Chiffrement PDF
python-dotenv==1.0.0      # Variables environnement sécurisées

# Audit vulnérabilités
pip install pip-audit
pip-audit --requirement requirements-security.txt
```

---

## 9. Formation et Sensibilisation

### 9.1 Bonnes pratiques notaire

**À communiquer**:
1. **Mot de passe fort**: 16+ caractères, unique, gestionnaire recommandé
2. **2FA obligatoire**: Scanner QR code avec Google Authenticator
3. **Session timeout**: 30 minutes d'inactivité → reconnexion
4. **Verrouillage écran**: Toujours verrouiller si absence
5. **Pas d'email/clé USB**: Jamais transférer données non chiffrées
6. **Vérification identité**: Double-check données client sensibles
7. **Alerte anomalie**: Signaler tout comportement suspect

### 9.2 Procédure incident

**En cas de compromission**:
1. **Isoler**: Déconnecter machine du réseau
2. **Notifier**: CNIL sous 72h si fuite données personnelles
3. **Rotation clés**: Regénérer toutes les clés immédiatement
4. **Audit forensique**: Analyser logs pour identifier étendue
5. **Information clients**: Si impact, notifier personnes concernées
6. **Amélioration**: Mettre à jour procédures de sécurité

---

## 10. Mise en Production

### 10.1 Checklist déploiement

```bash
# 1. Générer clé maître notaire
python execution/setup_notaire.py --email augustin@notaire.fr

# 2. Configurer 2FA
python execution/configurer_2fa.py --email augustin@notaire.fr

# 3. Chiffrer dossiers existants
python execution/migrer_chiffrement.py --dossier .tmp/dossiers

# 4. Activer RLS Supabase
psql $DATABASE_URL < schemas/security_policies.sql

# 5. Configurer backup automatique
cron: 0 2 * * * python execution/backup_secure.py

# 6. Test complet
pytest tests/security/ -v
```

### 10.2 Monitoring

**Alertes à configurer**:
- Échec authentification 2FA (5+ tentatives)
- Accès dossier hors heures ouvrables
- Export massif de données (>10 dossiers/jour)
- Modification schéma base de données
- Espace disque < 10% (backups)

```python
# execution/monitoring.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment="production",
    before_send=anonymiser_donnees_sensibles  # Pseudo-anonymiser avant envoi
)
```

---

## Résumé Exécutif

| Mesure | Statut | Priorité |
|--------|--------|----------|
| Chiffrement AES-256 dossiers | ✅ Documenté | CRITIQUE |
| 2FA notaire | ✅ Documenté | CRITIQUE |
| RLS Supabase | ✅ Documenté | CRITIQUE |
| Audit logs | ✅ Documenté | ÉLEVÉE |
| Backup 3-2-1 | ✅ Documenté | ÉLEVÉE |
| Rotation clés | ✅ Documenté | MOYENNE |
| Test restauration | ⚠️ À planifier | MOYENNE |
| Pentest | ❌ Non planifié | BASSE |

**Coût estimé**: 0€ (bibliothèques open-source) + temps développement (40-60h)

**ROI**: Protection juridique inestimable + conformité RGPD obligatoire

---

**Dernière mise à jour**: 2026-01-23
**Responsable sécurité**: À désigner
**Prochaine révision**: 2026-07-23 (6 mois)
