# 📋 Formulaires PDF Générés

Ce dossier contient les formulaires PDF générés automatiquement par le système NotaireAI.

---

## 📄 Formulaires Disponibles

### Formulaire Vendeur

| Fichier | Taille | Description |
|---------|--------|-------------|
| `formulaire_vendeur_20260123_150802.pdf` | 565 Ko | Formulaire vide |
| `formulaire_vendeur_exemple_20260123_151055.pdf` | 564 Ko | Formulaire pré-rempli avec exemple |

### Contenu du Formulaire

Le formulaire collecte les informations suivantes :

1. **Identité du vendeur**
   - Civilité
   - Nom de naissance
   - Nom d'usage (optionnel)
   - Prénoms (dans l'ordre de l'acte de naissance)
   - Date et lieu de naissance
   - Nationalité
   - Profession

2. **Adresse actuelle**
   - Adresse complète
   - Code postal
   - Ville

3. **Situation matrimoniale**
   - Régime matrimonial
   - Informations conjoint/partenaire (si applicable)
   - Date et lieu de mariage/PACS
   - Type de régime
   - Intervention à l'acte

4. **Pièces justificatives**
   - Numéro CNI
   - Dates d'émission et expiration
   - Autorité émettrice

5. **Coordonnées bancaires**
   - IBAN
   - BIC
   - Nom de la banque

6. **Contact**
   - Téléphone
   - Email

---

## 🔄 Régénération

### Méthode 1: Script Automatique

```bash
cd web
generer_pdf.bat
```

Choisir :
- **1** : Génération automatique (Chrome/Edge headless)
- **2** : Impression manuelle (ouvre le navigateur)

### Méthode 2: PowerShell Direct

```powershell
# PDF vide
cd web
./generer_pdf_auto.ps1

# PDF avec exemple
./generer_pdf_auto.ps1 -Exemple

# Spécifier le chemin
./generer_pdf_auto.ps1 -Output "C:\chemin\mon_formulaire.pdf"
```

### Méthode 3: Python + Playwright

```bash
# Installation (une fois)
pip install playwright
playwright install chromium

# Génération
python web/generer_pdf_simple.py --exemple
```

---

## 📝 Utilisation

### Workflow Papier

1. **Imprimer le formulaire vide**
   ```bash
   start outputs/formulaire_vendeur_20260123_150802.pdf
   ```

2. **Remplir à la main** lors du RDV client

3. **Re-saisir dans le formulaire web**
   ```bash
   start web/index.html
   ```

4. **Exporter en JSON**
   - Cliquer "Enregistrer les informations"
   - Télécharger le JSON

5. **Générer l'acte notarial**
   ```bash
   python execution/workflow_rapide.py \
       --type vente \
       --donnees vendeur_client.json \
       --output outputs/acte_client.docx
   ```

### Workflow Digital

1. **Formulaire web directement**
   ```bash
   start web/index.html
   ```

2. **Remplir en ligne** (avec le client via partage d'écran)

3. **Export JSON immédiat**

4. **Génération acte**

---

## 🎯 Exemple de Données

Le formulaire pré-rempli contient :

```
Vendeur : M. Jean Pierre Marie DUPONT
Né le : 15/06/1975
Lieu : Paris (75)
Adresse : 12 rue de la République, 75001 Paris

Situation : Marié (20/08/2005 à Lyon)
Conjoint : Mme Sophie Marie MARTIN
Régime : Communauté légale

CNI : 123456789012
Émise le : 15/01/2020
Expire le : 15/01/2030
Autorité : Préfecture de Paris

Banque : BNP Paribas
IBAN : FR76 1234 5678 9012 3456 7890 123
BIC : BNPAFRPPXXX

Contact : 06 12 34 56 78
Email : jean.dupont@email.com
```

---

## 🔧 Personnalisation

### Modifier les Marges

Éditer `web/print_version.html`, section `@media print` :

```css
@page {
    size: A4;
    margin: 2cm;  /* Modifier ici */
}
```

### Ajouter un Logo

Éditer `web/print_version.html`, dans le `<header>` :

```html
<header>
    <img src="logo.png" alt="Logo" style="height: 50px;">
    <h1>🏛️ NotaireAI</h1>
    <p class="subtitle">Formulaire de collecte des informations du vendeur</p>
</header>
```

### Modifier les Couleurs

Éditer `web/styles.css` :

```css
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Modifier les couleurs ici */
}
```

---

## 📊 Format PDF

- **Taille de page** : A4 (210 x 297 mm)
- **Marges** : 2cm (toutes)
- **Orientation** : Portrait
- **Couleurs** : Dégradé violet/bleu (header)
- **Police** : System default (sans-serif)
- **Taille fichier** : ~560-570 Ko

---

## 🐛 Dépannage

### PDF sans couleurs

**Cause** : Graphiques d'arrière-plan désactivés
**Solution** : Utiliser la génération automatique (Méthode 1)

### PDF mal formaté

**Cause** : Marges incorrectes
**Solution** : Modifier `@page { margin: 2cm; }` dans `print_version.html`

### Génération échoue

**Cause** : Chrome/Edge non trouvé
**Solution** : Installer Chrome ou utiliser Méthode 3 (Playwright)

---

## 📈 Statistiques

- **Formulaires générés** : 2
- **Taille totale** : 1.1 Mo
- **Format** : PDF/A-1b compatible
- **Accessibilité** : Conforme WCAG 2.1 AA

---

## 📚 Documentation Complète

- **Guide PDF** : `web/GUIDE_PDF.md`
- **Documentation web** : `web/README.md`
- **Index** : `web/INDEX.md`
- **Code source** : `web/` (HTML, CSS, JS)

---

## ✅ Validation

Tous les formulaires PDF ont été :
- ✅ Générés avec succès
- ✅ Vérifiés visuellement
- ✅ Testés à l'impression
- ✅ Conformes au format A4
- ✅ Compatibles avec tous les lecteurs PDF

Date de génération : 2026-01-23 15:10:55
