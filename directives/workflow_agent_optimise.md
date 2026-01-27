# Workflow Agent Optimisé - Notomai v1.3

> Directive consolidée pour un agent de génération d'actes notariaux excellent
> Version: 1.3.0 - Janvier 2026

---

## Vue d'Ensemble

Ce document définit le workflow optimisé pour la génération d'actes de promesse de vente et de vente. Il intègre toutes les leçons apprises et les meilleures pratiques.

### Capacités de l'Agent

| Fonctionnalité | Statut | Description |
|----------------|--------|-------------|
| Parsing langage naturel | ✅ v1.0 | Regex avancé + 73 patterns |
| Détection d'intention | ✅ v1.0 | 8 intentions (créer, modifier, etc.) |
| **Multi-parties** | ✅ v1.1 | "Martin & Pierre → Dupont & Thomas" |
| **Validation intégrée** | ✅ v1.1 | Vérification avant génération |
| **Score confiance détaillé** | ✅ v1.1 | Breakdown par catégorie |
| Génération DOCX | ✅ v1.0 | 100% fidèle aux trames |

---

## Workflow en 8 Étapes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW AGENT OPTIMISÉ                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. RÉCEPTION        Demande en langage naturel                        │
│       ↓                                                                 │
│  2. PARSING          Extraction entités + intentions                   │
│       ↓                                                                 │
│  3. SCORE            Calcul confiance détaillé                         │
│       ↓              (si < 70% → suggestions)                          │
│  4. CONSTRUCTION     Fusion données exemple + extraites                │
│       ↓                                                                 │
│  5. VALIDATION       Vérification complétude + cohérence              │
│       ↓              (si erreurs → arrêt + message)                    │
│  6. ASSEMBLAGE       Template Jinja2 → Markdown                        │
│       ↓                                                                 │
│  7. EXPORT           Markdown → DOCX formaté                           │
│       ↓                                                                 │
│  8. VÉRIFICATION     Comparaison structure → score conformité         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Étape 1: Réception de la Demande

### Formats Supportés

```python
# Format simple
"Crée une promesse Martin → Dupont, 450000€"

# Format avec bien
"Promesse Martin → Dupont, appartement 67m² Paris, 450k€"

# Format multi-parties (NOUVEAU v1.1)
"Promesse Martin & Pierre → Dupont & Thomas, maison 120m², 650000€"

# Format explicite
"Crée un acte de vente pour vendeur Martin vers acquéreur Dupont, prix 300000 euros"
```

### Exemples de Demandes

| Demande | Intention | Type | Confiance |
|---------|-----------|------|-----------|
| "Crée promesse Martin→Dupont 450k€" | CREER | promesse_vente | 85% |
| "Martin & Pierre → Dupont & Thomas" | CREER | promesse_vente | 75% |
| "Modifie le prix à 460k€ dans 2026-001" | MODIFIER | - | 90% |
| "Liste tous les actes pour Martin" | RECHERCHER | - | 85% |

---

## Étape 2: Parsing Langage Naturel

### Patterns Clés

```python
# Multi-parties (NOUVEAU v1.1)
PATTERN_FLECHE_MULTI = re.compile(
    r'(?P<vendeurs>Nom(?:\s*(?:&|et)\s*Nom)*)\s*'
    r'(?:→|->|vers)\s*'
    r'(?P<acquereurs>Nom(?:\s*(?:&|et)\s*Nom)*)'
)

# Prix
PATTERN_PRIX = re.compile(r'(\d[\d\s]*)\s*(€|euros?|k€?)')

# Surface
PATTERN_SURFACE = re.compile(r'(\d+(?:[.,]\d+)?)\s*m[²2]')
```

### Entités Extraites

| Entité | Pattern | Exemple |
|--------|---------|---------|
| vendeur | Nom avant → | "Martin" |
| vendeurs_multiples | Noms avant → séparés par & | ["Martin", "Pierre"] |
| acquereur | Nom après → | "Dupont" |
| acquereurs_multiples | Noms après → séparés par & | ["Dupont", "Thomas"] |
| prix | Nombre + €/euros/k | 450000 |
| surface | Nombre + m² | 67.0 |
| ville | Liste 50+ villes | "Paris" |
| type_bien | appartement/maison/etc | "appartement" |

---

