# Directive : Formatage DOCX des Actes Notariaux

## Objectif

Garantir que tous les actes générés en format DOCX soient **100% fidèles** à la trame originale `docs_originels/Trame vente lots de copropriété.docx`. Cette directive documente les spécifications exactes extraites de l'analyse du document original.

## IMPORTANT

**Ces valeurs ne doivent JAMAIS être modifiées** sans analyse préalable d'un nouveau document original. Elles garantissent la conformité aux standards notariaux français.

---

## Spécifications de mise en page

### Format de page
- **Format**: A4 (210mm x 297mm)
- **Orientation**: Portrait

### Marges

| Position | Valeur | Code python-docx |
|----------|--------|------------------|
| Gauche | 60mm (6.0cm) | `Mm(60)` |
| Droite | 15mm (1.5cm) | `Mm(15)` |
| Haut | 25mm (2.5cm) | `Mm(25)` |
| Bas | 25mm (2.5cm) | `Mm(25)` |
| Reliure (gutter) | 0mm | `Mm(0)` |
| Marges miroir | **NON** | - |

### En-tête et pied de page
- **Distance en-tête**: 12.7mm (1.27cm)
- **Distance pied de page**: 12.7mm (1.27cm)
- **En-tête différent sur première page**: OUI

---

## Spécifications typographiques

### Police principale
- **Famille**: Times New Roman
- **Taille**: 11pt
- **Appliquée à**: Tous les éléments (titres, paragraphes, tableaux)

### Interligne
- **Type**: Simple (`WD_LINE_SPACING.SINGLE`)

### Retrait de première ligne
- **Valeur**: 12.51mm (1.251cm)
- **Appliqué à**: Tous les paragraphes de style Normal
- **NON appliqué à**: Titres, listes, tableaux

---

## Styles de titres

### Heading 1 (Titres principaux)

**Utilisé pour**: PARTIE NORMALISÉE, PARTIE DÉVELOPPÉE, IDENTIFICATION DES PARTIES, DÉSIGNATION, etc.

| Propriété | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Gras | OUI |
| Majuscules | ALL CAPS |
| Souligné | OUI |
| Alignement | Centré |
| Espace avant | 0pt |
| Espace après | 12pt |
| Retrait première ligne | 0 |
| Garder avec suivant | OUI |

**Titres reconnus automatiquement:**
- PARTIE NORMALISÉE / PARTIE NORMALISEE
- PARTIE DÉVELOPPÉE / PARTIE DEVELOPPEE
- IDENTIFICATION DES PARTIES
- DÉSIGNATION / DESIGNATION
- ORIGINE DE PROPRIÉTÉ
- CHARGES ET CONDITIONS
- PRIX ET PAIEMENT
- GARANTIES
- TERMINOLOGIE
- CECI EXPOSÉ
- NATURE ET QUOTITÉ
- FIN DE PARTIE
- FIXATION DE LA PROPORTION

### Heading 2 (Sous-sections)

**Utilisé pour**: VENDEUR, ACQUÉREUR, QUOTITÉS, FINANCEMENT, etc.

| Propriété | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Gras | OUI |
| Petites majuscules | OUI |
| Souligné | OUI |
| Alignement | Centré |
| Espace avant | 0pt |
| Espace après | 12pt |
| Retrait première ligne | 0 |

**Sous-titres reconnus automatiquement:**
- VENDEUR
- ACQUÉREUR / ACQUEREUR
- QUOTITÉS / QUOTITES
- PRÉSENCE / PRESENCE
- REPRÉSENTATION / REPRESENTATION
- DÉCLARATIONS / DECLARATIONS
- DOCUMENTS RELATIFS
- DONT QUITTANCE
- FINANCEMENT
- TOTAL
- CONCERNANT

### Heading 3 (Sous-sous-sections)

| Propriété | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Gras | OUI |
| Souligné | OUI |
| Alignement | Centré |
| Espace avant | 0pt |
| Espace après | 12pt |

### Heading 4 (Petits titres)

| Propriété | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Gras | OUI |
| Souligné | NON |
| Italique | NON |
| Alignement | Justifié |
| Espace avant | 6pt |
| Espace après | 0pt |

---

## Paragraphes normaux

| Propriété | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Alignement | Justifié |
| Interligne | Simple |
| Espace avant | 0pt |
| Espace après | 0pt |
| Retrait première ligne | 12.51mm |

---

## Listes à puces

| Propriété | Valeur |
|-----------|--------|
| Caractère de puce | Tiret (-) |
| Retrait gauche | 6mm |
| Retrait première ligne | -3mm (négatif) |
| Espace après | 2pt |
| Alignement | Justifié |

