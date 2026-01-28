# Directive : Mise à Jour Automatique des Statuts après Donation-Partage

## Objectif

Automatiser la mise à jour des statuts d'une société civile après une donation-partage de parts sociales, en conservant la présentation d'origine des statuts.

## Problématique Notariale

Lorsqu'une donation-partage porte sur des parts sociales, certains articles des statuts doivent être modifiés :

- **Article 7 (CAPITAL SOCIAL)** : Nouvelle répartition des parts entre associés
- **Article 11 (DROIT DE VOTE)** : Règles en cas de démembrement (usufruit/nue-propriété)
- **Article 21 (AFFECTATION DES RÉSULTATS)** : Attribution des bénéfices en cas de démembrement

Aujourd'hui, cette mise à jour repose sur du **copier-coller manuel** depuis l'acte vers les statuts, ce qui est :
- ❌ Chronophage (30-45 minutes par dossier)
- ❌ Source d'erreurs (oubli, mauvais article, formatage cassé)
- ❌ Sans valeur ajoutée (tâche répétitive)

## Solution Automatisée

Le script `execution/mettre_a_jour_statuts.py` :
1. **Lit l'acte de donation-partage** (DOCX généré)
2. **Détecte automatiquement** les articles modifiés (surlignés ou marqués)
3. **Extrait le nouveau texte** pour chaque article
4. **Localise les articles** dans les statuts originaux
5. **Remplace le contenu** en conservant le formatage d'origine
6. **Génère les statuts mis à jour** prêts pour dépôt INPI

## Inputs

### Documents requis

| Document | Format | Source |
|----------|--------|--------|
| **Acte de donation-partage** | DOCX | Généré par `execution/assembler_acte.py` |
| **Statuts originaux** | DOCX | Déposés lors de la constitution |

### Informations dans l'acte

L'acte doit contenir les sections suivantes (déjà présentes dans `templates/donation_partage.md`) :

#### 1. Tableau de répartition du capital (Article 7)

```markdown
Par suite des faits et actes suivants, le capital social est dorénavant réparti de la manière suivante savoir :

| Associé | Pleine propriété | Nue-propriété | Usufruit |
|---------|------------------|---------------|----------|
| à M. Antoine AUVRAY | - | 250 parts | - |
| à Mme Camille AUVRAY | - | 250 parts | - |
| à M. Dominique AUVRAY | 500 parts | - | 250 parts |
| à Mme Viviane ROBIN | - | - | 250 parts |

Total égal au nombre de parts composant le capital social : 1000 parts sociales
```

#### 2. Modification Article 11 (Droit de vote)

```markdown
### Modification Article 11 - DROIT DE VOTE

Les parties déclarent vouloir modifier à titre de condition des présentes cet article 11 de la façon suivante :

« Démembrement

Le nu-propriétaire et l'usufruitier ont la qualité d'associé et, à ce titre, le droit de participer aux décisions collectives.

**Le droit de vote appartient à l'usufruitier pour toutes les décisions collectives ordinaires et extraordinaires.** »
```

#### 3. Modification Article 21 (Affectation résultats)

```markdown
### Modification Article 21 - AFFECTATION ET REPARTITION DES RESULTATS

Les associés décident de compléter l'article 21 des statuts de la manière suivante :

« Attribution du résultat courant à l'usufruitier et le résultat exceptionnel au nu-propriétaire sous réserve de quasi-usufruit

Le bénéfice social et le report à nouveau bénéficiaire provenant d'un résultat courant, s'ils sont mis en distribution reviennent en pleine propriété à l'usufruitier des parts.

... »
```

## Scripts et Outils

### Script principal

```bash
python execution/mettre_a_jour_statuts.py \
    --acte outputs/donation_partage_client.docx \
    --statuts docs_original/Statuts_SOCIETE.docx \
    --output outputs/Statuts_SOCIETE_modifies.docx
```

### Workflow complet (donation → statuts)

```bash
# Étape 1: Générer l'acte de donation-partage
python execution/assembler_acte.py \
    --template donation_partage.md \
    --donnees .tmp/dossiers/client_X/donnees.json \
    --output .tmp/actes_generes/

# Étape 2: Exporter en DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/donation_partage_client.docx

# Étape 3: Mettre à jour les statuts
python execution/mettre_a_jour_statuts.py \
    --acte outputs/donation_partage_client.docx \
    --statuts docs_original/Statuts_BLOUGE.docx \
    --output outputs/Statuts_BLOUGE_modifies.docx

# Étape 4: Valider les statuts modifiés
# (ouverture manuelle dans Word pour vérification)
```

## Fonctionnement Technique

### 1. Extraction des modifications

Le script analyse l'acte paragraphe par paragraphe et utilise des **expressions régulières** pour identifier :

- **Section "Modification Article 7"** → Extrait le tableau de répartition
- **Section "Modification Article 11"** → Extrait le nouveau texte du démembrement
- **Section "Modification Article 21"** → Extrait le nouveau texte de l'affectation

