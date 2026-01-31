# Analyse Comparative des 4 Trames de Promesse de Vente

**Date**: 2026-01-28 | **Version**: 1.0

---

## Résumé Exécutif

| Métrique | ORIGINAL | Trame A | Trame B | Trame C |
|----------|----------|---------|---------|---------|
| **Bookmarks** | 298 | 423 | 359 | 312 |
| **Tableaux** | 5 | 20 | 5 | 5 |
| **Parties (CompPP)** | 16 | 22 | 24 | 12 |
| **Lots (PXLOT)** | 12 | 12 | 12 | 9 |
| **Diagnostics** | 4 | 5 | 7 | 3 |
| **Mobilier (PZMOB)** | 0 | 18 | 0 | 13 |
| **Annexes** | 19 | 29 | 32 | 13 |

**Bookmarks communs aux 4 trames**: Seulement **16** (DOC_CONTENT, PYPROME, WdAnnexe1-9, etc.)

**Conclusion**: Les 4 trames sont **profondément différentes** et modélisent des cas d'usage distincts.

---

## 1. Cas d'Usage par Trame

| Trame | Cas d'Usage | Caractéristiques |
|-------|-------------|------------------|
| **ORIGINAL** | 1 bien copropriété simple | Pas de mobilier, diagnostics minimaux |
| **Trame A** | Multi-propriétés (3 biens) | 3 adresses, 3 cadastres, mobilier (24 items) |
| **Trame B** | Premium professionnel | Diagnostics exhaustifs, localisation détaillée |
| **Trame C** | Avec mobilier simplifié | Mobilier (19 items), diagnostics en tableau |

---

## 2. Variations par Catégorie

### 2.1 Parties et Situations Matrimoniales (CompPP)

- **ORIGINAL**: 16 variantes (base)
- **Trame A**: 22 variantes (+6 statuts complexes)
- **Trame B**: 24 variantes (LE PLUS COMPLET)
- **Trame C**: 12 variantes (RÉDUIT)

**Nouveaux statuts dans A/B**:
- `CompPPHEMAFCO` (homme marié + femme célibataire, régime commun)
- `CompPPFSDCHCO` (femme en séparation + homme célibataire)
- Variantes couples mixtes avec régimes différents

### 2.2 Mobilier Inclus (PZMOB)

| Trame | PZMOB | Tableau | Structure |
|-------|-------|---------|-----------|
| ORIGINAL | Absent | - | Immobilier uniquement |
| A | 18 | [24 x 2] | Désignation + État/Valeur |
| B | Absent | - | Immobilier uniquement |
| C | 13 | [19 x 2] | Désignation + État/Valeur |

### 2.3 Diagnostics Techniques (PDIAG)

- **ORIGINAL**: 4 bookmarks (minimal)
- **Trame A**: 5 (+1)
- **Trame B**: 7 (PLUS COMPLET - PDIAGTITRE, PDIAGOLO, PDIAGLOV, PDIAGLV3)
- **Trame C**: 3 (mais dans un tableau unifié de 15 lignes)

### 2.4 Annexes (WdAnnexe)

- **ORIGINAL**: 19 annexes (base)
- **Trame A**: 29 (+10)
- **Trame B**: 32 (VERSION CORPORATE COMPLÈTE)
- **Trame C**: 13 (VERSION SIMPLIFIÉE)

---

## 3. Structure des Tableaux

### ORIGINAL (5 tableaux - cas standard)

| # | Dimensions | Contenu |
|---|-----------|---------|
| 1 | 2 x 4 | Section cadastrale |
| 2 | 19 x 5 | Référence cadastrale détaillée |
| 3 | 10 x 2 | Prix et ventilation |
| 4 | 13 x 4 | Objets/Spécifications |
| 5 | 6 x 1 | Précisions |

### Trame A (20 tableaux - multi-propriétés)

```
Tableaux 1-11: REPETITION 3 FOIS de:
  - [7 x 2] Lieu de situation du bien
  - [2 x 4] Section
  - [3 x 4] Section détail
  - [1 x 1] Total surface

Tableau 12: [24 x 2] Désignation des meubles
Tableaux 13-15: Prix, objets, précisions
```

### Trame B (5 tableaux - premium)

| # | Dimensions | Différence |
|---|-----------|-----------|
| 1 | 7 x 2 | Lieu de situation DÉTAILLÉ (7 lignes) |
| 2-5 | Standard | Comme ORIGINAL |

### Trame C (5 tableaux - avec mobilier)

| # | Dimensions | Contenu |
|---|-----------|---------|
| 1 | 2 x 4 | Section cadastrale |
| 2 | 19 x 2 | Désignation des meubles |
| 3 | 10 x 2 | Prix et ventilation |
| 4 | 15 x 1 | Dossier diagnostics techniques |
| 5 | 6 x 1 | Précisions |

---

## 4. Matrice de Compatibilité

| Domaine | ORIGINAL | Trame A | Trame B | Trame C |
|---------|----------|---------|---------|---------|
| **Parties** | Standard | Étendu | Complet | Réduit |
| **Lots copropriété** | 12 | 12 | 12 | 9 |
| **Mobilier** | Non | Oui (24) | Non | Oui (19) |
| **Adresse bien** | Simple | Simple | Détaillée (7 champs) | Simple |
| **Diagnostics** | 4 | 5 | 7 | 3 (tableau) |
| **Annexes** | 19 | 29 | 32 | 13 |
| **Cadastre** | 1 | 3 | 1 | 1 |

---

## 5. Recommandations

### Option Recommandée: 4 Templates Séparés

```
promesse_vente_lots_copropriete.md  (Copropriété - appartement, lots)
promesse_hors_copropriete.md        (Hors copropriété - maison, local)
promesse_terrain_a_batir.md         (Terrain à bâtir - lotissement)
```

### Détection Automatique du Type

```python
def detecter_type_promesse(donnees):
    bien = donnees.get('bien', {})

    # Niveau 1: Catégorie de bien
    if bien.get('lotissement') or bien.get('type') == "terrain":
        return "promesse_terrain_a_batir.md"
    elif bien.get('copropriete') or bien.get('syndic'):
        return "promesse_vente_lots_copropriete.md"
    else:
        return "promesse_hors_copropriete.md"
```

---

## 6. Variables Communes (16 bookmarks)

Ces variables sont présentes dans les 4 trames:

- `DOC_CONTENT` - Contenu principal
- `PYPROME` - Identification promesse
- `WdAnnexe1` à `WdAnnexe9` - Annexes de base
- Variables de prix de base
- Variables d'identification parties

---

## 7. Prochaines Étapes

1. **Court terme**: Utiliser le template ORIGINAL (88.9% conformité)
2. **Fait (v1.7.0)**: Templates par catégorie de bien (copro, hors-copro, terrain)
3. **Long terme**: Enrichir templates spécialisés selon retours notaires

---

*Document généré le 2026-01-28 pour le projet Notomai*
