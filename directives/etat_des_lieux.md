# État des Lieux - NotaireAI

> **Date**: 28 janvier 2026
> **Version**: 1.4.0

---

## Conformité des Templates

| Template | Conformité | Statut | Seuil |
|----------|-----------|--------|-------|
| **Promesse de vente** | **88.9%** | ✅ PROD | ≥80% |
| **Vente** | **80.2%** | ✅ PROD | ≥80% |
| Règlement copropriété | 85.5% | ✅ PROD | ≥80% |
| Modificatif EDD | 91.7% | ✅ PROD | ≥80% |

**Résultat: 4/4 templates en production!**

---

## Architecture des Fichiers

### Structure Principale

```
notaire-ai/
├── api/                          # API REST (FastAPI)
│   └── main.py                   # 1100+ lignes, multi-tenant
├── modal/                        # 🆕 Déploiement Modal.com
│   ├── modal_app.py             # App principale avec CRON
│   ├── modal_app_legacy.py      # Version simplifiée
│   └── README.md
├── execution/                    # 65 scripts Python
├── templates/                    # 9 templates Markdown
│   └── sections/                # 44 sections modulaires
├── schemas/                     # 16 schémas JSON
├── exemples/                    # 10 fichiers données
├── directives/                  # Documentation
└── notaire.py                   # CLI racine
```

### Endpoints API

| Catégorie | Endpoints |
|-----------|-----------|
| **Agent** | `/agent/execute`, `/agent/feedback` |
| **Dossiers** | `/dossiers` (CRUD complet) |
| **Clauses** | `/clauses/sections`, `/clauses/profils`, `/clauses/analyser`, `/clauses/feedback`, `/clauses/suggestions` |
| **Système** | `/health`, `/stats`, `/me` |

---

## Système de Clauses Intelligentes

### Catalogue (schemas/clauses_promesse_catalogue.json)

| Type | Nombre | Description |
|------|--------|-------------|
| **Sections fixes** | 44 | Obligatoires, toujours présentes |
| **Sections variables** | 21 | Conditionnelles selon données |
| **Profils** | 4 | Configurations pré-définies |

### Profils Disponibles

1. **standard_simple** - 1 vendeur → 1 acquéreur
2. **standard_couple** - 2 vendeurs → 2 acquéreurs
3. **complexe_investisseur** - Avec vente préalable, séquestre
4. **sans_pret** - Paiement comptant

### Apprentissage Continu

- Jobs CRON Modal: `daily_learning_job` (2h), `weekly_catalog_sync` (dimanche 3h)
- Feedback notaire via API `/clauses/feedback`
- Enrichissement catalogues automatique

---

## Pipeline de Génération

### Performance

| Étape | Durée |
|-------|-------|
| Assemblage Jinja2 | ~1.5s |
| Export DOCX | ~3.5s |
| Vérification | ~0.7s |
| **TOTAL** | **~5.7s** |

### Commandes CLI

```bash
# Génération complète
python notaire.py promesse --donnees data.json --output acte.docx
python notaire.py vente --donnees data.json --output acte.docx

# Gestion clauses
python notaire.py clauses lister
python notaire.py clauses profils
python notaire.py clauses analyser --donnees data.json

# Feedback
python notaire.py feedback soumettre --action ajouter --cible "section_id"
```

---

## Données d'Exemple Enrichies

Les fichiers `exemples/donnees_*_exemple.json` contiennent maintenant:

- ✅ Fiscalité complète (contribution sécurité immobilière)
- ✅ Impôts locaux
- ✅ Travaux et garantie décennale
- ✅ Assurance dommages-ouvrage
- ✅ Obligation déclarative propriétaire
- ✅ Aides (APL, ANAH)

---

## Déploiement Modal

### Commandes

```bash
# Production
modal deploy modal/modal_app.py

# Développement
modal serve modal/modal_app.py
```

### Endpoint Production

```
https://notaire-ai--fastapi-app.modal.run/
```

### Configuration Secrets

1. **supabase-credentials**: `SUPABASE_URL`, `SUPABASE_KEY`
2. **notaire-secrets**: `ANTHROPIC_API_KEY`

---

## Améliorations Récentes

### v1.4.0 (28 janvier 2026)

1. ✅ Template vente passé de 77.8% à 80.2%
2. ✅ Fichiers Modal organisés dans `modal/`
3. ✅ Données d'exemple enrichies (fiscalité, travaux, assurances)
4. ✅ Sections `section_travaux_construction.md` et `section_assurances_garanties.md` intégrées
5. ✅ Endpoints clauses ajoutés à l'API

### v1.3.0 (précédent)

- Système de clauses modulaires (65 sections)
- Gestionnaire clauses intelligent
- API feedback notaire
- Jobs CRON apprentissage

---

## Points d'Attention

### Sections à Améliorer (Template Vente)

Titres manquants détectés:
- Récapitulatif de l'effort respectif de financement
- Avantage fiscal lié à un engagement de location
- Obligation déclarative du propriétaire
- Absence d'opération de construction
- Diagnostics environnementaux
- État des risques
- Règlement définitif des charges

### Tableaux

- Original: 6 tableaux
- Généré: 4 tableaux
- Écart: -2 (à investiguer)

---

## Prochaines Étapes

1. [ ] Améliorer score tableaux (56.7% → 80%+)
2. [ ] Ajouter sections manquantes identifiées
3. [ ] Tests automatisés pipeline complet
4. [ ] Documentation API Swagger/OpenAPI

---

*Document généré automatiquement - État au 28 janvier 2026*
