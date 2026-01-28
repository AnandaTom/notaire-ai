# Directive : Intégration du Titre de Propriété dans les Promesses de Vente

## Objectif

Intégrer l'analyse des titres de propriété (actes authentiques de vente) dans le workflow de création des promesses unilatérales de vente, afin d'extraire automatiquement ou manuellement la chaîne d'origine de propriété.

---

## Contexte

Les notaires doivent fournir le titre de propriété du vendeur (promettant) pour générer une promesse unilatérale de vente. Ce document contient la section **"ORIGINE DE PROPRIETE"** qui doit être reproduite dans la promesse de vente.

### Document de référence analysé

**Fichier**: `docs_original/ACTE_AUTHENTIQUE_PAGES_1-39.pdf`
- **Type**: Acte authentique de vente du 27 juin 2017
- **Notaire**: Maître Lionel MONJEAUD, Villeurbanne
- **Vendeurs**: Thibault TARBOURIECH (54.30%) et Sabah KSOURI (45.70%)
- **Acquéreurs**: Jean-Marie DIAZ, Patricia ROBLOT, Charlotte DIAZ
- **Bien**: Lots 25 (appartement) et 7 (cave) à Tassin-la-Demi-Lune
- **Prix**: 193 000 EUR
- **Section origine**: Pages 34-35 du PDF

---

## Structure de l'origine de propriété dans le PDF

### Chaîne complète à 3 niveaux

Le PDF montre une chaîne d'origine sur 3 niveaux, remontant jusqu'à l'acquisition originale:

#### Niveau 1 : Acquisition actuelle (2014)
**"Acquisition par M. Thibault TARBOURIECH et Melle Sabah KSOURI, en indivision"**

Suivant acte reçu par Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche, le 30 juin 2014, publié au service de la publicité foncière de LYON 5ème, le 24 juillet 2014, volume 2014P n° 4164.

**Vendeur**: Christian GROS

#### Niveau 2 : Successions (1974 & 2013)
Lui-même venant aux droits de :

**a) Jean GROS** - décédé le 4 juillet 1974 à Lyon 5ème
- Régime matrimonial: Marié sous le régime de la communauté légale
- Conjoint: Suzanne DUMOLLARD
- Héritier: Christian GROS (fils unique)

**b) Suzanne DUMOLLARD** - décédée le 21 octobre 2013 à Lyon 5ème
- Héritiers: Christian GROS et Pascal GROS (fils)

#### Niveau 3 : Acquisition originale VEFA (1972)
**"Acquisition par les époux Jean GROS et Suzanne DUMOLLARD"**

Suivant acte de vente en l'état futur d'achèvement (VEFA) reçu par Maître RESILLOT, notaire à Lyon, le 24 janvier 1972, publié au service de la publicité foncière de LYON 5ème, le 11 février 1972, volume 211, n° 2.

**Vendeur**: SCI "LES FEUILLANTINES"

### Lots concernés

Dans cet exemple, **tous les lots** (lot 25 et lot 7) ont la même origine de propriété. La chaîne est identique pour les deux lots.

---

## Mapping vers le schéma JSON existant

### Structure actuelle dans `variables_promesse_vente.json`

```json
{
  "origine_propriete": {
    "type": "array",
    "description": "Chaîne d'origine de propriété",
    "items": {
      "type": "object",
      "properties": {
        "lots_concernes": {
          "type": "array",
          "items": { "type": "integer" },
          "description": "Numéros des lots concernés par cette origine"
        },
        "origine_immediate": {
          "type": "object",
          "properties": {
            "type": { "enum": ["acquisition", "succession", "donation", "licitation", "partage", "adjudication"] },
            "vendeur_precedent": { "type": "string" },
            "notaire": { "type": "string" },
            "date": { "type": "string" },
            "publication": {
              "type": "object",
              "properties": {
                "service": { "type": "string" },
                "date": { "type": "string" },
                "volume": { "type": "string" },
                "numero": { "type": "string" }
              }
            }
          }
        }
      }
    }
  }
}
```