---

## Tableaux

### Style général
- **Style Word**: Table Grid
- **Alignement**: Centré dans la page
- **Bordures**: Simples, noires, 8pt

### Bordures XML
```xml
<w:tblBorders>
  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>
  <w:left w:val="single" w:sz="8" w:space="0" w:color="000000"/>
  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>
  <w:right w:val="single" w:sz="8" w:space="0" w:color="000000"/>
  <w:insideH w:val="single" w:sz="8" w:space="0" w:color="000000"/>
  <w:insideV w:val="single" w:sz="8" w:space="0" w:color="000000"/>
</w:tblBorders>
```

### En-têtes de tableau
- **Gras**: OUI
- **Alignement**: Selon le type de données

### Types de tableaux reconnus automatiquement

Le script `exporter_docx.py` détecte automatiquement 20 catégories de tableaux notariaux:

1. **Désignation cadastrale**: Section, N°, Lieudit, Surface
2. **Répartition des charges**: Type, Montant, Quote-part
3. **État hypothécaire**: Créancier, Montant, Date
4. **Frais d'acte / émoluments**: Nature, Base, Taux, Montant
5. **Répartition du prix**: Désignation, Prix
6. **Impôts fonciers / taxes**: Taxe, Base, Taux, Montant
7. **Diagnostics immobiliers**: Type, Date, Validité
8. **Servitudes**: Nature, Bénéficiaire
9. **Assurances**: Compagnie, N° Police, Échéance
10. **Financement / prêts**: Prêteur, Montant, Taux, Durée
11. **Tableaux récapitulatifs**: Poste, Montant
12. **Droits fiscaux**: Droit, Base, Taux, Montant
13. **Lots de copropriété**: N° lot, Désignation, Tantièmes
14. **Urbanisme**: Document, Date, Zone
15. **Parties / intervenants**: Qualité, Nom, Adresse
16. **Origine de propriété**: Nature acte, Date, Notaire
17. **Mobilier**: Désignation, Quantité, Valeur
18. **Provisions / régularisations**: Poste, Provision, Réel
19. **Séquestre / consignation**: Motif, Montant, Bénéficiaire
20. **Bornage**: Point, Coordonnées, Nature

---

## Pagination

### Numéro de page
- **Position**: En-tête, aligné à droite
- **Police**: Times New Roman 9pt
- **Format**: Numéro seul (sans "Page X sur Y")
- **Champ Word**: `PAGE`

---

## Formatage Markdown supporté

### Gras
```markdown
**texte en gras**
```

### Italique
```markdown
*texte en italique*
```

### Souligné
```markdown
__texte souligné__
```

### Gras + Italique
```markdown
***texte gras et italique***
```

### Titres Markdown
```markdown
# Titre niveau 1 → Heading 1
## Titre niveau 2 → Heading 2
### Titre niveau 3 → Heading 3
```

### Tableaux Markdown
```markdown
| Col1 | Col2 | Col3 |
|------|------|------|
| val1 | val2 | val3 |
```

---

## HTML supporté

### Blocs personnalisés
```html
<div class="header-ref">Référence de l'acte</div>
<div class="header-titre">Titre de l'acte</div>
<div class="header-notaire">Informations notaire</div>
<div class="personne">Bloc d'identification de personne</div>
```

### Retour à la ligne
```html
<br>
```

### Formatage inline
```html
<strong>gras</strong>
<em>italique</em>
```

**Note**: Les balises `<u>` sont ignorées. Utiliser `__texte__` pour le soulignement.

---

## Compatibilité Word

Le script applique des options de compatibilité pour améliorer la justification:
- `w:doNotExpandShiftReturn` - Ne pas étendre les espaces sur lignes courtes

---

## Script d'export

**Fichier**: `execution/exporter_docx.py`

**Usage**:
```bash
python execution/exporter_docx.py --input <acte.md> --output <acte.docx>
```

**Arguments**:
- `--input`, `-i`: Fichier Markdown source (requis)
- `--output`, `-o`: Fichier DOCX de sortie (requis)

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création - Spécifications extraites de l'analyse du DOCX original | Agent |

---

## Voir aussi

- [directives/creer_acte.md](creer_acte.md) - Flux complet de création d'acte
- [execution/exporter_docx.py](../execution/exporter_docx.py) - Script d'export
- [docs_originels/Trame vente lots de copropriété.docx](../docs_originels/Trame%20vente%20lots%20de%20copropriété.docx) - Document original de référence
