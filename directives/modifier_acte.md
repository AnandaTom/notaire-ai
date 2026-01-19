# Directive : Modification d'un Acte Notarial Existant

## Objectif
Modifier un acte notarial existant (vente ou promesse de vente) en préservant l'intégrité du document et en assurant la traçabilité des modifications.

## Prérequis
- Un acte existant (généré par le système ou importé)
- Le notaire a identifié la ou les modifications à apporter
- Accès aux données JSON de l'acte

## Types de modifications supportées

### 1. Corrections de données
- Erreur de saisie (nom, date, adresse)
- Mise à jour d'informations (nouvelle adresse, changement de situation)
- Correction de références (cadastre, publication)

### 2. Ajout/Retrait de sections
- Ajout d'un prêt supplémentaire
- Retrait de la section meubles
- Ajout d'une condition suspensive
- Modification des travaux récents

### 3. Modifications structurelles
- Ajout/retrait d'un vendeur ou acquéreur
- Modification des quotités
- Changement de lots

---

## Flux de travail

### Étape 1 : Identification de l'acte à modifier

**Question au notaire :**
> Quel acte souhaitez-vous modifier ?
> - Numéro de répertoire / référence interne
> - Ou fournir le fichier JSON des données

**Script utilisé :**
```bash
# Lister les actes existants
ls .tmp/actes_generes/
```

**Sortie :** Chemin vers le dossier de l'acte (`{id_acte}`)

---

### Étape 2 : Chargement des données existantes

**Script à exécuter :**
```bash
# Charger les données existantes
python -c "import json; print(json.dumps(json.load(open('.tmp/actes_generes/{id_acte}/donnees.json')), indent=2, ensure_ascii=False))"
```

**Sortie :** Données JSON de l'acte actuel

---

### Étape 3 : Identification de la modification

**Question au notaire :**
> Quelle modification souhaitez-vous apporter ?

**Catégorisation automatique :**

| Type de demande | Catégorie | Action |
|-----------------|-----------|--------|
| "Corriger le nom du vendeur" | Correction de données | Modifier `vendeurs[x].nom` |
| "Ajouter un prêt" | Ajout de section | Ajouter dans `paiement.prets[]` |
| "Retirer les meubles" | Retrait de section | Mettre `meubles.inclus = false` |
| "Changer le prix" | Correction de données | Modifier `prix.montant` |
| "Ajouter un acquéreur" | Modification structurelle | Ajouter dans `acquereurs[]` + ajuster quotités |

---

### Étape 4 : Application de la modification

#### 4.1 Pour les corrections de données simples

**Exemple : Corriger le nom d'un vendeur**

```python
# Identifier le chemin JSON
chemin = "vendeurs[0].nom"
ancienne_valeur = "DURAND"
nouvelle_valeur = "DURANT"

# Appliquer la modification
donnees["vendeurs"][0]["nom"] = "DURANT"
```

**Validation :**
- Vérifier que le format est correct
- Vérifier la cohérence (ex: si nom change, vérifier les références)

#### 4.2 Pour les ajouts de sections

**Exemple : Ajouter un prêt**

**Questions supplémentaires :**
- Établissement prêteur ?
- Montant du prêt ?
- Durée en mois ?
- Taux d'intérêt ?
- Type de garantie ?

```python
nouveau_pret = {
    "etablissement": {
        "nom": "BANQUE POPULAIRE",
        "forme_juridique": "SA",
        "siege": "LYON",
        "siren": "123456789",
        "rcs": "LYON"
    },
    "reference": "PRET 12345",
    "montant": 50000,
    "duree_mois": 180,
    "taux": 3.5,
    "type_garantie": "hypotheque_legale_preteur"
}

donnees["paiement"]["prets"].append(nouveau_pret)
```

#### 4.3 Pour les modifications structurelles

**Exemple : Ajouter un acquéreur**