### Limitation actuelle

Le schéma actuel ne supporte que **l'origine immédiate** (1 niveau). Il ne permet pas de capturer la **chaîne complète** à plusieurs niveaux comme dans le PDF.

---

## Proposition d'amélioration du schéma

### Option 1 : Structure chaînée simple (RECOMMANDÉE)

Cette option conserve la simplicité du schéma actuel mais documente que seule l'origine immédiate est capturée dans le template.

**Avantages**:
- Compatible avec le template existant (ligne 320-326 de `promesse_vente_lots_copropriete.md`)
- Simple à collecter via les questions
- Suffit pour la plupart des cas (la chaîne complète figure dans le titre de propriété annexé)

**Inconvénients**:
- Ne capture pas la chaîne complète
- Perte d'information si le titre de propriété n'est pas annexé

### Option 2 : Structure chaînée complète

Modifier le schéma pour supporter plusieurs niveaux:

```json
{
  "origine_propriete": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "lots_concernes": { "type": "array", "items": { "type": "integer" } },
        "chaine": {
          "type": "array",
          "description": "Chaîne d'origine du plus récent au plus ancien",
          "items": {
            "type": "object",
            "properties": {
              "type": { "enum": ["acquisition", "succession", "donation", "licitation", "partage", "adjudication", "vefa"] },
              "niveau": { "type": "integer", "description": "1 = origine immédiate, 2+ = origines antérieures" },
              "vendeur_ou_auteur": { "type": "string" },
              "notaire": { "type": "string" },
              "date": { "type": "string" },
              "publication": {
                "type": "object",
                "properties": {
                  "service": { "type": "string" },
                  "date": { "type": "string" },
                  "volume": { "type": "string" },
                  "numero": { "type": "string" }
                }
              },
              "details_succession": {
                "type": "object",
                "description": "Détails si type = succession",
                "properties": {
                  "defunt_nom": { "type": "string" },
                  "date_deces": { "type": "string" },
                  "lieu_deces": { "type": "string" },
                  "regime_matrimonial": { "type": "string" },
                  "conjoint_survivant": { "type": "string" },
                  "heritiers": {
                    "type": "array",
                    "items": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Avantages**:
- Capture la chaîne complète
- Permet de générer une section "ORIGINE DE PROPRIETE" détaillée
- Traçabilité totale

**Inconvénients**:
- Plus complexe à collecter
- Nécessite de modifier le template
- Peut être fastidieux pour des chaînes longues

---

## Recommandation : Option 1 (Simple)

Pour l'instant, **conserver la structure actuelle** (Option 1) et documenter que:

1. Seule **l'origine immédiate** est capturée dans le template
2. Le **titre de propriété complet** doit être **annexé** à la promesse de vente
3. La chaîne complète figure donc dans les annexes

### Justification

- Le template actuel (lignes 320-326) ne génère qu'une phrase simple pour l'origine immédiate
- La chaîne complète est toujours disponible dans le titre de propriété annexé
- Simplification du workflow de collecte
- Compatible avec 95% des cas d'usage

---

## Exemple JSON pour le cas analysé

### Données à extraire du PDF

```json
{
  "origine_propriete": [
    {
      "lots_concernes": [25, 7],
      "origine_immediate": {
        "type": "acquisition",
        "vendeur_precedent": "Christian GROS",
        "notaire": "Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche",
        "date": "30 juin 2014",
        "publication": {
          "service": "LYON 5ème",
          "date": "24 juillet 2014",
          "volume": "2014P",
          "numero": "4164"
        }
      }
    }
  ]
}
```

### Rendu dans le template (lignes 320-326)

```
# Effet relatif