## Étape 3: Score de Confiance Détaillé

### Calcul (NOUVEAU v1.1)

```python
@dataclass
class ScoreConfianceDetaille:
    score_global: float      # Moyenne pondérée

    # Par catégorie
    score_vendeur: float     # Poids: 20%
    score_acquereur: float   # Poids: 20%
    score_bien: float        # Poids: 15%
    score_prix: float        # Poids: 20%
    score_type_acte: float   # Poids: 15%
    score_intention: float   # Poids: 10%

    # Détails
    champs_detectes: List[str]
    champs_manquants: List[str]
    suggestions: List[str]
```

### Interprétation

| Score Global | Interprétation | Action |
|--------------|----------------|--------|
| ≥ 85% | Excellent | Génération directe |
| 70-84% | Bon | Génération avec avertissements |
| 50-69% | Moyen | Afficher suggestions, demander confirmation |
| < 50% | Faible | Demander plus d'informations |

### Exemple de Sortie

```
🔍 Analyse:
   • Intention: creer
   • Type acte: promesse_vente
   • Confiance: 72%
   • Vendeurs (2): MARTIN & PIERRE
   • Acquéreurs (2): DUPONT & THOMAS
   • Prix: 450,000€

   💡 Suggestions:
      → Préciser le type de bien et sa localisation
      → Vérifier les quotités acquises pour chaque acquéreur
```

---

## Étape 4: Construction des Données

### Fusion Intelligente

1. **Charger données d'exemple** comme base (deep copy)
2. **Fusionner** les données extraites (ne pas écraser les structures complètes)
3. **Gérer multi-parties** : créer des entrées pour chaque personne

### Règles de Fusion

```python
# Multi-parties: créer autant d'entrées que de personnes
if len(vendeurs_multiples) > 1:
    donnees['promettants'] = [
        fusionner(modele, vendeur)
        for vendeur in vendeurs_multiples
    ]

# Un seul: modifier l'existant
else:
    fusionner(donnees['promettants'][0], vendeur)
```

### Normalisation Automatique

| Source | Cible | Transformation |
|--------|-------|----------------|
| "450k€" | prix.montant | 450000 |
| "67m²" | bien.superficie | 67.0 |
| "Martin" | nom | "MARTIN" (uppercase) |
| "Paris" | bien.ville | "Paris" |

---

## Étape 5: Validation des Données

### Champs Obligatoires par Type

| Type Acte | Champs Obligatoires |
|-----------|---------------------|
| promesse_vente | promettants, beneficiaires, bien, prix |
| vente | vendeurs, acquereurs, bien, prix |
| reglement_copropriete | immeuble, lots |
| modificatif_edd | immeuble, modifications |

### Validations Spécifiques

```python
# Prix > 0
if prix.montant <= 0:
    erreurs.append("Le prix doit être supérieur à 0")

# Quotités si multi-parties
if len(vendeurs) > 1:
    suggestions.append("Vérifier les quotités vendues pour chaque vendeur")

# Conditions suspensives pour promesse
if type_acte == 'promesse_vente':
    if not conditions_suspensives:
        avertissements.append("Aucune condition suspensive définie")
```

### Résultat Validation

```python
@dataclass
class ResultatValidation:
    valide: bool                    # False si erreurs bloquantes
    erreurs: List[str]              # Bloquent la génération
    avertissements: List[str]       # Affichés mais n'empêchent pas
    champs_manquants: List[str]     # Pour information
    suggestions: List[str]          # Conseils d'amélioration
```

---

## Étape 6: Assemblage Template

### Templates Disponibles

| Template | Conformité | Statut |
|----------|------------|--------|
| `promesse_vente_lots_copropriete.md` | ≥85% | ✅ PROD |
| `vente_lots_copropriete.md` | 85.1% | ✅ PROD |
| `reglement_copropriete_edd.md` | 85.5% | ✅ PROD |
| `modificatif_edd.md` | 91.7% | ✅ PROD |

### Structure Promesse (NOUVEAU v1.1)

```markdown
{# En-tête #}
PROMESSE UNILATERALE DE VENTE

{# Parties - support multi-parties #}
{% for promettant in promettants %}
{{ promettant.civilite }} {{ promettant.nom }}...
{% endfor %}

{# Bien #}
# DÉSIGNATION DU BIEN

{# Prix #}
# PRIX ET PAIEMENT

{# NOUVEAU: Partie développée promesse #}
{% include 'sections/partie_developpee_promesse.md' %}

{# Partie développée commune #}
{% include 'sections/partie_developpee.md' %}

DONT ACTE
```

