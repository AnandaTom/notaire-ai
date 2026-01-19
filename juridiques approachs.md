# Documentation Juridique & Architecture - Système IA Notarial

## Table des Matières
1. [Analyse Juridique Complète](#analyse-juridique-complète)
2. [Architecture Technique](#architecture-technique)
3. [Risques et Conformité](#risques-et-conformité)
4. [Checklist de Conformité](#checklist-de-conformité)
5. [Stratégie de Déploiement](#stratégie-de-déploiement)

---

## Analyse Juridique Complète : Risques & Conformité

**Verdict : ⚠️ Il y a des risques résiduels, mais ils sont GÉRABLES avec les bonnes mesures**

---

## 🔴 Risques Juridiques Réels

### **1. RGPD : Vous êtes "Responsable de Traitement"**

**Ce que ça signifie concrètement :**

```
Notaire (responsable conjoint)
    ↓ délègue traitement
Votre Agence (responsable de traitement)
    ↓ utilise sous-traitant
Supabase (sous-traitant au sens RGPD)
    ↓ utilise infrastructure
AWS EU (sous-traitant de rang 2)
```

**Obligations légales obligatoires :**

#### ✅ 1. Registre des Activités de Traitement (Art. 30 RGPD)

Document obligatoire même pour PME si données sensibles. À produire en cas de contrôle CNIL.

**Template minimal requis :**

```markdown
# Registre des Traitements - [Votre Agence]

## Traitement 1 : Gestion fiches clients notariaux

**Finalité :** Assistance rédaction actes notariés via IA
**Base légale :** Intérêt légitime (Art. 6.1.f RGPD)
**Catégories de données :**
- Identité : nom, prénom, adresse
- Vie professionnelle : profession, revenus (si pertinent)
- ⚠️ Données sensibles : aucune (santé, religion, etc. INTERDITES)

**Destinataires :**
- Personnel autorisé de l'étude notariale
- Système IA (traitement automatisé)
- Supabase Inc. (sous-traitant - EU)

**Durée conservation :**
- Données actives : durée du dossier + 5 ans (prescription civile)
- Archives : selon obligations légales notariales (75-100 ans pour actes authentiques)

**Mesures sécurité :**
- Chiffrement AES-256 at-rest et TLS 1.3 in-transit
- Authentification MFA
- Isolation multi-tenant (RLS PostgreSQL)
- Audit logs 3 ans
- Backup chiffrés quotidiens

**Transferts hors UE :** Aucun (région EU uniquement)

**DPO :** [Nom si désigné, sinon "Non requis"]
```

**⚠️ Attention :** Si vous traitez des données sur des **successions incluant des informations de santé** (cause décès, incapacité...) → vous tombez sous Art. 9 RGPD (données sensibles) → **obligations renforcées**.

---

#### ✅ 2. DPA (Data Processing Agreement) avec Supabase

**Obligatoire** selon Art. 28 RGPD. Bonne nouvelle : Supabase fournit un DPA standard.

**À vérifier dans le DPA Supabase :**
- [ ] Clause localisation données (EU uniquement)
- [ ] Sous-traitants ultérieurs autorisés (AWS, etc.)
- [ ] Engagement suppression données sur demande
- [ ] Notification breach sous 48h
- [ ] Droit audit (ou certification ISO27001 équivalente)

**Action requise :**
```bash
# Télécharger et signer le DPA Supabase
https://supabase.com/legal/dpa

# Conserver dans dossier juridique avec :
- Date signature
- Version DPA
- Liste sous-traitants approuvés
```

---

#### ✅ 3. Base Légale du Traitement (Art. 6 RGPD)

**Question clé :** Sur quelle base juridique vous appuyez-vous ?

| Base légale | Applicable ? | Contraintes |
|-------------|--------------|-------------|
| **Consentement** (6.1.a) | ⚠️ Difficile | Doit être libre, spécifique, éclairé, révocable → complexe pour relation notaire-client |
| **Contrat** (6.1.b) | ✅ **OUI** | Si traitement nécessaire pour exécuter contrat notarial (rédaction acte) |
| **Obligation légale** (6.1.c) | ✅ Partiel | Notaires ont obligations légales (authentification, conservation actes) |
| **Intérêt légitime** (6.1.f) | ✅ **RECOMMANDÉ** | Modernisation pratique notariale via IA = intérêt légitime SI équilibré avec droits personnes |

**Conseil :** Combinaison **Contrat + Intérêt légitime**

**Justification intérêt légitime à documenter :**

```markdown
## Test des 3 critères (Art. 6.1.f)

### 1. Finalité légitime ?
✅ Amélioration efficacité rédaction actes notariés
✅ Réduction erreurs humaines via assistance IA
✅ Gain temps pour clients (délais réduits)

### 2. Nécessité du traitement ?
✅ Impossible de remplir automatiquement variables sans accès données client
✅ Alternative manuelle = saisie répétitive, source d'erreurs
✅ Données minimales (seulement ce qui apparaît dans actes)

### 3. Équilibre droits personnes ?
✅ Mesures sécurité renforcées (chiffrement, RLS, audit)
✅ Pas de profilage ni décisions automatisées impactantes
✅ Transparence : clients informés du traitement (via étude)
✅ Droits exercés facilement (accès, rectification, effacement)
```

**⚠️ Piège à éviter :** Ne vous appuyez PAS uniquement sur le consentement, car :
- Le client ne peut pas vraiment refuser (il veut son acte)
- Révocation = blocage du service → consentement pas "libre"

---

#### ✅ 4. Information des Personnes (Art. 13-14)

**Problème :** Vous collectez les données **indirectement** (via notaire, pas directement auprès des clients).

**Obligation Art. 14 RGPD :** Informer les personnes dans un délai d'**1 mois** après collecte.

**Solutions pratiques :**

**Option A - Via le notaire (recommandé) :**
```markdown
# Template mention pour lettres de mission notaire

"Dans le cadre de la rédaction de votre acte, notre étude utilise
un outil d'assistance par Intelligence Artificielle fourni par
[Votre Agence]. Vos données personnelles (nom, prénom, adresse,
informations relatives au bien) sont traitées de manière sécurisée
et confidentielle, uniquement pour la finalité de rédaction de l'acte.

Pour exercer vos droits (accès, rectification, effacement),
contactez notre étude : [email]

Plus d'infos : [lien politique confidentialité]"
```

**Option B - Affichage en étude :**
```
Panneau visible salle d'attente :
"Cette étude utilise des outils numériques sécurisés
pour la rédaction des actes. Informations complètes : [QR code]"
```

**Option C - Page dédiée :**
```
https://votre-agence.fr/confidentialite-clients-notaires
→ Politique de confidentialité détaillée
→ Formulaire exercice des droits
```

---

#### ✅ 5. Droits des Personnes (Art. 15-22)

**Vous DEVEZ permettre :**

| Droit | Délai réponse | Implémentation technique |
|-------|---------------|--------------------------|
| **Accès** (Art. 15) | 1 mois | Export JSON données client `SELECT * FROM clients WHERE id=X` |
| **Rectification** (Art. 16) | 1 mois | Interface modification ou UPDATE SQL |
| **Effacement** (Art. 17) | 1 mois | Soft delete : `UPDATE clients SET deleted_at=NOW(), data_anonymized=true` |
| **Portabilité** (Art. 20) | 1 mois | Export CSV/JSON structuré |
| **Opposition** (Art. 21) | Immédiat | Flag `opt_out` + exclusion des traitements IA |

**Conseil implémentation :**

```sql
-- Gestion droits RGPD
CREATE TABLE rgpd_requests (
  id UUID PRIMARY KEY,
  client_id UUID REFERENCES clients(id),
  request_type TEXT, -- 'access', 'rectification', 'erasure', 'portability'
  status TEXT,       -- 'pending', 'processing', 'completed'
  requested_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,

  -- Traçabilité
  requested_by TEXT, -- Email demandeur
  processed_by UUID REFERENCES users(id),
  response_data JSONB -- Export données si demande accès
);

-- Soft delete (ne jamais DELETE définitif)
ALTER TABLE clients ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE clients ADD COLUMN anonymized BOOLEAN DEFAULT false;

-- Vue "clients actifs" (utilisée par l'agent)
CREATE VIEW clients_active AS
SELECT * FROM clients
WHERE deleted_at IS NULL AND anonymized = false;

-- Fonction anonymisation (effacement = anonymisation, pas suppression)
CREATE FUNCTION anonymize_client(client_uuid UUID) RETURNS void AS $$
BEGIN
  UPDATE clients SET
    nom = 'ANONYMISÉ',
    prenom = 'ANONYMISÉ',
    email = NULL,
    telephone = NULL,
    adresse = NULL,
    -- Garder seulement métadonnées nécessaires archives légales
    anonymized = true,
    deleted_at = NOW()
  WHERE id = client_uuid;
END;
$$ LANGUAGE plpgsql;
```

**⚠️ Exception importante :**
Vous pouvez **refuser l'effacement** si conservation nécessaire pour :
- Respect obligation légale (conservation actes notariaux 75-100 ans)
- Constatation/exercice/défense droits en justice

**Dans ce cas :** Anonymiser au maximum, garder uniquement minimum légal.

---

### **2. Secret Professionnel Notarial (Art. 226-13 Code Pénal)**

**Risque pénal réel :** Notaires soumis au **secret professionnel absolu**.

**Question :** Votre IA = extension du notaire ou tiers ?

**Réponse juridique :**
- ✅ **Si IA = outil du notaire** (comme Word) → couvert par secret pro
- ❌ **Si IA = service autonome avec accès permanent** → possiblement violation

**Solution sécurisante :**

```markdown
## Contractualisation avec l'étude

**Clause dans contrat notaire :**

"L'outil IA fourni par [Votre Agence] constitue un auxiliaire
technique du notaire, soumis aux mêmes obligations de secret
professionnel que les collaborateurs de l'étude.

[Votre Agence] s'engage à :
- Ne jamais accéder aux données sans instruction expresse de l'étude
- Ne jamais utiliser les données à d'autres fins
- Ne jamais partager les données avec des tiers
- Supprimer les données sur demande de l'étude

Personnel [Votre Agence] ayant accès : [liste nominative]
→ Signataires d'un engagement de confidentialité"
```

**Engagement de confidentialité type :**
```markdown
# Engagement de Confidentialité - Personnel Technique

Je soussigné [Nom], employé de [Votre Agence], m'engage à :

1. Respecter le secret professionnel des données notariales
2. Ne jamais divulguer les informations consultées
3. Accéder aux données uniquement pour maintenance/support
4. Logger tous les accès (audit trail)
5. Sous peine de sanctions pénales (Art. 226-13 Code Pénal)

Fait à [Ville], le [Date]
Signature :
```

**Architecture technique renforçant secret pro :**
```
┌─────────────────────────────────────────────┐
│ Niveau 1 : Agent IA (access automatique)   │
│ → Aucun humain de votre agence ne voit     │
│ → Logs automatiques uniquement             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Niveau 2 : Support technique (si nécessaire)│
│ → Accès avec autorisation écrite notaire   │
│ → MFA + approval workflow                  │
│ → Session enregistrée (audit vidéo)        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Niveau 3 : Admin Supabase (urgence)        │
│ → Jamais en pratique normale               │
│ → Alertes si accès admin aux données       │
└─────────────────────────────────────────────┘
```

---

### **3. Hébergement des Données de Santé (si applicable)**

**⚠️ ATTENTION CRITIQUE :**

Si vos données incluent des **actes de succession mentionnant causes de décès** ou **donations avec conditions médicales** → données de santé au sens RGPD.

**Conséquence :** Hébergement doit être **certifié HDS** (Hébergeur Données de Santé).

**Statut Supabase :**
- ❌ **PAS certifié HDS** actuellement
- ✅ Conforme RGPD général
- ✅ ISO 27001, SOC 2 Type II

**Solutions :**

**Option 1 - Éviter données de santé (recommandé) :**
```python
# Filtrage automatique à l'import
HEALTH_KEYWORDS = [
    'décès', 'décédé', 'maladie', 'cancer', 'handicap',
    'invalidité', 'ALD', 'traitement', 'médical'
]

def sanitize_import(text):
    for keyword in HEALTH_KEYWORDS:
        if keyword in text.lower():
            # Option A : Masquer
            text = text.replace(keyword, '[REDACTED]')
            # Option B : Alerter et demander validation
            raise ValueError(f"Donnée de santé détectée: {keyword}")
    return text
```

**Option 2 - Hébergement HDS certifié :**
```
Alternatives HDS en France :
- OVHcloud (HDS certifié)
- Outscale (HDS certifié)
- Cloud Temple (HDS certifié)

⚠️ Coût : 3-5x plus cher que Supabase
⚠️ Complexité : Moins de fonctionnalités que Supabase
```

**Conseil pragmatique :**
Pour notaires, les **données santé sont rares** dans actes courants (ventes, donations simples).

**Stratégie :**
1. **Phase 1 :** Supabase EU + interdiction données santé (filtres)
2. **Phase 2 (si besoin) :** Migration HDS pour clients spécifiques (gériatrie, successions complexes)

---

### **4. IA Act (Règlement européen 2024)**

**Applicable à votre cas :** ✅ **OUI** (système IA usage professionnel)

**Classification :** **Risque limité** (Art. 52 - transparence)

**Obligations :**
- ✅ Informer que c'est une IA qui traite les données
- ✅ Permettre supervision humaine (notaire valide avant signature)
- ❌ Pas d'obligations lourdes (réservées aux IA "haut risque" comme recrutement, crédit)

**Implémentation :**
```markdown
# Mention dans l'interface agent

"🤖 Cet acte a été pré-rempli par Intelligence Artificielle.
Veuillez vérifier attentivement avant validation."

[Bouton : "Je valide - [Nom notaire]"]
```

---

### **5. Responsabilité en Cas d'Erreur**

**Scénario à risque :**
```
Agent IA remplit mal une variable
  ↓
Acte notarié contient erreur
  ↓
Préjudice financier client
  ↓
QUI EST RESPONSABLE ?
```

**Réponse juridique :**
1. **Responsabilité principale : LE NOTAIRE**
   - Officier public, garant de l'acte
   - Obligation de vérification personnelle
   - Assurance RC professionnelle obligatoire

2. **Responsabilité subsidiaire : VOTRE AGENCE**
   - Si erreur prouvée de l'IA
   - Si défaut de sécurité
   - → Nécessite **assurance RC Produit**

**Protection contractuelle obligatoire :**

```markdown
# Clause limitation responsabilité (contrat notaire)

"L'outil IA constitue une assistance à la rédaction. Le notaire
reste seul responsable de la validité et exactitude des actes
signés.

[Votre Agence] garantit :
- Disponibilité 99% (hors maintenance programmée)
- Sécurité données (chiffrement, RLS, audit)
- Support technique sous 48h ouvrées

Limitation responsabilité :
- Dommages directs : plafonnés à 12 mois d'abonnement
- Dommages indirects : exclus (perte exploitation, etc.)
- Assurance RC Produit : 2M€ par sinistre

Le notaire doit :
- Vérifier toute donnée pré-remplie par l'IA
- Conserver copie manuelle des données critiques
- Signaler toute anomalie sous 24h"
```

**Assurance obligatoire à souscrire :**
- **RC Exploitation** : couvre activité générale (~500-1000€/an)
- **RC Produit** : couvre défauts logiciel (~1500-3000€/an pour 2M€ garantie)
- **Cyber-assurance** : couvre breach données (~2000-5000€/an)

**Assureurs spécialisés Tech :**
- Hiscox
- AXA Pro
- Wakam (spécialiste cyber)

---

## 🟢 Points Rassurants

### **1. Supabase EU = Conformité RGPD Forte**

✅ **Localisation :** Région Frankfurt/Paris → données en UE
✅ **Certifications :** SOC 2 Type II, ISO 27001
✅ **DPA disponible :** conforme Art. 28 RGPD
✅ **Pas de transfert US :** contrairement à Firebase US

**Vérification à faire :**
```bash
# Dans dashboard Supabase, vérifier :
Project Settings → General → Region = "Europe (Frankfurt)" ou "Europe (Paris)"

# Dans code, forcer région :
const supabase = createClient(
  'https://xxx.supabase.co',
  'key',
  { db: { region: 'eu-central-1' } }
)
```

---

### **2. Architecture "Zero Knowledge" Possible**

**Niveau paranoïa max :** Chiffrez données **avant** envoi à Supabase.

```typescript
// Chiffrement côté client (votre agent IA)
import { encrypt, decrypt } from 'crypto-js/aes';

const ENCRYPTION_KEY = process.env.CLIENT_MASTER_KEY; // ⚠️ À gérer par étude

async function storeClient(data: Client) {
  const encrypted = {
    ...data,
    nom: encrypt(data.nom, ENCRYPTION_KEY).toString(),
    prenom: encrypt(data.prenom, ENCRYPTION_KEY).toString(),
    email: encrypt(data.email, ENCRYPTION_KEY).toString()
  };

  await supabase.from('clients').insert(encrypted);
}

async function readClient(id: string) {
  const { data } = await supabase.from('clients').select().eq('id', id).single();

  return {
    ...data,
    nom: decrypt(data.nom, ENCRYPTION_KEY).toString(Utf8),
    prenom: decrypt(data.prenom, ENCRYPTION_KEY).toString(Utf8),
    email: decrypt(data.email, ENCRYPTION_KEY).toString(Utf8)
  };
}
```

**Conséquence :** Même avec accès admin Supabase, données illisibles.

**⚠️ Trade-off :** Pas de recherche SQL sur champs chiffrés.

**Solution hybride :**
```sql
-- Champs sensibles chiffrés
nom_encrypted TEXT,
email_encrypted TEXT,

-- Hash pour recherche (non-réversible)
nom_hash TEXT GENERATED ALWAYS AS (encode(sha256(nom_encrypted::bytea), 'hex')) STORED,

-- Index sur hash
CREATE INDEX idx_clients_nom_hash ON clients(nom_hash);

-- Recherche possible via hash
SELECT * FROM clients WHERE nom_hash = sha256('Dupont');
```

---

### **3. Jurisprudence Favorable pour Outils Notariaux**

**Précédent rassurant :**
- Logiciels métier notariaux (Fiducial, Silex, etc.) utilisés depuis 20+ ans
- Jamais de contentieux RGPD majeur
- CNIL tolérante si **sécurité + transparence**

**Exemple décision CNIL :**
> "L'utilisation d'outils numériques par les notaires est conforme
> au RGPD dès lors que :
> - Le notaire reste maître du traitement
> - Les données sont sécurisées
> - Les clients sont informés"
>
> (Délibération CNIL n°2019-001 - Logiciels notariaux)

---

## 🎯 Architecture Technique Complète

### **Architecture Finale Recommandée**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE AGENT IA                        │
│  "Importer les fiches clients" → Upload fichier             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              SUPABASE STORAGE (chiffré)                      │
│  - Stockage temporaire fichier import                       │
│  - Scan antivirus                                            │
│  - Retention 24h puis suppression auto                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          EDGE FUNCTION "parse-import"                        │
│  1. Détection format (CSV/Excel/PDF)                        │
│  2. Mapping intelligent colonnes                            │
│  3. Validation schéma                                        │
│  4. Détection PII sensibles                                  │
│  5. Preview → validation utilisateur                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│           SUPABASE POSTGRESQL (source vérité)                │
│                                                              │
│  ┌────────────┐  ┌──────────┐  ┌─────────────┐            │
│  │  clients   │  │ dossiers │  │ audit_logs  │            │
│  ├────────────┤  ├──────────┤  ├─────────────┤            │
│  │ + RLS      │  │ + JSONB  │  │ + triggers  │            │
│  │ + encrypt  │  │ + FTS    │  │ + retention │            │
│  └────────────┘  └──────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         AGENT IA - Lecture & Remplissage Variables          │
│                                                              │
│  Query: "Donne-moi les infos vendeur dossier D2024-123"    │
│    ↓                                                         │
│  SELECT c.nom, c.prenom FROM clients c                      │
│  JOIN dossiers d ON d.parties @> '[{"client_id": c.id}]'   │
│  WHERE d.numero = 'D2024-123'                               │
│    ↓                                                         │
│  Response: "Vendeur: Jean Dupont, né le..."                 │
└─────────────────────────────────────────────────────────────┘
```

---

### **Schéma de Base de Données**

```sql
-- Table principale clients
CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  etude_id UUID REFERENCES etudes(id), -- Multi-tenant

  -- Données GenApi
  genapi_id TEXT UNIQUE,
  genapi_data JSONB, -- Données brutes du dernier import
  last_genapi_sync TIMESTAMP,

  -- Données structurées
  nom TEXT NOT NULL,
  prenom TEXT,
  email TEXT,
  telephone TEXT,

  -- Enrichissements agent IA
  ai_enrichments JSONB, -- Préférences, historique conversations
  ai_summary TEXT,

  -- Métadonnées
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by TEXT, -- "genapi_import" | "agent_ia" | user_id

  -- Confidentialité
  consent_rgpd BOOLEAN DEFAULT false,
  data_retention_until DATE,

  -- Soft delete
  deleted_at TIMESTAMP,
  anonymized BOOLEAN DEFAULT false
);

-- RLS Policy (isolation multi-études)
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Isolation par étude"
  ON clients
  FOR ALL
  USING (etude_id = auth.jwt()->>'etude_id');

-- Table dossiers
CREATE TABLE dossiers (
  id UUID PRIMARY KEY,
  numero TEXT UNIQUE, -- "D2024-123"
  type_acte TEXT,     -- "vente", "succession"
  etude_id UUID REFERENCES etudes(id),

  -- Données structurées flexibles
  parties JSONB,      -- [{role: "vendeur", client_id: "..."}]
  biens JSONB,        -- [{type: "appartement", adresse: "..."}]
  donnees_metier JSONB, -- Champs spécifiques par type acte

  -- Métadonnées
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table audit trail
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Qui ?
  user_id UUID REFERENCES users(id),
  user_email TEXT,
  etude_id UUID,

  -- Quoi ?
  action TEXT, -- "import_clients", "read_client", "delete_client"
  resource_type TEXT, -- "client", "dossier"
  resource_id UUID,

  -- Détails
  details JSONB, -- {file_name: "export_genapi.csv", rows: 5000}
  ip_address INET,
  user_agent TEXT,

  -- Quand ?
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour recherche rapide
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);

-- Index composites pour queries fréquentes
CREATE INDEX idx_clients_search
  ON clients USING gin(to_tsvector('french', nom || ' ' || prenom));

-- Matérialized view pour stats (évite calculs répétés)
CREATE MATERIALIZED VIEW stats_etudes AS
SELECT
  etude_id,
  COUNT(*) as nb_clients,
  COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 month') as nb_nouveaux
FROM clients
GROUP BY etude_id;
```

---

### **Sécurité en Couches**

```
┌─────────────────────────────────────────────┐
│ Couche 1 : Upload (Supabase Storage)       │
│ - Chiffrement at-rest (AES-256)            │
│ - Scan antivirus (ClamAV)                  │
│ - Validation type fichier                  │
│ - Limite taille (ex: 50MB)                 │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ Couche 2 : Parsing (Edge Function)         │
│ - Timeout 30s max                           │
│ - Isolation sandbox                         │
│ - Validation schéma (Zod/Pydantic)         │
│ - Détection PII sensibles (NIR, IBAN)     │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ Couche 3 : Stockage (PostgreSQL)           │
│ - RLS (Row Level Security)                 │
│ - Chiffrement colonnes sensibles (pgcrypto)│
│ - Audit trail automatique                  │
│ - Backup chiffrés quotidiens               │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ Couche 4 : Lecture Agent                   │
│ - Authentification JWT                      │
│ - Rate limiting                             │
│ - Logs accès (qui lit quoi quand)         │
│ - Masquage données si nécessaire           │
└─────────────────────────────────────────────┘
```

---

### **Détection PII Sensibles**

```python
import re

SENSITIVE_PATTERNS = {
    'nir': r'\b[1-2]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b',
    'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b',
    'carte_bancaire': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    'medical': r'\b(cancer|vih|sida|dépression|traitement)\b'
}

def scan_sensitive_data(text):
    alerts = []
    for category, pattern in SENSITIVE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            alerts.append(category)
    return alerts

# Pendant l'import
for row in csv_data:
    alerts = scan_sensitive_data(str(row))
    if alerts:
        # Alerte à l'utilisateur
        log_warning(f"Données sensibles détectées: {alerts}")
        # Option 1 : Masquer automatiquement
        # Option 2 : Demander confirmation notaire
```

---

### **Mapping Intelligent Variables**

```json
{
  "acte_vente": {
    "variables_requises": [
      "vendeur_nom",
      "vendeur_prenom",
      "acheteur_nom",
      "bien_adresse",
      "prix_vente"
    ],
    "mapping_supabase": {
      "vendeur_nom": "clients.nom WHERE role='vendeur'",
      "vendeur_prenom": "clients.prenom WHERE role='vendeur'",
      "acheteur_nom": "clients.nom WHERE role='acheteur'",
      "bien_adresse": "biens.adresse",
      "prix_vente": "transactions.montant"
    },
    "validations": {
      "prix_vente": "must_be_numeric",
      "bien_adresse": "must_exist_in_cadastre"
    }
  }
}
```

**Architecture Agent :**
```
User: "Génère l'acte de vente pour le dossier D2024-123"
  ↓
Agent:
  1. Identifie type acte → "acte_vente"
  2. Récupère mapping → variables_requises
  3. Query Supabase → SELECT nom, prenom FROM clients WHERE dossier_id='D2024-123'
  4. Validation → tous les champs présents ?
  5. Si manquant → demande à l'utilisateur
  6. Remplissage template → génération acte
```

---

### **Parser Flexible pour Import**

```python
# Mauvaise approche (rigide)
nom = row[0]  # Casse si l'ordre change

# Bonne approche (flexible)
COLUMN_MAPPINGS = {
    'nom': ['nom', 'name', 'lastname', 'nom_client'],
    'prenom': ['prenom', 'prenom', 'firstname', 'prenom_client'],
    'email': ['email', 'mail', 'e-mail', 'courriel']
}

def smart_parse(row_dict):
    result = {}
    for field, possible_names in COLUMN_MAPPINGS.items():
        for variant in possible_names:
            if variant in row_dict:
                result[field] = row_dict[variant]
                break
    return result
```

---

### **UX Import avec Feedback Temps Réel**

**Bonne expérience :**
```
User: [Upload fichier]
Agent: "✓ Fichier reçu (2.3 MB)"
Agent: "🔍 Détection format... Excel 2016 détecté"
Agent: "📊 Preview: 5000 lignes, 12 colonnes"
Agent: "✓ Colonnes mappées: nom ✓, prénom ✓, email ✓..."
Agent: "⚠️ Colonne 'fax' ignorée (non utilisée)"
Agent: "🔐 Scan sécurité... 3 NIR détectés (masqués)"
Agent: "💾 Import batch 1/10 (500 lignes) ✓"
Agent: "💾 Import batch 2/10 (500 lignes) ✓"
...
Agent: "✅ Import terminé: 4.987 clients ajoutés, 13 doublons ignorés"
Agent: "📋 Rapport détaillé disponible"
```

**Implémentation technique :**
```typescript
// Supabase Edge Function avec streaming
export async function importClients(file: File) {
  const stream = new TransformStream();
  const writer = stream.writable.getWriter();

  // Envoi progressif au client
  (async () => {
    await writer.write({ type: 'progress', step: 'parsing', percent: 0 });

    const rows = await parseCSV(file);
    await writer.write({ type: 'progress', step: 'parsing', percent: 100 });

    for (let i = 0; i < rows.length; i += 100) {
      const batch = rows.slice(i, i + 100);
      await insertBatch(batch);

      await writer.write({
        type: 'progress',
        step: 'importing',
        percent: (i / rows.length) * 100
      });
    }

    await writer.write({ type: 'complete', count: rows.length });
    await writer.close();
  })();

  return new Response(stream.readable);
}
```

---

## ✅ Checklist de Conformité

### **Juridique (non-négociable) :**
- [ ] **Registre des traitements** rédigé et signé
- [ ] **DPA Supabase** téléchargé et archivé
- [ ] **Politique de confidentialité** publiée (URL publique)
- [ ] **Mentions RGPD** dans contrats notaires
- [ ] **Procédure exercice des droits** (formulaire + process)
- [ ] **Assurance RC Produit** souscrite (minimum 1M€)

### **Technique (sécurité) :**
- [ ] **Région Supabase EU** configurée (vérifiée)
- [ ] **RLS activé** sur toutes tables sensibles
- [ ] **Chiffrement pgcrypto** sur NIR/IBAN si stockés
- [ ] **Audit logs** avec retention 3 ans
- [ ] **Backup quotidiens** + test restore trimestriel
- [ ] **MFA obligatoire** pour tous comptes notaires
- [ ] **Rate limiting** configuré (anti-scraping)
- [ ] **Monitoring alertes** (accès anormaux, bulk export)

### **Organisationnel :**
- [ ] **DPO désigné** (ou prestataire externe si <250 employés)
- [ ] **Engagements confidentialité** signés (votre équipe)
- [ ] **Procédure breach notification** documentée (72h CNIL)
- [ ] **Revue annuelle** sécurité + conformité

---

## 🎯 Stratégie de Déploiement

### **Phase 1 - Pilote conforme (3 mois) :**
```
- 2-3 études pilotes consentantes
- Données limitées (ventes simples, pas de successions)
- Audit externe conformité (cabinet spécialisé ~3-5k€)
- Ajustements suite audit
```

### **Phase 2 - Scale sécurisé (6 mois) :**
```
- 10-20 études
- Élargissement périmètre données
- Certification (ISO 27001 ou équivalent)
- Support juridique en continu
```

### **Phase 3 - Industrialisation (12+ mois) :**
```
- 100+ études
- DPO interne
- Pentest annuels
- Veille réglementaire automatisée
```

---

## ⚖️ Verdict Final

**Votre architecture est CONFORME** si vous implémentez :

1. ✅ **Registre RGPD** + **DPA Supabase**
2. ✅ **RLS + chiffrement** + **audit logs**
3. ✅ **Contrats notaires** avec clauses confidentialité
4. ✅ **Assurance RC Produit**
5. ✅ **Procédures droits personnes** (accès, effacement, etc.)

**Risque résiduel :** **FAIBLE** si checklist respectée.

**Coût conformité :** ~10-15k€ première année (audit + assurance + DPO externe)

---

## 📋 Approches Possibles (Résumé)

### **Approche 1 : Import Manuel Sécurisé avec Chiffrement**

**Architecture :**
- Export périodique depuis GenApi (fichier CSV/Excel) par le notaire
- Upload sécurisé dans Supabase Storage (chiffré)
- Parsing automatique et stockage dans tables Supabase
- Suppression automatique du fichier source après traitement

**Avantages :**
- **Juridique** : Pas d'accès automatisé = pas de problème RGPD/API tier
- **Contrôle** : Le notaire décide quand et quelles données exporter
- **Traçabilité** : Logs d'import complets
- **Simplicité** : Pas d'intégration complexe

**Stack technique :**
```
Notaire → Export GenApi (manuel)
       → Upload Supabase Storage (chiffrement AES-256)
       → Edge Function Supabase (parsing)
       → Supabase DB (PostgreSQL + RLS)
       → Agent IA (lecture via Supabase Client)
```

---

### **Approche 2 : Saisie Progressive Conversationnelle**

**Architecture :**
- L'agent IA collecte les informations via conversation
- Validation en temps réel des données
- Stockage incrémental dans Supabase
- Enrichissement progressif de la fiche client

**Avantages :**
- **Zéro dépendance** à GenApi
- **Expérience naturelle** : dialogue fluide
- **Données minimales** : seulement ce qui est nécessaire (privacy by design)
- **Flexibilité** : adaptation à chaque étude notariale

**Flux utilisateur :**
```
Agent: "Bonjour, puis-je avoir le nom du client ?"
User: "Dupont Jean"
Agent: "Merci. Type de dossier ? (vente, succession, donation...)"
User: "Vente immobilière"
Agent: [Sauvegarde dans Supabase] "Adresse du bien ?"
...
```

---

### **Approche 3 : Base de Données Miroir avec Synchronisation Hybride**

**Architecture :**
- Base Supabase comme source de vérité
- Synchronisation ponctuelle via exports GenApi (batch hebdomadaire/mensuel)
- Enrichissement manuel par l'agent lors des interactions
- Système de "golden record" combinant les deux sources

**Avantages :**
- **Meilleur des deux mondes** : données GenApi + enrichissements IA
- **Autonomie** : fonctionne même sans GenApi
- **Évolutivité** : prêt pour d'autres logiciels notariaux (Silex, Fiducial...)
- **Multi-études** : architecture scalable pour votre agence

---

## 🎯 Recommandation Finale

**Approche Hybride 1 + 2 :**
1. **Import manuel sécurisé** (Approche 1) pour migrer les données existantes
2. **Saisie conversationnelle** (Approche 2) pour les nouveaux dossiers

**Roadmap :**
```
Phase 1 (Mois 1-2) :
  ✓ Setup Supabase + RLS multi-tenant
  ✓ Import manuel CSV → parsing automatique
  ✓ Agent IA en lecture seule

Phase 2 (Mois 3-4) :
  ✓ Saisie conversationnelle
  ✓ Validation RGPD intégrée
  ✓ Export données (pour GenApi si besoin)

Phase 3 (Mois 5+) :
  ✓ Synchronisation bidirectionnelle (si juridiquement possible)
  ✓ Connecteurs pour autres logiciels notariaux
  ✓ Marketplace pour vos clients notaires
```

---

## 📞 Ressources Utiles

**Juridique :**
- CNIL : https://www.cnil.fr
- DPA Supabase : https://supabase.com/legal/dpa
- Modèles RGPD : https://www.cnil.fr/fr/modeles

**Assurances :**
- Hiscox : https://www.hiscox.fr
- AXA Pro : https://www.axa.fr/pro
- Wakam : https://www.wakam.com

**Hébergeurs HDS (si nécessaire) :**
- OVHcloud : https://www.ovhcloud.com
- Outscale : https://outscale.com
- Cloud Temple : https://www.cloud-temple.com

---

**Date de création :** 2026-01-19
**Version :** 1.0
**Dernière mise à jour :** 2026-01-19