**Concernant les lots numéros 25, 7**
Acquisition suivant acte reçu par Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche le 30 juin 2014, publié au service de la publicité foncière de LYON 5ème le 24 juillet 2014, volume 2014P, numéro 4164.
```

---

## Workflow d'intégration

### Étape 1 : Réception du titre de propriété

Le notaire fournit le titre de propriété du vendeur (PDF, DOCX, ou papier).

### Étape 2 : Extraction de l'origine immédiate

**Méthode A : Extraction manuelle via questions**

Utiliser les questions existantes dans `schemas/questions_promesse_vente.json` (Section 16):

```json
{
  "16_origine_propriete": {
    "titre": "Origine de propriété",
    "questions": [
      {
        "id": "origine_type",
        "question": "Type d'acquisition par le promettant ?",
        "type": "choix",
        "options": ["Acquisition", "Succession", "Donation", "Licitation", "Partage", "Adjudication"],
        "obligatoire": true,
        "variable": "origine_propriete[].type"
      },
      {
        "id": "origine_vendeur",
        "question": "Nom du vendeur ou auteur précédent ?",
        "variable": "origine_propriete[].vendeur_precedent"
      },
      {
        "id": "origine_notaire",
        "question": "Notaire de l'acte d'origine ?",
        "exemple": "Maître NOM, notaire à VILLE",
        "variable": "origine_propriete[].notaire"
      },
      {
        "id": "origine_date",
        "question": "Date de l'acte d'origine ?",
        "variable": "origine_propriete[].date"
      },
      {
        "id": "origine_publication_service",
        "question": "Service de publicité foncière ?",
        "exemple": "LYON 5ème",
        "variable": "origine_propriete[].publication.service"
      },
      {
        "id": "origine_publication_date",
        "question": "Date de publication ?",
        "variable": "origine_propriete[].publication.date"
      },
      {
        "id": "origine_publication_volume",
        "question": "Volume de publication ?",
        "exemple": "2014P",
        "variable": "origine_propriete[].publication.volume"
      },
      {
        "id": "origine_publication_numero",
        "question": "Numéro de publication ?",
        "exemple": "4164",
        "variable": "origine_propriete[].publication.numero"
      }
    ]
  }
}
```

**Méthode B : Extraction automatique (Future amélioration)**

Créer un script `execution/extraire_origine_titre.py` qui:
1. Parse le PDF du titre de propriété
2. Détecte la section "ORIGINE DE PROPRIETE"
3. Extrait les données structurées
4. Génère le JSON pour `origine_propriete`

**Note**: Cette méthode nécessite un investissement en OCR/NLP et n'est pas prioritaire.

### Étape 3 : Validation

Ajouter des validations dans `execution/valider_acte.py`:

```python
def valider_origine_propriete(data):
    """Valide la section origine de propriété"""
    errors = []

    if "origine_propriete" not in data or not data["origine_propriete"]:
        errors.append("Origine de propriété manquante")
        return errors

    for i, origine in enumerate(data["origine_propriete"]):
        # Vérifier lots concernés
        if "lots_concernes" not in origine or not origine["lots_concernes"]:
            errors.append(f"Origine {i+1}: Lots concernés manquants")

        # Vérifier origine immédiate
        if "origine_immediate" not in origine:
            errors.append(f"Origine {i+1}: Origine immédiate manquante")
            continue

        imm = origine["origine_immediate"]

        # Champs obligatoires
        if "type" not in imm:
            errors.append(f"Origine {i+1}: Type d'acquisition manquant")
        if "notaire" not in imm:
            errors.append(f"Origine {i+1}: Notaire manquant")
        if "date" not in imm:
            errors.append(f"Origine {i+1}: Date manquante")

        # Publication
        if "publication" not in imm:
            errors.append(f"Origine {i+1}: Publication manquante")
        else:
            pub = imm["publication"]
            if "service" not in pub:
                errors.append(f"Origine {i+1}: Service de publicité foncière manquant")

    return errors
