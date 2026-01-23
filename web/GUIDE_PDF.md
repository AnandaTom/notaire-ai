# Guide de Génération PDF - Formulaire Vendeur

Ce guide présente **3 méthodes** pour générer un PDF du formulaire vendeur, du plus simple au plus avancé.

---

## 🚀 Méthode 1: Script Automatisé (Recommandée)

**Avantages**: Simple, rapide, 1 clic
**Prérequis**: Chrome ou Edge installé

### Windows

Double-cliquez sur `generer_pdf.bat` ou exécutez :

```bash
cd web
generer_pdf.bat
```

Le script propose 2 options :
1. **Génération automatique** - Crée le PDF directement (564 Ko)
2. **Impression manuelle** - Ouvre le navigateur pour plus de contrôle

### Sortie

Le PDF est automatiquement créé dans :
```
outputs/formulaire_vendeur_YYYYMMDD_HHMMSS.pdf
```

---

## 📝 Méthode 2: Impression Manuelle

**Avantages**: Contrôle total, personnalisation
**Prérequis**: Aucun

### Étapes

1. **Ouvrir le formulaire imprimable**
   ```bash
   start web/print_version.html
   ```

2. **Remplir le formulaire** (optionnel)
   - Cliquer sur "Remplir avec exemple" pour des données de test
   - Ou remplir manuellement les champs

3. **Imprimer en PDF**
   - Appuyez sur **Ctrl+P** (Windows/Linux) ou **Cmd+P** (Mac)
   - Destination : **"Microsoft Print to PDF"** ou **"Enregistrer au format PDF"**
   - ✅ Cocher **"Graphiques d'arrière-plan"** pour conserver les couleurs
   - Cliquer sur **"Enregistrer"**

### Résultat

- Format : A4
- Marges : 2cm (toutes)
- Taille : ~550-600 Ko
- Les boutons sont automatiquement masqués à l'impression

---

## 🔧 Méthode 3: Script Python avec Playwright

**Avantages**: Automatisation complète, scriptable, intégrable
**Prérequis**: Python, Playwright

### Installation (une seule fois)

```bash
pip install playwright
playwright install chromium
```

### Utilisation

```bash
# PDF vide
python web/generer_pdf_simple.py

# PDF avec exemple pré-rempli
python web/generer_pdf_simple.py --exemple

# Spécifier le chemin de sortie
python web/generer_pdf_simple.py --output mon_formulaire.pdf
```

### Options

| Option | Description |
|--------|-------------|
| `--output`, `-o` | Chemin du PDF de sortie |
| `--exemple`, `-e` | Pré-remplir avec données d'exemple |

### Exemple complet

```bash
python web/generer_pdf_simple.py \
    --exemple \
    --output outputs/formulaire_dupont_2026.pdf
```

---

## 📊 Comparaison des Méthodes

| Critère | Méthode 1 (Script) | Méthode 2 (Manuel) | Méthode 3 (Playwright) |
|---------|-------------------|-------------------|----------------------|
| **Simplicité** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Vitesse** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Contrôle** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Automatisation** | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Prérequis** | Chrome/Edge | Aucun | Python + Playwright |

---

## 🎨 Personnalisation

### Modifier les marges PDF

Éditez [print_version.html](print_version.html), section `@media print` :

```css
@page {
    size: A4;
    margin: 2cm;  /* Modifier ici */
}
```

### Modifier les couleurs d'impression

Pour des couleurs plus vives dans le PDF :

```css
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
```

---

## 🐛 Dépannage

### Le PDF est vide ou mal formaté

**Cause**: Graphiques d'arrière-plan désactivés
**Solution**: Cocher "Graphiques d'arrière-plan" dans les options d'impression

### Les couleurs ne s'impriment pas

**Cause**: `print-color-adjust` non supporté
**Solution**: Utiliser Chrome/Edge récent, ou Méthode 3 (Playwright)

### "Chrome/Edge non trouvé" (Méthode 1)

**Cause**: Navigateur non installé ou chemin non standard
**Solution**:
- Installer Chrome : https://www.google.com/chrome/
- Ou utiliser Méthode 2 (manuel)
- Ou utiliser Méthode 3 (Playwright)

### Erreur Playwright (Méthode 3)

**Cause**: Chromium non installé
**Solution**:
```bash
playwright install chromium
```

---

## 📦 Fichiers Générés

Tous les PDFs sont automatiquement enregistrés dans :

```
outputs/
├── formulaire_vendeur_20260123_150802.pdf
├── formulaire_vendeur_exemple_20260123_151234.pdf
└── ...
```

Format du nom :
- `formulaire_vendeur` : Type de document
- `_exemple` : (optionnel) Pré-rempli avec données de test
- `_YYYYMMDD_HHMMSS` : Timestamp
- `.pdf` : Extension

---

## 🔄 Intégration avec le Pipeline NotaireAI

Le formulaire PDF peut servir de support papier pour :

1. **Collecte terrain** - Le notaire remplit à la main lors du RDV client
2. **Saisie digitale** - Les données sont ensuite saisies dans le formulaire web
3. **Export JSON** - Téléchargement du JSON depuis le formulaire web
4. **Génération acte** - Utilisation du JSON avec le pipeline

```bash
# Workflow complet
python execution/workflow_rapide.py \
    --type vente \
    --donnees vendeur_dupont.json \
    --output outputs/acte_dupont.docx
```

---

## 📝 Support

**Questions ou problèmes ?**

1. Vérifier ce guide en premier
2. Consulter [README.md](README.md) pour la documentation complète
3. Tester avec "Remplir avec exemple" pour isoler le problème
4. Essayer les 3 méthodes pour identifier laquelle fonctionne

**Logs utiles** :

```bash
# Voir les PDFs générés
ls -lh outputs/formulaire_vendeur_*.pdf

# Tester la génération
python web/generer_pdf_simple.py --exemple
```
