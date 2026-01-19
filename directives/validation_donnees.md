# Directive : Validation des données

## Objectif

Garantir la cohérence et la complétude des données avant génération d'un acte notarial. La validation est effectuée par `execution/valider_acte.py`.

---

## Niveaux de validation

| Niveau | Description | Action |
|--------|-------------|--------|
| **ERREUR** | Bloquant - Acte ne peut pas être généré | Corriger obligatoirement |
| **AVERTISSEMENT** | Non bloquant - Possible anomalie | Informer le notaire, continuer si validé |
| **INFO** | Informatif | Mentionner, aucune action requise |

---

## Règles de validation par catégorie

### 1. Complétude des données

#### Champs obligatoires - ERREUR si manquants

**Acte :**
- `acte.date` - Date de l'acte
- `acte.reference` - Référence/numéro de répertoire

**Vendeur(s) :**
- `vendeurs[].civilite` - Monsieur/Madame
- `vendeurs[].prenoms` - Tous les prénoms
- `vendeurs[].nom` - Nom de famille
- `vendeurs[].profession` - Profession
- `vendeurs[].adresse` - Adresse complète
- `vendeurs[].naissance.date` - Date de naissance
- `vendeurs[].naissance.lieu` - Lieu de naissance
- `vendeurs[].nationalite` - Nationalité
- `vendeurs[].situation_matrimoniale` - Situation matrimoniale

**Acquéreur(s) :**
- Mêmes champs que vendeurs

**Bien :**
- `bien.adresse` - Adresse du bien
- `bien.cadastre.section` - Section cadastrale
- `bien.cadastre.numero` - Numéro de parcelle
- `bien.lots[]` - Au moins un lot

**Prix :**
- `prix.montant` - Prix de vente

---

### 2. Cohérence des quotités

#### Règle : Total = 100%

```
Somme(quotités vendues) = 100%
Somme(quotités acquises) = 100%
```

**Validation :**
```python
def valider_quotites(quotites):
    total = sum(q.fraction for q in quotites)
    if total != 1.0:  # 1.0 = 100%
        return ERREUR, f"Total quotités = {total*100}% (attendu: 100%)"
    return OK
```

**Exemples valides :**
- 1/2 + 1/2 = 100% ✓
- 1/3 + 1/3 + 1/3 = 100% ✓
- 60% + 40% = 100% ✓

**Exemples invalides :**
- 1/2 + 1/3 = 83.3% ✗ (ERREUR)
- 50% + 50% + 10% = 110% ✗ (ERREUR)

---

### 3. Cohérence des prêts

#### Règle : Montant prêts ≤ Prix + Frais estimés

```python
def valider_prets(prets, prix):
    total_prets = sum(p.montant for p in prets)
    seuil = prix * 1.15  # Prix + 15% frais estimés

    if total_prets > seuil:
        return AVERTISSEMENT, f"Total prêts ({total_prets}€) > Prix + frais estimés ({seuil}€)"
    return OK
```

**Note** : C'est un avertissement, pas une erreur, car les prêts peuvent inclure les frais de notaire.

---

### 4. Superficie Carrez

#### Règle : Obligatoire pour lots > 8m²

```python
def valider_carrez(lot):
    if lot.type in ['appartement', 'local_commercial', 'bureau']:
        if lot.superficie_carrez is None:
            return ERREUR, f"Superficie Carrez obligatoire pour lot n°{lot.numero}"
    return OK
```

**Exemples :**
- Appartement 68m² sans Carrez → ERREUR
- Cave 5m² sans Carrez → OK (< 8m²)
- Parking sans Carrez → OK (non concerné)

---

### 5. Cohérence des dates

#### Règle : Ordre chronologique logique

```python
def valider_dates(donnees):
    erreurs = []

    # Date acte dans le futur ou aujourd'hui
    if donnees.acte.date < date.today():
        erreurs.append(AVERTISSEMENT, "Date de l'acte dans le passé")

    # Date naissance < Date acte
    for personne in donnees.vendeurs + donnees.acquereurs:
        if personne.naissance.date >= donnees.acte.date:
            erreurs.append(ERREUR, f"Date naissance {personne.nom} >= date acte")

    # Date origine propriété < Date acte
    if donnees.origine.date >= donnees.acte.date:
        erreurs.append(ERREUR, "Date origine propriété >= date acte")

    return erreurs
```

---

### 6. Régime matrimonial et intervention du conjoint