**Questions obligatoires :**
- Toutes les informations de la personne (voir directive création)
- Nouvelles quotités pour TOUS les acquéreurs

**Validation spéciale :**
- Total des quotités = 100%
- Cohérence des régimes matrimoniaux

---

### Étape 5 : Validation des modifications

**Script à exécuter :**
```bash
python execution/valider_acte.py --donnees .tmp/donnees_modifiees.json --schema schemas/variables_vente.json
```

**Gestion des erreurs :**
- Si erreur de validation → Corriger et recommencer
- Si avertissement → Informer le notaire, continuer si accord

---

### Étape 6 : Régénération de l'acte

**Script à exécuter :**
```bash
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_modifiees.json \
    --output .tmp/actes_generes/{id_acte}/ \
    --version 2
```

**Important :** Le script incrémente automatiquement la version et conserve l'historique.

---

### Étape 7 : Comparaison avant/après

**Présentation au notaire :**
> Voici les modifications apportées :
>
> **Avant :**
> - Vendeur : M. DURAND Jean
>
> **Après :**
> - Vendeur : M. DURANT Jean
>
> [Fichier PDF comparatif joint]
>
> Validez-vous ces modifications ?

**Script de comparaison (optionnel) :**
```bash
diff .tmp/actes_generes/{id_acte}/acte_v1.md .tmp/actes_generes/{id_acte}/acte_v2.md
```

---

### Étape 7bis : Choix du format d'export

**Question au notaire :**
> Dans quel format souhaitez-vous générer l'acte modifié ?
> - **PDF** : Document figé, prêt pour signature
> - **Word (DOCX)** : Document modifiable, annotations possibles

---

### Étape 8 : Export et archivage

**Si le notaire valide :**

**Format PDF :**
```bash
python execution/exporter_pdf.py \
    --input .tmp/actes_generes/{id_acte}/acte.md \
    --output .tmp/actes_generes/{id_acte}/acte_v2.pdf \
    --brouillon
```

**Format DOCX :**
```bash
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id_acte}/acte.md \
    --output .tmp/actes_generes/{id_acte}/acte_v2.docx \
    --brouillon
```

**Mise à jour des métadonnées :**
```json
{
    "id": "{id_acte}",
    "version": 2,
    "statut": "modifie",
    "date_creation": "2025-01-15",
    "date_modification": "2025-01-17",
    "historique": [
        {
            "version": 1,
            "date": "2025-01-15",
            "action": "creation"
        },
        {
            "version": 2,
            "date": "2025-01-17",
            "action": "modification",
            "description": "Correction nom vendeur DURAND -> DURANT"
        }
    ]
}
```

---

## Arbre de décision - Types de modifications

```
DEMANDE DE MODIFICATION
│
├─ Correction simple ?
│   ├─ Oui → Modifier directement dans JSON
│   │        → Valider
│   │        → Régénérer
│   │
│   └─ Non → Continuer ↓
│
├─ Ajout/Retrait de section ?
│   ├─ Ajout → Collecter infos manquantes
│   │         → Valider cohérence
│   │         → Régénérer
│   │
│   └─ Retrait → Confirmer avec notaire
│              → Mettre section à false/null
│              → Régénérer
│
└─ Modification structurelle ?
    ├─ Parties (vendeurs/acquéreurs)
    │   → Collecter nouvelles infos
    │   → Recalculer quotités
    │   → Valider (total = 100%)
    │   → Régénérer
    │
    └─ Bien (lots)
        → Collecter nouvelles infos
        → Vérifier tantièmes
        → Régénérer
```

---

## Exemples de dialogues

### Exemple 1 : Correction simple

**Notaire :** "Il y a une faute dans le nom du vendeur, c'est DURANT avec un T, pas DURAND"

**Agent :** "Je vais corriger le nom du vendeur de DURAND à DURANT.

Modification appliquée :
- Ancien : Madame Marie Jeanne DURAND
- Nouveau : Madame Marie Jeanne DURANT

