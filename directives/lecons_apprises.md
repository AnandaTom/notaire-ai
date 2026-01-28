# Leçons Apprises - NotaireAI

> Cette directive documente toutes les leçons apprises pendant le développement et les tests du système NotaireAI.

---

## 1. Gestion des Structures de Données

### Problème: Mismatch entre données générées et templates

**Constat**: Les données générées par `generer_donnees_test.py` utilisent une structure nested (`vendeur.personne_physique.situation_matrimoniale`) alors que les templates Jinja2 attendent une structure aplatie (`vendeur.situation_matrimoniale`).

**Solution implémentée**: [assembler_acte.py:370-399](../execution/assembler_acte.py#L370-L399)
```python
# Aplatir automatiquement dans enrichir_donnees()
for cle in ['vendeurs', 'acquereurs']:
    for i, personne in enumerate(donnees_enrichies[cle]):
        if 'personne_physique' in personne:
            donnees_enrichies[cle][i] = {**personne, **personne['personne_physique']}
            del donnees_enrichies[cle][i]['personne_physique']
```

**Leçon**: Toujours normaliser les structures de données dans le layer d'orchestration (`assembler_acte.py`) plutôt que dans le générateur. Cela permet de supporter plusieurs formats de données en entrée.

---

## 2. Normalisation PACS

### Problème: Incohérence nomenclature PACS

**Constat**:
- Les données utilisent `partenaire` mais le template attend `conjoint`
- Les données ont `date_pacs` flat mais le template attend `pacs.date`

**Solution implémentée**: [assembler_acte.py:386-399](../execution/assembler_acte.py#L386-L399) + [generer_donnees_test.py:161-168](../execution/generer_donnees_test.py#L161-L168)
```python
# 1. Générer avec structure complète
if sitmat.get("statut") == "pacse":
    sitmat["pacs"] = {
        "date": sitmat.get("date_pacs", ""),
        "regime_libelle": sitmat.get("regime_pacs", "séparation de biens"),
        "lieu_enregistrement": sitmat.get("lieu_pacs", "...")
    }
    sitmat["conjoint"] = sitmat["partenaire"]  # Alias

# 2. Normaliser dans assembler si besoin
```

**Leçon**: Créer des alias de compatibilité dès la génération plutôt que de modifier les templates existants.

---

## 3. Encodage Unicode sur Windows

### Problème: `UnicodeEncodeError` avec caractères spéciaux

**Constat**: Les scripts Python affichant des caractères UTF-8 (✓, é, à) plantent sur Windows avec `'charmap' codec can't encode character`.

**Solution implémentée**: [comparer_documents.py:48-50](../execution/comparer_documents.py#L48-L50)
```python
# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

**Leçon**: Toujours ajouter ce fix au début de chaque script Python qui affiche du texte non-ASCII.

---

## 4. Deep Copy vs Shallow Copy

### Problème: Modifications involontaires des données imbriquées

**Constat**: Utiliser `donnees.copy()` crée un shallow copy qui ne copie que le premier niveau. Les dictionnaires imbriqués sont toujours des références.

**Solution implémentée**: [assembler_acte.py:35+369](../execution/assembler_acte.py#L35)
```python
from copy import deepcopy
...
donnees_enrichies = deepcopy(donnees)
```

**Leçon**: **TOUJOURS** utiliser `deepcopy()` quand on manipule des dictionnaires imbriqués.

---

## 5. Filtres Jinja2 Manquants

### Problème: Templates utilisent des filtres non définis

**Constat**: Le template `promesse_vente` utilise `mois_en_lettres` et `jour_en_lettres` qui n'existaient pas dans `assembler_acte.py`.

**Solution implémentée**: [assembler_acte.py:233-262](../execution/assembler_acte.py#L233-L262)
```python
def mois_en_lettres(mois: int) -> str:
    mois_noms = ['', 'janvier', 'février', ...]
    return mois_noms[mois] if 1 <= mois <= 12 else str(mois)

def jour_en_lettres(jour: int) -> str:
    return 'premier' if jour == 1 else nombre_en_lettres(jour)
```

**Leçon**: Créer une bibliothèque complète de filtres Jinja2 dès le début. Documenter les filtres disponibles dans `CLAUDE.md`.

---

## 6. Champs Obligatoires des Templates

### Problème: Templates attendent des champs non générés

**Constat**: Le template `vente_lots_copropriete.md` attend de nombreux champs:
- `quotites_vendues` / `quotites_acquises` (CRITIQUE)
- `bien.superficie_carrez` (global)
- `lot.tantiemes` (structure complexe)
- `copropriete.syndic`, `copropriete.reglement`
- `defunt_conjoint` pour statut="veuf"
- `ex_conjoint` pour statut="divorce"

**Solution implémentée**: Enrichir `generer_donnees_test.py` pour tous les cas:
- [Quotités](../execution/generer_donnees_test.py#L820-L856)
- [Surface Carrez globale](../execution/generer_donnees_test.py#L840-L845)
- [Tantièmes structurés](../execution/generer_donnees_test.py#L295-L300)
- [Copropriété](../execution/generer_donnees_test.py#L931-L947)
- [Situations matrimoniales complètes](../execution/generer_donnees_test.py#L137-L156)

**Leçon**:
1. **Toujours** analyser le template AVANT de générer des données
2. Utiliser `extraire_bookmarks_contenu.py` pour identifier toutes les variables
3. Créer un schéma JSON complet AVANT d'écrire le générateur

---

## 7. Types de Personnes dans Templates

### Problème: Template assume personnes physiques uniquement

**Constat**: Le template `vente_lots_copropriete.md` (lignes 76-103) accède directement à `acquereur.situation_matrimoniale` sans vérifier si c'est une personne morale.

**Solution temporaire**: Forcer uniquement personnes physiques dans `generer_donnees_vente()`:
```python
# Acquéreurs (TOUJOURS personnes physiques pour compatibilité template)
acquereur = {"type": "personne_physique"}
```

**Solution long terme**: Améliorer le template pour gérer les deux cas:
```jinja2
{% if acquereur.type == "personne_physique" %}
    {{ acquereur.situation_matrimoniale.statut }}
{% else %}
    Société {{ acquereur.forme_juridique }}
{% endif %}
```

**Leçon**: Les templates doivent être **défensifs** et gérer tous les cas possibles.

---

## 8. Compatibilité Générateur ⟷ Template

### Problème: Le générateur et le template évoluent indépendamment

**Constat**: Difficile de savoir quels champs sont réellement utilisés par chaque template.

**Solution recommandée**: Créer des **schémas de validation** pour chaque type d'acte:
```json
{
  "vente_lots_copropriete": {
    "required": ["acte", "vendeurs", "acquereurs", "quotites_vendues", "quotites_acquises", "bien", "prix", "copropriete"],
    "optional": ["financement", "diagnostics", "meubles", "annexes"]
  }
}
```

**Leçon**: Valider les données **AVANT** l'assemblage avec `valider_acte.py`.

---

## 9. Conformité des Documents Générés

### Résultats Tests

| Template | Conformité | Statut | Raison |
|----------|-----------|--------|--------|
| `reglement_copropriete_edd.md` | **85.5%** | ✅ CONFORME | Template complet et fidèle |
| `modificatif_edd.md` | **91.7%** | ✅ CONFORME | Template le plus abouti |
| `vente_lots_copropriete.md` | **46.0%** | ❌ Incomplet | Manque 97 titres, 2 tableaux |
| `promesse_vente_lots_copropriete.md` | **60.9%** | ❌ Incomplet | Manque 24 titres |

**Leçon**:
- Un template "squelette" ne suffit pas
- **Objectif**: ≥80% de conformité pour production
- Les templates `reglement` et `modificatif` sont des **références** à suivre

---

## 10. Workflow de Création de Template

### Process recommandé

1. **Analyser le document original DOCX**
   ```bash
   python execution/extraire_bookmarks_contenu.py \
       --input docs_original/nouveau_template.docx \
       --output schemas/variables_nouveau.json
   ```

2. **Créer le schéma de questions**
   - Lire `schemas/variables_nouveau.json`
   - Créer `schemas/questions_nouveau.json`
   - S'inspirer de `questions_notaire.json` (100+ questions)

3. **Créer le template Markdown avec Jinja2**
   - Copier la structure du DOCX original
   - Remplacer les zones variables par `{{ variable }}`
   - Ajouter conditions `{% if %}` et boucles `{% for %}`

4. **Créer le générateur de données test**
   - Fonction `generer_donnees_nouveau()` dans `generer_donnees_test.py`
   - Générer **TOUS** les champs requis (voir leçon #6)
   - Utiliser `normaliser_situation_matrimoniale()` si applicable

5. **Tester le pipeline complet**
   ```bash
   python execution/generer_donnees_test.py --type nouveau --output .tmp/test.json
   python execution/assembler_acte.py -t nouveau.md -d .tmp/test.json -o .tmp/out
   python execution/exporter_docx.py --input .tmp/out/*/acte.md --output test.docx
   python execution/comparer_documents.py --original docs_original/nouveau.docx --genere test.docx
   ```

6. **Itérer jusqu'à ≥80% conformité**

**Leçon**: Le process est **itératif**. Ne pas chercher la perfection du premier coup.

---

## 11. Organisation du Code

### Structure actuelle

```
execution/
├── assembler_acte.py           # Orchestration Jinja2
├── exporter_docx.py            # Markdown → DOCX
├── generer_donnees_test.py     # Données aléatoires
├── valider_acte.py             # Validation pré-génération
├── comparer_documents.py       # Validation post-génération
├── detecter_type_acte.py       # Auto-détection type
├── suggerer_clauses.py         # Intelligence clauses
└── collecter_informations.py   # CLI interactive
```

**Leçon**: Chaque script a UNE responsabilité. Pas de monolithe.

---

## 12. Gestion des Erreurs

### Stratégie actuelle

```python
try:
    acte = assembleur.assembler(nom_template, donnees)
except FileNotFoundError as e:
    print(f"[ERREUR] Template: {e}")
    return 1
except ValueError as e:
    print(f"[ERREUR] Donnees: {e}")
    return 1
```

**Améliorations possibles**:
1. Logger les erreurs dans un fichier `.tmp/errors.log`
2. Retourner des codes d'erreur structurés (JSON)
3. Implémenter un mode `--debug` avec traceback complet

**Leçon**: Les messages d'erreur doivent être **actionnables**.

---

## 13. Performance

### Observations

- Génération données: ~100ms
- Assemblage template: ~200ms
- Export DOCX: ~500ms
- Comparaison: ~1.5s

**Total pipeline**: ~2.3s pour un acte

**Optimisations possibles**:
- Cache Jinja2 des templates compilés
- Paralléliser export DOCX + comparaison
- Utiliser `multiprocessing` pour batch

**Leçon**: La performance actuelle est acceptable. Optimiser seulement si besoin.

---

## 14. Tests Automatisés

### Coverage actuel

- ✅ Unit tests: `test_assembler_acte.py` (filtres Jinja2)
- ✅ Integration tests: `test_integration.py` (pipeline complet)
- ❌ Tests de régression: manquants
- ❌ Tests de conformité automatiques: manquants

**Recommandation**: Ajouter pytest-cov pour mesurer coverage.

**Leçon**: Les tests sont cruciaux pour éviter les régressions lors des améliorations.

---

## 15. Documentation

### État actuel

| Document | Statut | Complétude |
|----------|--------|------------|
| `CLAUDE.md` | ✅ Complet | Architecture 3 layers bien documentée |
| `directives/creer_acte.md` | ✅ Complet | Process création acte de vente |
| `directives/creer_promesse_vente.md` | ✅ Complet | Promesse unilatérale |
| `directives/creer_reglement_copropriete.md` | ✅ Complet | EDD et RC |
| `directives/creer_modificatif_edd.md` | ✅ Complet | Modificatif |
| `directives/modifier_acte.md` | ✅ Complet | Modification acte existant |
| `directives/lecons_apprises.md` | ⭐ **CE FICHIER** | Bonnes pratiques |
| `README.md` | ❌ Manquant | À créer |

**Leçon**: La documentation est aussi importante que le code.

---

## Résumé des Principes

### ✅ DO

1. **Normaliser les données** dans `enrichir_donnees()` (layer orchestration)
2. **Utiliser deepcopy()** pour dictionnaires imbriqués
3. **Valider AVANT assemblage** avec `valider_acte.py`
4. **Fixer l'encodage UTF-8** sur Windows dès le début
5. **Créer des alias** de compatibilité (ex: conjoint = partenaire)
6. **Documenter les filtres Jinja2** disponibles
7. **Analyser le template** AVANT de générer des données
8. **Viser ≥80% conformité** pour la production
9. **Tester le pipeline complet** après chaque modification
10. **Enrichir les catalogues** (clauses, annexes) à chaque nouveau cas

### ❌ DON'T

1. Ne PAS modifier les templates pour s'adapter aux données
2. Ne PAS utiliser `copy()` pour dictionnaires imbriqués
3. Ne PAS oublier les champs obligatoires (quotités, copropriété, etc.)
4. Ne PAS créer de monolithe - un script = une responsabilité
5. Ne PAS commit `.tmp/` dans git
6. Ne PAS modifier `docs_original/` (référence absolue)
7. Ne PAS générer personnes morales si template ne les gère pas
8. Ne PAS ignorer les warnings de conformité <80%

---

## Checklist Ajout Nouveau Type d'Acte

- [ ] Analyser DOCX original avec `extraire_bookmarks_contenu.py`
- [ ] Créer `schemas/questions_nouveau.json` (toutes les questions)
- [ ] Créer `schemas/variables_nouveau.json` (structure données)
- [ ] Créer `templates/nouveau.md` (Jinja2 + Markdown)
- [ ] Créer `generer_donnees_nouveau()` dans `generer_donnees_test.py`
- [ ] Créer `directives/creer_nouveau.md` (SOP)
- [ ] Tester pipeline complet (generate → assemble → export → compare)
- [ ] Valider conformité ≥80%
- [ ] Enrichir `schemas/clauses_catalogue.json` si nécessaire
- [ ] Enrichir `schemas/annexes_catalogue.json` si nécessaire
- [ ] Mettre à jour `CLAUDE.md`
- [ ] Créer exemples dans `exemples/donnees_nouveau_exemple.json`

---

**Dernière mise à jour**: 2026-01-20
**Auteur**: Claude Sonnet 4.5 (NotaireAI Agent)