```

### Étape 4 : Assemblage

Le template existant (lignes 320-326) génère automatiquement la section "Effet relatif" à partir des données JSON.

### Étape 5 : Annexes

**Obligatoire**: Annexer le titre de propriété complet à la promesse de vente pour traçabilité.

---

## Cas particuliers

### Cas 1 : Origines multiples

Si les lots ont des origines différentes:

```json
{
  "origine_propriete": [
    {
      "lots_concernes": [25],
      "origine_immediate": {
        "type": "acquisition",
        "vendeur_precedent": "Christian GROS",
        "notaire": "Maître PAGLIAROLI, notaire à Saint Alban de Roche",
        "date": "30 juin 2014",
        "publication": {
          "service": "LYON 5ème",
          "date": "24 juillet 2014",
          "volume": "2014P",
          "numero": "4164"
        }
      }
    },
    {
      "lots_concernes": [7],
      "origine_immediate": {
        "type": "donation",
        "vendeur_precedent": "Marie MARTIN",
        "notaire": "Maître DUPONT, notaire à Lyon",
        "date": "15 mars 2010",
        "publication": {
          "service": "LYON 5ème",
          "date": "28 mars 2010",
          "volume": "2010P",
          "numero": "1234"
        }
      }
    }
  ]
}
```

**Rendu**:
```
# Effet relatif

**Concernant le lot numéro 25**
Acquisition suivant acte reçu par Maître PAGLIAROLI, notaire à Saint Alban de Roche le 30 juin 2014, publié au service de la publicité foncière de LYON 5ème le 24 juillet 2014, volume 2014P, numéro 4164.

**Concernant le lot numéro 7**
Donation suivant acte reçu par Maître DUPONT, notaire à Lyon le 15 mars 2010, publié au service de la publicité foncière de LYON 5ème le 28 mars 2010, volume 2010P, numéro 1234.
```

### Cas 2 : VEFA (Vente en l'État Futur d'Achèvement)

Ajouter "vefa" aux types d'acquisition dans le schéma:

```json
{
  "type": { "enum": ["acquisition", "succession", "donation", "licitation", "partage", "adjudication", "vefa"] }
}
```

### Cas 3 : Succession avec détails

Pour une succession, capturer le nom du défunt dans `vendeur_precedent`:

```json
{
  "origine_immediate": {
    "type": "succession",
    "vendeur_precedent": "Jean GROS (défunt) et Suzanne DUMOLLARD (défunte)",
    "notaire": "Maître DUBOIS, notaire à Lyon",
    "date": "5 novembre 2013",
    "publication": {
      "service": "LYON 5ème",
      "date": "18 novembre 2013",
      "volume": "2013P",
      "numero": "5678"
    }
  }
}
```

---

## Modifications du schéma (OBLIGATOIRES)

### Fichier: `schemas/variables_promesse_vente.json`

**Modification 1**: Ajouter "vefa" aux types d'acquisition

```json
{
  "origine_propriete": {
    "type": "array",
    "items": {
      "properties": {
        "origine_immediate": {
          "properties": {
            "type": {
              "enum": ["acquisition", "succession", "donation", "licitation", "partage", "adjudication", "vefa"]
            }
          }
        }
      }
    }
  }
}
```

**Modification 2**: Rendre `origine_propriete` obligatoire pour promesse de vente

```json
{
  "required": ["acte", "promettant", "beneficiaire", "bien", "prix", "indemnite_immobilisation", "delais", "origine_propriete"]
}
```

### Fichier: `schemas/questions_promesse_vente.json`

**Modification**: Ajouter "VEFA" aux options de type d'acquisition

```json
{
  "16_origine_propriete": {
    "questions": [
      {
        "id": "origine_type",
        "question": "Type d'acquisition par le promettant ?",
        "type": "choix",
        "options": ["Acquisition", "Succession", "Donation", "Licitation", "Partage", "Adjudication", "VEFA"],
        "obligatoire": true,
        "variable": "origine_propriete[].origine_immediate.type"
      }
    ]
  }
}
```

---

## Script d'extraction (Future amélioration)

### `execution/extraire_origine_titre.py`

```python
"""
Script d'extraction de l'origine de propriété depuis un titre de propriété PDF.

Usage:
    python execution/extraire_origine_titre.py --pdf docs_original/titre.pdf --output .tmp/origine.json
"""

