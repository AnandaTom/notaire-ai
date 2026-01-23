# Guide Rapide : Origine de Propriété dans les Promesses de Vente

**Pour**: Notaires utilisant le système NotaireAI
**Temps de lecture**: 2 minutes
**Nouveauté**: Support du type "VEFA" ajouté

---

## En 3 Étapes

### 1️⃣ Récupérer le titre de propriété du vendeur

Demander au vendeur (promettant) son **titre de propriété** (acte authentique de la dernière acquisition).

**Exemple**: Acte de vente reçu par Maître X le JJ/MM/AAAA

### 2️⃣ Extraire l'origine immédiate

Dans la section **"ORIGINE DE PROPRIETE"** du titre, relever:

| Information | Exemple |
|-------------|---------|
| **Type d'acquisition** | Acquisition / Succession / Donation / VEFA |
| **Vendeur précédent** | Christian GROS |
| **Notaire** | Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche |
| **Date de l'acte** | 30 juin 2014 |
| **Service de publicité foncière** | LYON 5ème |
| **Date de publication** | 24 juillet 2014 |
| **Volume** | 2014P |
| **Numéro** | 4164 |

### 3️⃣ Répondre aux questions (Section 16)

Lors de la collecte des informations pour la promesse de vente:

```
Agent: Type d'acquisition par le promettant ?
Notaire: Acquisition

Agent: Nom du vendeur précédent ?
Notaire: Christian GROS

Agent: Notaire de l'acte d'origine ?
Notaire: Maître Mathieu PAGLIAROLI, notaire à Saint Alban de Roche

Agent: Date de l'acte ?
Notaire: 30 juin 2014

Agent: Service de publicité foncière ?
Notaire: LYON 5ème

Agent: Date de publication ?
Notaire: 24 juillet 2014

Agent: Volume ?
Notaire: 2014P

Agent: Numéro ?
Notaire: 4164
```

---

## Rendu dans la Promesse

La section **"Effet relatif"** sera générée automatiquement:

```
# Effet relatif

**Concernant les lots numéros 25, 7**
Acquisition suivant acte reçu par Maître Mathieu PAGLIAROLI,
notaire à Saint Alban de Roche le 30 juin 2014, publié au
service de la publicité foncière de LYON 5ème le 24 juillet 2014,
volume 2014P, numéro 4164.
```

---

## Types d'Acquisition Supportés

| Type | Quand l'utiliser |
|------|------------------|
| **Acquisition** | Vente classique |
| **Succession** | Héritage (décès) |
| **Donation** | Don entre vifs |
| **Licitation** | Vente suite à partage judiciaire |
| **Partage** | Partage amiable |
| **Adjudication** | Vente aux enchères |
| **VEFA** ⭐ | Vente en l'État Futur d'Achèvement (immeuble neuf) |

⭐ **Nouveau**: Le type "VEFA" est maintenant supporté (fréquent pour les immeubles des années 1970-1980).

---

## Cas Particuliers

### Cas 1 : Lots avec origines différentes

Si les lots ont des origines différentes (rare), répondre aux questions **deux fois** (une fois par origine).

**Exemple**:
- Lot 25 : acquisition 2014 de Christian GROS
- Lot 7 : donation 2010 de Marie MARTIN

→ Le système générera deux paragraphes distincts.

### Cas 2 : Succession

Pour une succession, indiquer le nom du défunt dans "Vendeur précédent":

```
Vendeur précédent: Jean GROS (défunt)
```

### Cas 3 : Chaîne d'origine longue

**Important**: Le système ne capture que **l'origine immédiate** (le dernier acte). La chaîne complète figure dans le titre de propriété qui doit être **annexé** à la promesse.

**Exemple**:
- 2014 : Acquisition par le vendeur actuel ← **CAPTURÉ**
- 1974/2013 : Successions ← Dans le titre annexé
- 1972 : VEFA originale ← Dans le titre annexé

---

## Annexes Obligatoires

**TOUJOURS** annexer à la promesse de vente:
- ✅ Le titre de propriété complet du vendeur
- ✅ Tous les documents mentionnés dans l'origine (actes de succession, etc.)

**Pourquoi?** La traçabilité complète de la chaîne d'origine doit figurer dans les annexes.

---

## Test Rapide

Pour tester avec les données d'exemple:

```bash
# Générer une promesse avec l'origine du PDF analysé
python execution/workflow_rapide.py \
    --donnees exemples/donnees_promesse_avec_origine.json \
    --template promesse_vente_lots_copropriete.md \
    --output outputs/test_origine.docx
```

**Résultat**: Promesse de vente avec section "Effet relatif" remplie.

---

## Aide-Mémoire

### Format du notaire
```
Maître [NOM], notaire à [VILLE]
```

### Format du service de publicité foncière
```
[VILLE] [ARRONDISSEMENT]
Exemple: LYON 5ème, PARIS 1er, MARSEILLE 2ème
```

### Format du volume
```
[ANNÉE]P
Exemple: 2014P, 2020P
```

---

## En Cas de Problème

| Problème | Solution |
|----------|----------|
| Type d'acquisition manquant | Ajouter "VEFA" maintenant supporté |
| Publication incomplète | Volume et numéro sont optionnels |
| Plusieurs vendeurs | Tous les noms séparés par "et" |
| Date manquante | Obligatoire - vérifier le titre |

---

## Documents de Référence

| Document | Usage |
|----------|-------|
| [ANALYSE_TITRE_PROPRIETE.md](ANALYSE_TITRE_PROPRIETE.md) | Analyse complète du PDF exemple |
| [directives/integration_titre_propriete.md](directives/integration_titre_propriete.md) | Documentation technique détaillée |
| [exemples/donnees_promesse_avec_origine.json](exemples/donnees_promesse_avec_origine.json) | Exemple complet de données |

---

**Version**: 1.0
**Date**: 23 janvier 2026
**Statut**: ✅ Opérationnel
