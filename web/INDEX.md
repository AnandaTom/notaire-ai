# 📋 Formulaire Web NotaireAI - Index

Interface web complète pour collecter les informations du vendeur nécessaires à la génération d'un acte notarial.

---

## 🎯 Démarrage Rapide

### Option A: Formulaire Interactif

```bash
# Ouvrir le formulaire dans le navigateur
start web/index.html

# Ou avec un serveur local
cd web
python -m http.server 8000
# Puis ouvrir http://localhost:8000
```

### Option B: Générer directement un PDF

```bash
# Méthode automatique (1 clic)
cd web
generer_pdf.bat
```

---

## 📚 Documentation

| Document | Description | Usage |
|----------|-------------|-------|
| [README.md](README.md) | Documentation complète | Vue d'ensemble, fonctionnalités, intégration |
| [GUIDE_PDF.md](GUIDE_PDF.md) | Guide de génération PDF | 3 méthodes détaillées pour créer des PDFs |
| [INDEX.md](INDEX.md) | Ce fichier | Navigation rapide |

---

## 📁 Fichiers Principaux

### Interface Web

| Fichier | Type | Description |
|---------|------|-------------|
| [index.html](index.html) | HTML | Formulaire principal interactif |
| [print_version.html](print_version.html) | HTML | Version optimisée pour l'impression PDF |
| [styles.css](styles.css) | CSS | Design moderne avec gradient violet/bleu |
| [script.js](script.js) | JavaScript | Logique, validation, export JSON |

### Scripts de Génération PDF

| Fichier | Type | Description |
|---------|------|-------------|
| [generer_pdf.bat](generer_pdf.bat) | Batch | Menu interactif (auto/manuel) |
| [generer_pdf_auto.ps1](generer_pdf_auto.ps1) | PowerShell | Génération automatique Chrome/Edge |
| [generer_pdf_simple.py](generer_pdf_simple.py) | Python | Génération avec Playwright |
| [generer_pdf.py](generer_pdf.py) | Python | (Obsolète) WeasyPrint - nécessite dépendances système |

---

## 🚀 Workflows Typiques

### Workflow 1: Collecte + Export JSON

1. Ouvrir `index.html`
2. Remplir le formulaire (ou cliquer "Remplir avec exemple")
3. Cliquer "Enregistrer les informations"
4. Télécharger le JSON
5. Utiliser avec le pipeline NotaireAI

```bash
python execution/workflow_rapide.py \
    --type vente \
    --donnees vendeur_2026-01-23.json \
    --output outputs/acte.docx
```

### Workflow 2: Formulaire Papier

1. Exécuter `generer_pdf.bat`
2. Choisir "Génération automatique"
3. Imprimer le PDF (outputs/formulaire_vendeur_*.pdf)
4. Utiliser lors du RDV client
5. Re-saisir dans le formulaire web après le RDV

### Workflow 3: Test Rapide

1. Ouvrir `index.html`
2. Cliquer "Remplir avec exemple"
3. Vérifier les données
4. Cliquer "Copier JSON"
5. Tester directement dans le pipeline

---

## 🎨 Captures d'Écran

### Formulaire Principal (index.html)

- Header avec gradient violet/bleu
- 8 sections de collecte
- Validation en temps réel
- Boutons d'action (Réinitialiser, Exemple, Enregistrer)
- Visualisation JSON formatée

### Version Imprimable (print_version.html)

- Bandeau d'instructions jaune (masqué à l'impression)
- Bouton "Imprimer / PDF" rapide
- Mise en page optimisée A4
- Marges 2cm

---

## 📊 Données Collectées

### Sections Obligatoires (*)

1. **Identité** : Civilité, nom, prénoms, date/lieu naissance, nationalité
2. **Adresse** : Adresse complète, code postal, ville
3. **Situation matrimoniale** : Régime (+ conjoint si marié/pacsé)
4. **Pièces identité** : CNI (numéro, dates, autorité)
5. **Coordonnées bancaires** : IBAN, BIC, nom banque
6. **Contact** : Téléphone, email

### Format de Sortie

```json
{
  "vendeur": {
    "personne_physique": {...},
    "adresse": {...},
    "situation_matrimoniale": {...},
    "pieces_identite": {...},
    "coordonnees_bancaires": {...},
    "contact": {...}
  }
}
```

---

## 🔧 Maintenance

### Ajouter un Champ

1. Modifier `index.html` (ou `print_version.html`)
2. Ajouter le champ HTML avec `id` unique
3. Mettre à jour `script.js` pour collecter la valeur
4. Tester avec "Remplir avec exemple"

### Modifier le Style

1. Éditer `styles.css`
2. Pour l'impression : section `@media print` dans `print_version.html`
3. Tester en mode aperçu (Ctrl+P)

### Enrichir les Données d'Exemple

1. Modifier la fonction `fillExample()` dans `script.js`
2. Utiliser des données réalistes
3. Respecter les contraintes (dates, formats)

---

## 🐛 Résolution de Problèmes

| Problème | Solution |
|----------|----------|
| JSON vide | Vérifier que tous les champs `*` sont remplis |
| PDF sans couleurs | Cocher "Graphiques d'arrière-plan" |
| Conjoint non affiché | Sélectionner "Marié(e)" ou "Pacsé(e)" |
| Script PowerShell bloqué | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Chrome/Edge introuvable | Installer Chrome ou utiliser impression manuelle |

Voir [GUIDE_PDF.md](GUIDE_PDF.md) pour plus de détails.

---

## 📈 Extensions Futures

Idées pour améliorer le formulaire :

- [ ] Formulaire acquéreur séparé
- [ ] Formulaire bien immobilier
- [ ] Multi-vendeurs (co-vendeurs)
- [ ] Sauvegarde locale (localStorage)
- [ ] Upload de pièces justificatives (drag & drop)
- [ ] Validation avancée (IBAN, SIRET)
- [ ] Mode sombre
- [ ] Internationalisation (i18n)
- [ ] API REST pour intégration backend
- [ ] Signature électronique

---

## 🛠️ Technologies

- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **PDF Generation** :
  - Chrome/Edge headless (Méthode 1)
  - Print API native (Méthode 2)
  - Playwright + Chromium (Méthode 3)
- **Dépendances** : Aucune (100% client-side)

---

## 📝 Licence & Contact

Partie du projet **NotaireAI** - Génération automatisée d'actes notariaux.

Pour toute question sur le formulaire web :
- Consulter [README.md](README.md) et [GUIDE_PDF.md](GUIDE_PDF.md)
- Tester avec "Remplir avec exemple"
- Vérifier les logs dans la console du navigateur (F12)