import argparse
import json
import re
from pathlib import Path

# Import PDF parsing library (PyMuPDF, pdfplumber, etc.)
import pdfplumber

def extraire_section_origine(pdf_path):
    """Extrait la section ORIGINE DE PROPRIETE du PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        texte_complet = ""
        for page in pdf.pages:
            texte_complet += page.extract_text()

    # Détecter la section ORIGINE
    match = re.search(r"ORIGINE DE PROPRIETE(.*?)(?=\n\n[A-Z]{3,}|\Z)", texte_complet, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("Section ORIGINE DE PROPRIETE non trouvée dans le PDF")

    return match.group(1)

def parser_origine_immediate(texte_origine):
    """Parse le texte de l'origine pour extraire les données structurées"""
    # Pattern pour détecter type d'acquisition
    type_pattern = r"(Acquisition|Succession|Donation|Licitation|Partage|Adjudication|vente en l'état futur d'achèvement)"
    type_match = re.search(type_pattern, texte_origine, re.IGNORECASE)
    type_acq = type_match.group(1).lower() if type_match else "acquisition"
    if "futur" in type_acq:
        type_acq = "vefa"

    # Pattern pour notaire
    notaire_pattern = r"Maître ([A-ZÉÈ\s]+), notaire à ([A-Za-zÀ-ÿ\s-]+)"
    notaire_match = re.search(notaire_pattern, texte_origine)
    notaire = f"Maître {notaire_match.group(1)}, notaire à {notaire_match.group(2)}" if notaire_match else ""

    # Pattern pour date
    date_pattern = r"le (\d{1,2} [a-zû]+ \d{4})"
    date_match = re.search(date_pattern, texte_origine)
    date_acte = date_match.group(1) if date_match else ""

    # Pattern pour publication
    pub_pattern = r"publié au service de la publicité foncière de ([A-ZÀ-Ÿ\s\dèéême]+).*?le (\d{1,2} [a-zû]+ \d{4}),?\s*volume ([A-Z0-9]+),?\s*n°?\s*(\d+)"
    pub_match = re.search(pub_pattern, texte_origine)

    publication = {}
    if pub_match:
        publication = {
            "service": pub_match.group(1).strip(),
            "date": pub_match.group(2),
            "volume": pub_match.group(3),
            "numero": pub_match.group(4)
        }

    return {
        "type": type_acq,
        "vendeur_precedent": "",  # À extraire manuellement
        "notaire": notaire,
        "date": date_acte,
        "publication": publication
    }

def main():
    parser = argparse.ArgumentParser(description="Extrait l'origine de propriété d'un titre PDF")
    parser.add_argument("--pdf", required=True, help="Chemin vers le PDF du titre de propriété")
    parser.add_argument("--output", required=True, help="Fichier JSON de sortie")
    parser.add_argument("--lots", nargs="+", type=int, help="Numéros des lots concernés")

    args = parser.parse_args()

    # Extraire la section origine
    texte_origine = extraire_section_origine(args.pdf)

    # Parser l'origine immédiate
    origine_immediate = parser_origine_immediate(texte_origine)

    # Construire la structure JSON
    origine_propriete = {
        "origine_propriete": [
            {
                "lots_concernes": args.lots or [],
                "origine_immediate": origine_immediate
            }
        ]
    }

    # Sauvegarder
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(origine_propriete, f, indent=2, ensure_ascii=False)

    print(f"✅ Origine extraite et sauvegardée dans {args.output}")
    print("\n⚠️  IMPORTANT: Vérifier manuellement le champ 'vendeur_precedent'")

if __name__ == "__main__":
    main()