Je régénère l'acte... Voici le projet modifié [PDF joint]. Validez-vous cette correction ?"

### Exemple 2 : Ajout d'un prêt

**Notaire :** "Il faut ajouter un prêt à taux zéro de la Caisse d'Épargne"

**Agent :** "Je vais ajouter un prêt supplémentaire. J'ai besoin des informations suivantes :
- Montant du prêt ?
- Durée en mois ?
- Référence du prêt ?
- Date de l'acte de prêt (si déjà signé) ?"

**Notaire :** "15 000 euros sur 180 mois, référence PTZ-2025-1234"

**Agent :** "Prêt ajouté avec les caractéristiques :
- Établissement : Caisse d'Épargne
- Montant : 15 000 EUR
- Durée : 180 mois (15 ans)
- Taux : 0% (PTZ)
- Référence : PTZ-2025-1234

Validation en cours... Le total des prêts (235 564 EUR + 24 400 EUR + 15 000 EUR = 274 964 EUR) est supérieur au prix (245 000 EUR). Cela inclut-il les frais de notaire ? [Oui/Non]"

### Exemple 3 : Modification des quotités

**Notaire :** "Les acquéreurs veulent changer les quotités : 60% pour M. MARTIN et 40% pour Mme BERNARD"

**Agent :** "Je vais modifier les quotités d'acquisition :

Avant :
- M. MARTIN Jean Philippe : 50% (la moitié)
- Mme BERNARD Sophie Anne : 50% (la moitié)

Après :
- M. MARTIN Jean Philippe : 60% (trois cinquièmes)
- Mme BERNARD Sophie Anne : 40% (deux cinquièmes)

Total : 100% ✓

Je régénère l'acte avec ces nouvelles quotités..."

---

## Points de vigilance

1. **Traçabilité** : Toujours documenter les modifications dans l'historique
2. **Cohérence** : Vérifier les impacts en cascade (ex: nom → références)
3. **Validation** : Toujours revalider après modification
4. **Versions** : Ne jamais écraser les versions précédentes
5. **Quotités** : Toujours vérifier que le total = 100%
6. **Prêts** : Vérifier la cohérence montant prêts vs prix

---

## Modifications interdites sans nouvel acte

Certaines modifications sont trop structurantes et nécessitent un nouvel acte :

- Changement de type d'acte (vente → promesse)
- Changement complet du bien (autre immeuble)
- Changement de tous les vendeurs ou acquéreurs
- Modification fondamentale du prix (variation > 20%)

Dans ces cas, informer le notaire :
> "Cette modification est trop importante pour une simple correction. Je vous recommande de créer un nouvel acte. Souhaitez-vous procéder ?"

---

## Formatage DOCX - Rappel CRITIQUE

Lors de la régénération, le formatage DOCX est **automatiquement identique** à la trame originale :

| Paramètre | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Marges | G=60mm, D=15mm, H/B=25mm |
| Retrait 1ère ligne | 12.51mm |

**Ne jamais modifier ces valeurs** - elles sont codées en dur dans `exporter_docx.py`.

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-17 | Création initiale | Agent |
| 2025-01-19 | Ajout rappel formatage DOCX, liens vers nouvelles directives | Agent |

---

## Voir aussi

- [directives/creer_acte.md](creer_acte.md) - Création d'un nouvel acte
- [directives/collecte_informations.md](collecte_informations.md) - Guide de collecte des informations
- [directives/formatage_docx.md](formatage_docx.md) - Spécifications formatage DOCX
- [directives/pipeline_generation.md](pipeline_generation.md) - Pipeline rapide
- [directives/validation_donnees.md](validation_donnees.md) - Règles de validation
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma des variables
- [schemas/questions_notaire.json](../schemas/questions_notaire.json) - Questions à poser
- [execution/valider_acte.py](../execution/valider_acte.py) - Script de validation
