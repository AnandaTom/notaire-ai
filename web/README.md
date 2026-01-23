# Formulaire Web NotaireAI - Collecte Vendeur

Interface web simple pour collecter les informations du vendeur nécessaires à la génération d'un acte notarial.

## 🚀 Utilisation

### Méthode 1: Ouvrir directement dans le navigateur

```bash
# Ouvrir index.html dans votre navigateur préféré
start web/index.html  # Windows
open web/index.html   # macOS
xdg-open web/index.html  # Linux
```

### Méthode 2: Serveur local (recommandé)

```bash
# Python 3
cd web
python -m http.server 8000

# Puis ouvrir: http://localhost:8000
```

### Méthode 3: Live Server (VSCode)

1. Installer l'extension "Live Server"
2. Clic droit sur `index.html` → "Open with Live Server"

## 📋 Fonctionnalités

- **Formulaire complet** avec toutes les informations du vendeur :
  - Identité (nom, prénoms, date et lieu de naissance)
  - Adresse actuelle
  - Situation matrimoniale (avec gestion dynamique du conjoint/partenaire)
  - Pièces justificatives (CNI)
  - Coordonnées bancaires
  - Contact

- **Validation en temps réel** :
  - Champs obligatoires marqués avec *
  - Validation visuelle (bordure verte pour champs valides)
  - Formatage automatique (IBAN, téléphone)

- **Bouton "Remplir avec exemple"** :
  - Génère instantanément un exemple complet
  - Parfait pour tester le formulaire

- **Export des données** :
  - Visualisation JSON formatée
  - Téléchargement du fichier JSON
  - Copie dans le presse-papier

## 📊 Structure des données générées

```json
{
  "vendeur": {
    "personne_physique": {
      "civilite": "M",
      "nom": "DUPONT",
      "prenoms": ["Jean", "Pierre", "Marie"],
      "date_naissance": "1975-06-15",
      "lieu_naissance": "Paris (75)",
      "nationalite": "Française",
      "profession": "Ingénieur"
    },
    "adresse": {
      "adresse": "12 rue de la République",
      "code_postal": "75001",
      "ville": "Paris"
    },
    "situation_matrimoniale": {
      "regime": "marie",
      "conjoint": {
        "nom": "MARTIN",
        "prenoms": ["Sophie", "Marie"],
        "intervient_acte": true
      },
      "date_union": "2005-08-20",
      "lieu_union": "Lyon (69)",
      "type_regime": "communaute_legale"
    },
    "pieces_identite": {
      "cni": {
        "numero": "123456789012",
        "date_emission": "2020-01-15",
        "date_expiration": "2030-01-15",
        "autorite_emission": "Préfecture de Paris"
      }
    },
    "coordonnees_bancaires": {
      "iban": "FR76 1234 5678 9012 3456 7890 123",
      "bic": "BNPAFRPPXXX",
      "nom_banque": "BNP Paribas"
    },
    "contact": {
      "telephone": "06 12 34 56 78",
      "email": "jean.dupont@email.com"
    }
  }
}
```

## 🎨 Design

- Interface moderne et responsive
- Gradient violet/bleu (branding NotaireAI)
- Compatible mobile, tablette et desktop
- Animations fluides et feedback visuel

## 📄 Génération PDF

### Méthode 1: Impression manuelle (Recommandée - Aucune dépendance)

```bash
# Windows
web\generer_pdf.bat

# Ou ouvrir directement
start web/print_version.html
```

Puis dans le navigateur :
1. Cliquer sur "Remplir avec exemple" (optionnel)
2. Appuyez sur **Ctrl+P** (Windows/Linux) ou **Cmd+P** (Mac)
3. Destination : **"Microsoft Print to PDF"** ou **"Enregistrer au format PDF"**
4. Cocher **"Graphiques d'arrière-plan"** pour conserver les couleurs
5. Enregistrer le fichier

### Méthode 2: Génération automatique avec Playwright

```bash
# Installation (une seule fois)
pip install playwright
playwright install chromium

# Génération PDF vide
python web/generer_pdf_simple.py

# Génération PDF avec exemple pré-rempli
python web/generer_pdf_simple.py --exemple

# Spécifier le chemin de sortie
python web/generer_pdf_simple.py --output outputs/mon_formulaire.pdf
```

## 🔄 Intégration avec NotaireAI

Le JSON généré est directement compatible avec le système NotaireAI :

```bash
# 1. Remplir le formulaire web → Télécharger JSON
# 2. Utiliser le JSON avec le pipeline NotaireAI

python execution/workflow_rapide.py \
    --type vente \
    --donnees vendeur_2026-01-23.json \
    --output outputs/acte_dupont.docx
```

## 📝 Extensions futures possibles

- Formulaire acquéreur
- Formulaire bien immobilier
- Gestion multi-vendeurs
- Sauvegarde locale (localStorage)
- Upload de pièces justificatives
- Signature électronique
- Validation côté serveur
- API REST pour intégration backend

## 🛠️ Technologies

- HTML5 pur (pas de framework)
- CSS3 (Grid, Flexbox, animations)
- JavaScript vanilla (pas de dépendances)
- 100% client-side (pas de serveur requis)