```

**Note**: Ce script est un prototype et nécessite des tests approfondis avec différents formats de titres de propriété.

---

## Checklist d'intégration

- [ ] Modifier `schemas/variables_promesse_vente.json` pour ajouter "vefa"
- [ ] Modifier `schemas/questions_promesse_vente.json` pour ajouter "VEFA"
- [ ] Rendre `origine_propriete` obligatoire dans le schéma
- [ ] Ajouter la validation dans `execution/valider_acte.py`
- [ ] Tester avec les données du PDF exemple (ACTE_AUTHENTIQUE_PAGES_1-39.pdf)
- [ ] Documenter dans `directives/creer_promesse_vente.md` la section origine
- [ ] (Optionnel) Créer le script `execution/extraire_origine_titre.py`
- [ ] (Optionnel) Enrichir le template pour supporter la chaîne complète (Option 2)

---

## Exemples de tests

### Test 1 : Origine simple (acquisition)

**Input JSON**:
```json
{
  "origine_propriete": [
    {
      "lots_concernes": [25, 7],
      "origine_immediate": {
        "type": "acquisition",
        "vendeur_precedent": "Christian GROS",
        "notaire": "Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche",
        "date": "30 juin 2014",
        "publication": {
          "service": "LYON 5ème",
          "date": "24 juillet 2014",
          "volume": "2014P",
          "numero": "4164"
        }
      }
    }
  ]
}
```

**Output attendu (dans le DOCX)**:
```
# Effet relatif

**Concernant les lots numéros 25, 7**
Acquisition suivant acte reçu par Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche le 30 juin 2014, publié au service de la publicité foncière de LYON 5ème le 24 juillet 2014, volume 2014P, numéro 4164.
```

### Test 2 : Origine succession

**Input JSON**:
```json
{
  "origine_propriete": [
    {
      "lots_concernes": [10],
      "origine_immediate": {
        "type": "succession",
        "vendeur_precedent": "Marie DUPONT (défunte)",
        "notaire": "Maître Jean MARTIN, notaire à Paris",
        "date": "12 janvier 2020",
        "publication": {
          "service": "PARIS 1er",
          "date": "25 janvier 2020",
          "volume": "2020P",
          "numero": "789"
        }
      }
    }
  ]
}
```

**Output attendu**:
```
# Effet relatif

**Concernant le lot numéro 10**
Succession suivant acte reçu par Maître Jean MARTIN, notaire à Paris le 12 janvier 2020, publié au service de la publicité foncière de PARIS 1er le 25 janvier 2020, volume 2020P, numéro 789.
```

### Test 3 : VEFA

**Input JSON**:
```json
{
  "origine_propriete": [
    {
      "lots_concernes": [1, 2],
      "origine_immediate": {
        "type": "vefa",
        "vendeur_precedent": "SCI LES JARDINS",
        "notaire": "Maître Sophie LEROY, notaire à Marseille",
        "date": "5 septembre 2018",
        "publication": {
          "service": "MARSEILLE 1er",
          "date": "20 septembre 2018",
          "volume": "2018P",
          "numero": "3456"
        }
      }
    }
  ]
}
```

**Output attendu**:
```
# Effet relatif

**Concernant les lots numéros 1, 2**
Vefa suivant acte reçu par Maître Sophie LEROY, notaire à Marseille le 5 septembre 2018, publié au service de la publicité foncière de MARSEILLE 1er le 20 septembre 2018, volume 2018P, numéro 3456.
```

---

## Voir aussi

- [directives/creer_promesse_vente.md](creer_promesse_vente.md) - Workflow complet de création
- [schemas/variables_promesse_vente.json](../schemas/variables_promesse_vente.json) - Schéma des variables
- [schemas/questions_promesse_vente.json](../schemas/questions_promesse_vente.json) - Questions à poser
- [templates/promesse_vente_lots_copropriete.md](../templates/promesse_vente_lots_copropriete.md) - Template Jinja2
- [docs_original/ACTE_AUTHENTIQUE_PAGES_1-39.pdf](../docs_original/ACTE_AUTHENTIQUE_PAGES_1-39.pdf) - Document de référence analysé

---

## Historique

| Date | Modification | Auteur |
|------|--------------|--------|
| 2026-01-23 | Création initiale suite à analyse du titre de propriété | Agent |