Exemple de regex pour Article 11 :
```python
pattern = r"Article\s+11.*?Démembrement.*?(?=Article\s+\d+|En conséquence|$)"
match = re.search(pattern, texte_complet, re.DOTALL | re.IGNORECASE)
```

### 2. Localisation dans les statuts

Le script parcourt les statuts et trouve chaque article par son numéro :

```python
def trouver_article_dans_statuts(doc_statuts: Document, numero_article: int) -> Optional[Tuple[int, int]]:
    """
    Trouve les indices de début et fin d'un article dans les statuts.
    Returns: Tuple (index_debut, index_fin) ou None si non trouvé
    """
    pattern_debut = re.compile(rf"Article\s+{numero_article}\s*[-–:]\s*", re.IGNORECASE)
    # ... recherche du début et de la fin
    return (index_debut, index_fin)
```

### 3. Remplacement du contenu

Le script **conserve le titre de l'article** et remplace uniquement le contenu :

```python
def remplacer_contenu_article(doc_statuts: Document, numero_article: int, nouveau_texte: str) -> bool:
    # 1. Localiser l'article
    indices = trouver_article_dans_statuts(doc_statuts, numero_article)

    # 2. Supprimer les paragraphes existants (sauf le titre)
    for i in range(index_fin - 1, index_debut, -1):
        p._element.getparent().remove(p._element)

    # 3. Insérer le nouveau contenu avec le même formatage
    for ligne in lignes:
        new_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        new_para.paragraph_format.first_line_indent = Mm(12.51)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
```

## Outputs

### Fichier généré

| Fichier | Description |
|---------|-------------|
| `Statuts_SOCIETE_modifies.docx` | Statuts mis à jour, prêts pour dépôt INPI |

### Contenu attendu

Les statuts modifiés contiennent :

✅ **Formatage original préservé** (police, marges, alignement)
✅ **Article 7** : Nouvelle répartition du capital
✅ **Article 11** : Nouvelles règles de droit de vote (démembrement)
✅ **Article 21** : Nouvelles règles d'affectation des résultats (démembrement)
✅ **Tous les autres articles inchangés**

## Edge Cases

### 1. Articles non trouvés dans les statuts

**Problème** : Les statuts n'ont pas d'Article 11 ou 21 (société sans démembrement prévu)

**Solution** : Le script affiche un warning et continue
```
[WARN] Article 11 non trouvé dans les statuts
```

**Action notaire** : Ajouter manuellement les articles manquants

### 2. Format de l'acte différent

**Problème** : L'acte ne contient pas les marqueurs "Modification Article 11" (acte externe, autre template)

**Solution** : Utiliser le mode manuel avec `--articles` pour spécifier les sections :
```bash
python execution/mettre_a_jour_statuts.py \
    --acte outputs/donation_partage.docx \
    --statuts docs_original/Statuts.docx \
    --output outputs/Statuts_modifies.docx \
    --article-11-debut "Ligne 456" \
    --article-11-fin "Ligne 489"
```

### 3. Numérotation différente des articles

**Problème** : Dans certaines sociétés, l'article "Droit de vote" est l'article 12 au lieu de 11

**Solution** : Paramétrer via `--mapping-articles` :
```bash
python execution/mettre_a_jour_statuts.py \
    ... \
    --mapping-articles "droit_vote:12,affectation:22"
```

### 4. Statuts en PDF uniquement

**Problème** : Les statuts originaux ne sont disponibles qu'en PDF

**Solution** : Convertir d'abord en DOCX avec `pdf2docx` :
```bash
pip install pdf2docx
python execution/convertir_pdf_vers_docx.py \
    --input docs_original/Statuts.pdf \
    --output docs_original/Statuts.docx
```

## Validation

### Checklist après génération