### Sections Spécifiques Promesse

| Section | Contenu |
|---------|---------|
| CONDITIONS SUSPENSIVES | Prêt, vente préalable, urbanisme |
| DÉLAI DE RÉALISATION | Durée, date butoir, prorogation |
| INDEMNITÉ D'IMMOBILISATION | Montant, versement, sort |
| FACULTÉ DE SUBSTITUTION | Conditions, effets |
| CLAUSE PÉNALE | Inexécution promettant/bénéficiaire |

---

## Étape 7: Export DOCX

### Formatage Fixe

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| Police | Times New Roman 11pt | Trame originale |
| Marges | G=60mm, D=15mm, H/B=25mm | Trame originale |
| Retrait 1ère ligne | 12.51mm | Trame originale |
| Interligne | Simple | Trame originale |
| Zones grisées | Actives (#D9D9D9) | Standard notarial |

### Styles Headings

| Niveau | Style | Exemple |
|--------|-------|---------|
| # | Bold, ALL CAPS, underline, centré | PROMETTANT |
| ## | Bold, small caps, underline, centré | Coordonnées |
| ### | Bold, underline, centré | Condition suspensive |
| #### | Bold only, 6pt avant | Détail |

---

## Étape 8: Vérification Conformité

### Seuil de Production

- **≥ 80%** : Template production, génération directe
- **< 80%** : Template développement, utiliser données exemple

### Commande de Test

```bash
python execution/comparer_documents_v2.py \
    outputs/acte_genere.docx \
    docs_originels/Trame_promesse.docx
```

### Rapport de Conformité

```
📊 RAPPORT DE CONFORMITÉ
========================
Score global: 87.3%

✅ Sections présentes: 45/52 (87%)
✅ Structure headings: OK
✅ Formatage: OK
⚠️ Sections manquantes:
   - Plus-values immobilières (optionnel)
   - Diagnostics électricité (optionnel)
```

---

## Commandes CLI

### Génération Rapide

```bash
# Promesse simple
python notaire.py agent "Crée promesse Martin → Dupont, 450000€"

# Promesse multi-parties
python notaire.py agent "Promesse Martin & Pierre → Dupont & Thomas, appart 67m², 450k€"

# Vente depuis dossier existant
python notaire.py generer 2026-0127 --type vente
```

### Validation

```bash
# Valider des données
python notaire.py valider donnees.json --type promesse_vente

# Statut des templates
python notaire.py template status
```

### Debug

```bash
# Mode verbose
python notaire.py agent "..." --debug

# Preview sans génération
python notaire.py agent "..." --preview
```

---

## Checklist Agent Excellent

### Parsing
- [x] Support multi-parties (& / et)
- [x] Extraction prix avec k€
- [x] Extraction surface m²
- [x] 50+ villes françaises
- [x] 10+ types de biens

### Intelligence
- [x] Score confiance détaillé
- [x] Suggestions contextuelles
- [x] Validation intégrée
- [x] Avertissements proactifs

### Templates
- [x] Promesse avec partie développée
- [x] Vente avec partie développée
- [x] Règlement copropriété
- [x] Modificatif EDD

### Génération
- [x] Zones grisées pour variables
- [x] En-tête première page
- [x] Formatage 100% fidèle
- [x] Tableaux avec largeurs proportionnelles

### UX
- [x] Messages d'erreur clairs
- [x] Suggestions d'amélioration
- [x] Affichage multi-parties
- [x] Résumé de génération

---

## Évolutions Futures

### Court terme (1-2 semaines)
- [ ] Mode interactif (questions/réponses)
- [ ] CLI `template status`
- [ ] Tests automatisés E2E

### Moyen terme (1 mois)
- [ ] Apprentissage des corrections
- [ ] NLP amélioré (spaCy)
- [ ] Dashboard analytics

### Long terme (3 mois)
- [ ] API REST complète
- [ ] Multi-tenant production
- [ ] Intégration GED notariales

---

*Directive créée le 27 janvier 2026*
*Notomai v1.3.0*