#### Règle : Si marié en communauté, le conjoint doit intervenir

```python
def valider_regime_matrimonial(vendeur, bien):
    if vendeur.situation_matrimoniale == 'marie':
        if vendeur.regime_matrimonial in ['communaute_legale', 'communaute_universelle']:
            if not vendeur.conjoint_intervient:
                return AVERTISSEMENT, f"Le conjoint de {vendeur.nom} devrait intervenir (bien commun probable)"
    return OK
```

---

### 7. Tantièmes de copropriété

#### Règle : Cohérence avec le total de la copropriété

```python
def valider_tantiemes(lots, total_copropriete):
    total_lots = sum(lot.tantiemes for lot in lots)

    # Les tantièmes des lots vendus doivent être <= total copropriété
    if total_lots > total_copropriete:
        return ERREUR, f"Total tantièmes lots ({total_lots}) > total copropriété ({total_copropriete})"

    return OK
```

---

### 8. Références et publications

#### Règle : Format valide

**Références cadastrales :**
```python
def valider_cadastre(cadastre):
    # Section : 1 ou 2 lettres majuscules
    if not re.match(r'^[A-Z]{1,2}$', cadastre.section):
        return ERREUR, f"Section cadastrale invalide: {cadastre.section}"

    # Numéro : chiffres uniquement
    if not cadastre.numero.isdigit():
        return ERREUR, f"Numéro parcelle invalide: {cadastre.numero}"

    return OK
```

**Références de publication :**
```python
def valider_publication(pub):
    # SPF : format attendu "SPF de [ville]"
    # Volume et numéro : entiers positifs
    if pub.volume <= 0 or pub.numero <= 0:
        return AVERTISSEMENT, "Références de publication incomplètes"
    return OK
```

---

## Usage du script de validation

### Commande de base

```bash
python execution/valider_acte.py \
    --donnees .tmp/donnees_client.json \
    --schema schemas/variables_vente.json
```

### Options

| Option | Description |
|--------|-------------|
| `--donnees` | Fichier JSON des données à valider |
| `--schema` | Schéma JSON de référence |
| `--strict` | Mode strict : avertissements = erreurs |
| `--output` | Fichier JSON de sortie avec résultats |

### Exemple de sortie

```json
{
  "statut": "valide_avec_avertissements",
  "erreurs": [],
  "avertissements": [
    {
      "code": "PRET_SUPERIEUR_PRIX",
      "message": "Total prêts (300 000 €) > Prix + frais (290 000 €)",
      "champs": ["paiement.prets"]
    }
  ],
  "infos": [
    {
      "code": "PRIMO_ACCEDANT",
      "message": "L'acquéreur est primo-accédant (éligible PTZ)"
    }
  ]
}
```

---

## Workflow de validation

```
DONNÉES COLLECTÉES
       │
       ▼
┌──────────────────┐
│ valider_acte.py  │
└──────────────────┘
       │
       ├─── ERREURS ? ──► Retour au notaire pour correction
       │         │
       │         └──► Corriger et relancer validation
       │
       ├─── AVERTISSEMENTS ? ──► Informer le notaire
       │         │
       │         ├──► Notaire valide → Continuer
       │         └──► Notaire refuse → Corriger
       │
       └─── OK ──► Génération de l'acte
```

---

## Ajout de nouvelles règles

Pour ajouter une règle de validation :

1. **Identifier la règle** et son niveau (ERREUR/AVERTISSEMENT/INFO)

2. **Implémenter dans `valider_acte.py`** :
```python
def valider_nouvelle_regle(donnees):
    """Description de la règle."""
    if condition_non_respectee:
        return Resultat(
            niveau=Niveau.ERREUR,
            code="CODE_ERREUR",
            message="Description du problème",
            champs=["chemin.vers.champ"]
        )
    return None
```

3. **Ajouter au pipeline de validation** :
```python
validations = [
    valider_completude,
    valider_quotites,
    valider_prets,
    valider_carrez,
    valider_dates,
    valider_nouvelle_regle,  # Nouvelle règle
]
```

4. **Documenter ici** dans cette directive

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création initiale | Agent |

---

## Voir aussi

- [execution/valider_acte.py](../execution/valider_acte.py) - Script de validation
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma de référence
- [directives/collecte_informations.md](collecte_informations.md) - Collecte des données
- [directives/creer_acte.md](creer_acte.md) - Flux de création