- [ ] **Ouvrir le fichier** `Statuts_SOCIETE_modifies.docx` dans Word
- [ ] **Vérifier Article 7** : Répartition correcte des parts (total = capital)
- [ ] **Vérifier Article 11** : Texte du démembrement (droit de vote à l'usufruitier)
- [ ] **Vérifier Article 21** : Texte de l'affectation (résultat courant/exceptionnel)
- [ ] **Vérifier formatage** : Police Times 11pt, retraits 12.51mm
- [ ] **Vérifier numérotation** : Articles suivants non décalés
- [ ] **Lire en entier** : Aucune erreur de copier-coller (phrases coupées)

### Test de cohérence

```bash
# Comparer les statuts avant/après
python execution/comparer_statuts.py \
    --original docs_original/Statuts_BLOUGE.docx \
    --modifie outputs/Statuts_BLOUGE_modifies.docx \
    --articles-modifies "7,11,21"
```

**Résultat attendu** :
```
[OK] Articles 7, 11, 21 modifiés comme prévu
[OK] 45 autres articles inchangés
[OK] Formatage préservé (100% de conformité)
```

## Améliorations Futures

### Version 1.1 (prochaine)

- [ ] **Détection automatique** des articles à modifier depuis l'acte (sans spécifier --articles)
- [ ] **Support PDF** natif (sans conversion préalable)
- [ ] **Génération du PV d'AG** approuvant les modifications
- [ ] **Export multi-formats** (DOCX + PDF + XML INPI)

### Version 2.0 (long terme)

- [ ] **IA de validation** : Détection automatique des incohérences (ex: total parts ≠ capital)
- [ ] **Historique des versions** : Suivi des modifications successives des statuts
- [ ] **Intégration INPI** : Dépôt automatique des statuts modifiés
- [ ] **Support multi-sociétés** : Traiter plusieurs sociétés dans le même acte

## Ressources

### Fichiers système

| Type | Chemin | Description |
|------|--------|-------------|
| **Script** | `execution/mettre_a_jour_statuts.py` | Script principal de mise à jour |
| **Directive** | `directives/mise_a_jour_statuts_donation.md` | Ce fichier |
| **Template** | `templates/donation_partage.md` | Template de l'acte (contient les modifications) |
| **Exemple** | `exemples/donnees_donation_partage_exemple.json` | Données d'exemple avec société |

### Documentation juridique

- **Articles du Code civil** : Art. 1844 (démembrement), Art. 1832-1873 (sociétés civiles)
- **Articles du Code de commerce** : Art. L123-8 (dépôt des actes), Art. R123-54 (INPI)
- **Loi n°2023-171** du 9 mars 2023 : Simplification des formalités INPI

### Liens utiles

- **INPI - Guichet unique** : https://procedures.inpi.fr
- **Documentation python-docx** : https://python-docx.readthedocs.io
- **Regex101** (tester les expressions régulières) : https://regex101.com

## Exemple Complet

### Contexte

Famille AUVRAY, société BLOUGE :
- **Avant donation** : M. et Mme AUVRAY détiennent 1000 parts (500 chacun)
- **Après donation** : Transmission de la nue-propriété aux 2 enfants (250 parts chacun), les parents conservent l'usufruit

### Commandes

```bash
# Générer l'acte de donation-partage
python execution/assembler_acte.py \
    --template donation_partage.md \
    --donnees exemples/donnees_donation_partage_exemple.json \
    --output .tmp/actes_generes/

python execution/exporter_docx.py \
    --input .tmp/actes_generes/dp_20250120_143022/acte.md \
    --output outputs/donation_partage_auvray.docx

# Mettre à jour les statuts
python execution/mettre_a_jour_statuts.py \
    --acte outputs/donation_partage_auvray.docx \
    --statuts docs_original/Statuts_BLOUGE.docx \
    --output outputs/Statuts_BLOUGE_2025.docx
```

### Résultat

```
[INFO] Lecture de l'acte: outputs/donation_partage_auvray.docx
[INFO] Lecture des statuts: docs_original/Statuts_BLOUGE.docx
[INFO] Extraction des modifications depuis l'acte...
[INFO] Modification Article 7 - CAPITAL SOCIAL
       Nouvelle répartition : 1000 parts entre 4 associés
[INFO] Modification Article 11 - DROIT DE VOTE
       Nouveau texte démembrement extrait (452 caractères)
[INFO] Modification Article 21 - AFFECTATION ET REPARTITION DES RESULTATS
       Nouveau texte démembrement extrait (1204 caractères)
[INFO] Sauvegarde des statuts modifiés: outputs/Statuts_BLOUGE_2025.docx
[OK] 3 modification(s) appliquée(s) avec succès

[OK] Statuts modifiés générés: outputs/Statuts_BLOUGE_2025.docx (45.3 Ko)
```

### Fichier généré

Le fichier `Statuts_BLOUGE_2025.docx` contient :

**Article 7 - CAPITAL SOCIAL** (modifié)
```
Le capital social est fixé à la somme de 1 000,00 euros.

Il est divisé en 1000 parts sociales...

Ces 1000 parts sociales sont réparties entre les associés dans les proportions suivantes :

- M. Dominique AUVRAY : 500 parts en pleine propriété (50%)
- M. Antoine AUVRAY : 250 parts en nue-propriété (25%)
- Mme Camille AUVRAY : 250 parts en nue-propriété (25%)

Usufruit :
- M. Dominique AUVRAY : 250 parts (25%)
- Mme Viviane ROBIN : 250 parts (25%)

Total : 1000 parts
```

**Article 11 - DROIT DE VOTE** (modifié)
```
Démembrement

Le nu-propriétaire et l'usufruitier ont la qualité d'associé et, à ce titre, le droit de participer aux décisions collectives.

Le droit de vote appartient à l'usufruitier pour toutes les décisions collectives ordinaires et extraordinaires.
```

**Article 21 - AFFECTATION ET REPARTITION DES RESULTATS** (modifié)
```
Attribution du résultat courant à l'usufruitier et le résultat exceptionnel au nu-propriétaire sous réserve de quasi-usufruit

Le bénéfice social et le report à nouveau bénéficiaire provenant d'un résultat courant, s'ils sont mis en distribution reviennent en pleine propriété à l'usufruitier des parts.

...
```

**Tous les autres articles** : Inchangés

---

**Version** : 1.0.0
**Date création** : 2026-01-21
**Auteur** : NotaireAI
**Statut** : ✅ Directive production-ready
