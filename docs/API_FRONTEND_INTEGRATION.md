# Guide d'Intégration Frontend - NotaireAI API

**Version**: 1.5.0
**Date**: 28 janvier 2026
**Auteur**: Équipe NotaireAI
**Destinataire**: Paul (Développeur Frontend)

---

## Table des Matières

1. [Introduction](#introduction)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Authentification](#authentification)
4. [Workflow Upload Titre](#workflow-upload-titre)
5. [Workflow Génération Promesse](#workflow-génération-promesse)
6. [Workflow Génération Vente](#workflow-génération-vente)
7. [Modèles de Données](#modèles-de-données)
8. [Exemples cURL et JavaScript](#exemples-curl-et-javascript)
9. [Gestion des Erreurs](#gestion-des-erreurs)
10. [Webhooks (Futur)](#webhooks-futur)

---

## Introduction

L'API NotaireAI permet de générer des actes notariaux (promesse de vente, acte de vente) à partir de données structurées ou de titres de propriété uploadés.

### Base URL

```
Production: https://api.notaireai.fr/v1
Développement: http://localhost:8000/v1
```

### Formats

- **Requêtes**: JSON (`Content-Type: application/json`)
- **Réponses**: JSON
- **Fichiers générés**: DOCX, PDF

---

## Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/titres/upload` | Upload d'un titre de propriété |
| `GET` | `/titres/{id}` | Récupérer un titre extrait |
| `GET` | `/titres/search` | Rechercher des titres |
| `POST` | `/promesses/generer` | Générer une promesse de vente |
| `POST` | `/promesses/depuis-titre` | Générer depuis un titre |
| `GET` | `/promesses/{id}` | Récupérer une promesse |
| `POST` | `/ventes/generer` | Générer un acte de vente |
| `POST` | `/ventes/depuis-promesse` | Convertir promesse → vente |
| `POST` | `/validation/donnees` | Valider des données |
| `GET` | `/schemas/{type}` | Récupérer un schéma JSON |
| `GET` | `/health` | Statut de l'API |

---

## Authentification

### JWT Bearer Token

```http
Authorization: Bearer <votre_token>
```

### Obtenir un token

```bash
curl -X POST https://api.notaireai.fr/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "***"}'
```

**Réponse:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "refresh_token": "rt_..."
}
```

---

## Workflow Upload Titre

### Étape 1: Upload du fichier

```http
POST /v1/titres/upload
Content-Type: multipart/form-data
```

**Paramètres:**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `file` | File | Oui | PDF ou DOCX du titre |
| `reference` | String | Non | Référence interne |
| `ocr` | Boolean | Non | Forcer OCR (défaut: auto) |

**Exemple cURL:**
```bash
curl -X POST https://api.notaireai.fr/v1/titres/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@titre_propriete.pdf" \
  -F "reference=DOSSIER-2026-001"
```

**Réponse (200 OK):**
```json
{
  "id": "titre_abc123",
  "status": "processing",
  "reference": "DOSSIER-2026-001",
  "created_at": "2026-01-28T10:30:00Z"
}
```

### Étape 2: Vérifier le statut

```http
GET /v1/titres/{id}
```

**Réponse (200 OK):**
```json
{
  "id": "titre_abc123",
  "status": "completed",
  "reference": "DOSSIER-2026-001",
  "confiance_extraction": 0.92,
  "donnees": {
    "proprietaires": [
      {
        "nom": "DUPONT",
        "prenoms": "Jean Pierre",
        "date_naissance": "15/03/1975",
        "lieu_naissance": "Lyon (Rhône)"
      }
    ],
    "bien": {
      "adresse": {
        "numero": "15",
        "rue": "Rue de la République",
        "code_postal": "69001",
        "commune": "LYON"
      },
      "lots": [
        {
          "numero": 25,
          "description": "Appartement au 3ème étage",
          "tantiemes": {"valeur": 125, "base": 10000}
        }
      ]
    },
    "origine_propriete": {
      "type": "Vente",
      "date": "12/05/2010",
      "notaire": "Me MARTIN à Lyon",
      "reference": "2010V1234"
    }
  },
  "fichier_original": "https://storage.notaireai.fr/titres/abc123/original.pdf"
}
```

### Statuts possibles

| Statut | Description |
|--------|-------------|
| `pending` | En attente de traitement |
| `processing` | Extraction en cours |
| `completed` | Extraction terminée |
| `error` | Erreur d'extraction |

---

## Workflow Génération Promesse

### Option A: Génération directe

```http
POST /v1/promesses/generer
Content-Type: application/json
```

**Body:**
```json
{
  "type_promesse": "standard",
  "promettants": [
    {
      "nom": "DUPONT",
      "prenoms": "Jean Pierre",
      "date_naissance": "15/03/1975",
      "lieu_naissance": "Lyon (Rhône)",
      "adresse": "15 rue de la République, 69001 LYON",
      "situation_matrimoniale": {
        "statut": "marie",
        "regime_matrimonial": "communaute_legale",
        "conjoint": {
          "nom": "DUPONT",
          "prenoms": "Marie",
          "intervient": true
        }
      }
    }
  ],
  "beneficiaires": [
    {
      "nom": "MARTIN",
      "prenoms": "Paul",
      "date_naissance": "20/08/1985",
      "lieu_naissance": "Paris (75)",
      "adresse": "10 avenue des Champs, 75008 PARIS"
    }
  ],
  "bien": {
    "adresse": {
      "numero": "15",
      "rue": "Rue de la République",
      "code_postal": "69001",
      "commune": "LYON"
    },
    "lots": [
      {
        "numero": 25,
        "description": "Appartement de type T3",
        "superficie_carrez": 65.5,
        "tantiemes": {"valeur": 125, "base": 10000}
      }
    ]
  },
  "prix": {
    "montant": 250000,
    "en_lettres": "deux cent cinquante mille euros"
  },
  "conditions_suspensives": {
    "pret": {
      "actif": true,
      "montant": 200000,
      "taux_max": 4.5,
      "duree_mois": 240,
      "date_limite_obtention": "2026-04-15"
    }
  },
  "delai_realisation": "2026-06-30",
  "indemnite_immobilisation": {
    "montant": 25000,
    "pourcentage": 10
  }
}
```

**Réponse (200 OK):**
```json
{
  "id": "promesse_xyz789",
  "status": "generated",
  "type_promesse": "standard",
  "fichiers": {
    "docx": "https://storage.notaireai.fr/promesses/xyz789/promesse.docx",
    "pdf": "https://storage.notaireai.fr/promesses/xyz789/promesse.pdf",
    "md": "https://storage.notaireai.fr/promesses/xyz789/promesse.md"
  },
  "sections_incluses": [
    "identification_parties",
    "designation_bien",
    "prix_paiement",
    "conditions_suspensives",
    "indemnite_immobilisation"
  ],
  "validation": {
    "valide": true,
    "warnings": [
      "Conjoint du vendeur intervient - vérifier signature requise"
    ]
  },
  "duree_generation": 3.2,
  "created_at": "2026-01-28T10:35:00Z"
}
```

### Option B: Depuis un titre extrait

```http
POST /v1/promesses/depuis-titre
Content-Type: application/json
```

**Body:**
```json
{
  "titre_id": "titre_abc123",
  "beneficiaires": [
    {
      "nom": "MARTIN",
      "prenoms": "Paul",
      "date_naissance": "20/08/1985",
      "lieu_naissance": "Paris (75)",
      "adresse": "10 avenue des Champs, 75008 PARIS"
    }
  ],
  "prix": {
    "montant": 250000
  },
  "options": {
    "type_promesse": "auto",
    "conditions_suspensives": {
      "pret": {
        "actif": true,
        "montant": 200000
      }
    }
  }
}
```

---

## Workflow Génération Vente

### Option A: Génération directe

```http
POST /v1/ventes/generer
Content-Type: application/json
```

**Body:** Similaire à promesse, avec `vendeurs` et `acquereurs` au lieu de `promettants`/`beneficiaires`.

### Option B: Depuis une promesse signée

```http
POST /v1/ventes/depuis-promesse
Content-Type: application/json
```

**Body:**
```json
{
  "promesse_id": "promesse_xyz789",
  "date_vente": "2026-06-15",
  "modifications": {
    "prix.montant": 248000
  }
}
```

**Réponse (200 OK):**
```json
{
  "id": "vente_def456",
  "status": "generated",
  "source_promesse": "promesse_xyz789",
  "fichiers": {
    "docx": "https://storage.notaireai.fr/ventes/def456/vente.docx",
    "pdf": "https://storage.notaireai.fr/ventes/def456/vente.pdf"
  },
  "modifications_detectees": [
    {
      "type": "prix",
      "original": 250000,
      "nouveau": 248000,
      "gravite": "mineure"
    }
  ],
  "avenant_necessaire": false,
  "validation": {
    "valide": true,
    "errors": [],
    "warnings": []
  }
}
```

---

## Modèles de Données

### Personne Physique

```typescript
interface PersonnePhysique {
  nom: string;              // En majuscules
  prenoms: string;          // Tous les prénoms
  date_naissance: string;   // Format "DD/MM/YYYY"
  lieu_naissance: string;   // "Ville (Département)"
  nationalite?: string;     // Défaut: "Française"
  profession?: string;
  adresse: string | Adresse;
  situation_matrimoniale?: SituationMatrimoniale;
}
```

### Situation Matrimoniale

```typescript
interface SituationMatrimoniale {
  statut: "celibataire" | "marie" | "pacse" | "divorce" | "veuf";
  regime_matrimonial?: "communaute_legale" | "separation_biens" |
                       "communaute_universelle" | "participation_acquets";
  conjoint?: {
    nom: string;
    prenoms: string;
    intervient: boolean;  // Doit signer l'acte?
  };
  date_mariage?: string;
  lieu_mariage?: string;
  contrat_mariage?: {
    notaire: string;
    date: string;
  };
}
```

### Bien Immobilier

```typescript
interface Bien {
  adresse: Adresse;
  designation?: string;     // Description libre
  lots: Lot[];             // Copropriété
  cadastre?: Cadastre[];
  superficie_carrez?: {
    superficie_m2: number;
    date_mesurage: string;
  };
}
```

### Lot de Copropriété

```typescript
interface Lot {
  numero: number;
  description: string;
  etage?: string;
  superficie_carrez?: number;
  tantiemes: {
    valeur: number;        // Ex: 125
    base: number;          // Ex: 10000
    type?: string;         // "charges générales"
  };
}
```

### Prix

```typescript
interface Prix {
  montant: number;
  en_lettres?: string;     // Auto-généré si absent
  devise?: string;         // Défaut: "EUR"
  ventilation?: {
    terrain?: number;
    construction?: number;
    mobilier?: number;
  };
}
```

### Conditions Suspensives

```typescript
interface ConditionsSuspensives {
  pret?: {
    actif: boolean;
    montant: number;
    taux_max?: number;
    duree_mois?: number;
    date_limite_obtention: string;
    organisme?: string;
  };
  vente_prealable?: {
    actif: boolean;
    bien_a_vendre: string;
    date_limite: string;
  };
  urbanisme?: {
    actif: boolean;
    type: "permis_construire" | "declaration_prealable" | "autre";
    description?: string;
  };
}
```

---

## Exemples cURL et JavaScript

### JavaScript (Fetch)

```javascript
// Configuration
const API_BASE = 'https://api.notaireai.fr/v1';
const TOKEN = 'votre_token_jwt';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// 1. Upload d'un titre
async function uploadTitre(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/titres/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${TOKEN}` },
    body: formData
  });

  return response.json();
}

// 2. Générer une promesse
async function genererPromesse(donnees) {
  const response = await fetch(`${API_BASE}/promesses/generer`, {
    method: 'POST',
    headers,
    body: JSON.stringify(donnees)
  });

  return response.json();
}

// 3. Générer depuis titre
async function genererDepuisTitre(titreId, beneficiaires, prix) {
  const response = await fetch(`${API_BASE}/promesses/depuis-titre`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      titre_id: titreId,
      beneficiaires,
      prix
    })
  });

  return response.json();
}

// 4. Convertir promesse en vente
async function promesseVersVente(promesseId, dateVente, modifications = {}) {
  const response = await fetch(`${API_BASE}/ventes/depuis-promesse`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      promesse_id: promesseId,
      date_vente: dateVente,
      modifications
    })
  });

  return response.json();
}

// 5. Télécharger le fichier généré
async function telechargerDocx(url) {
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${TOKEN}` }
  });

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = 'document.docx';
  a.click();
}
```

### React Hook (Exemple)

```jsx
import { useState, useCallback } from 'react';

function useNotaireAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const genererPromesse = useCallback(async (donnees) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/promesses/generer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(donnees)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Erreur de génération');
      }

      return await response.json();

    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { genererPromesse, loading, error };
}
```

---

## Gestion des Erreurs

### Codes d'erreur HTTP

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé (upload réussi) |
| 400 | Données invalides |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Ressource non trouvée |
| 422 | Validation échouée |
| 500 | Erreur serveur |

### Format des erreurs

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Données invalides",
    "details": [
      {
        "field": "promettants[0].date_naissance",
        "code": "REQUIRED",
        "message": "Date de naissance requise"
      },
      {
        "field": "prix.montant",
        "code": "INVALID_TYPE",
        "message": "Le montant doit être un nombre"
      }
    ]
  }
}
```

### Codes d'erreur métier

| Code | Description | Action |
|------|-------------|--------|
| `REQUIRED` | Champ obligatoire manquant | Ajouter le champ |
| `INVALID_TYPE` | Type de données incorrect | Corriger le format |
| `INVALID_FORMAT` | Format incorrect (date, etc.) | Utiliser le bon format |
| `CONJOINT_REQUIS` | Conjoint doit intervenir | Ajouter `conjoint.intervient: true` |
| `QUOTITES_INVALIDES` | Total ≠ 100% | Corriger les quotités |
| `DIAGNOSTIC_EXPIRE` | Diagnostic expiré | Avertir l'utilisateur |
| `EXTRACTION_FAILED` | Échec OCR | Réessayer ou saisie manuelle |

---

## Webhooks (Futur)

### Configuration

```http
POST /v1/webhooks
Content-Type: application/json
```

```json
{
  "url": "https://votre-app.com/webhooks/notaireai",
  "events": [
    "titre.extraction_completed",
    "promesse.generated",
    "vente.generated"
  ],
  "secret": "votre_secret_hmac"
}
```

### Événements disponibles

| Événement | Description |
|-----------|-------------|
| `titre.extraction_completed` | Extraction d'un titre terminée |
| `titre.extraction_failed` | Échec d'extraction |
| `promesse.generated` | Promesse générée |
| `vente.generated` | Acte de vente généré |
| `validation.warning` | Avertissement de validation |

### Format du payload

```json
{
  "event": "promesse.generated",
  "timestamp": "2026-01-28T10:35:00Z",
  "data": {
    "id": "promesse_xyz789",
    "type_promesse": "standard",
    "fichiers": {
      "docx": "https://..."
    }
  }
}
```

### Vérification HMAC

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${expected}`)
  );
}
```

---

## Support

**Contact technique**: dev@notaireai.fr
**Documentation complète**: https://docs.notaireai.fr
**Postman Collection**: https://api.notaireai.fr/postman

---

*Document généré automatiquement - NotaireAI v1.5.0*
