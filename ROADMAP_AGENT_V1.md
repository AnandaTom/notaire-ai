# Roadmap Agent NotaireAI v1.0

> **Objectif**: Premier agent fonctionnel de création & modification d'actes de vente et promesse de vente

**Date**: 24 janvier 2026
**État actuel**: 75% fonctionnel
**Cible**: Agent autonome en production

---

## Résumé de l'Audit

### Ce qui FONCTIONNE (Forces)

| Composant | État | Score |
|:----------|:-----|:-----:|
| Architecture 3-layers | Excellente | ⭐⭐⭐⭐⭐ |
| Performance génération | 5.7s/acte | ⭐⭐⭐⭐⭐ |
| Template vente | 85.1% conforme | ✅ PROD |
| Template règlement copro | 85.5% conforme | ✅ PROD |
| Template modificatif EDD | 91.7% conforme | ✅ PROD |
| Documentation | Exceptionnelle | ⭐⭐⭐⭐⭐ |
| Validation données | 12+ règles métier | ✅ |
| Catalogues (clauses/annexes) | 45+ clauses, 28+ annexes | ✅ |

### Ce qui est INCOMPLET

| Composant | État | Impact |
|:----------|:-----|:-------|
| Template promesse | 60.9% → besoin 80% | 🔴 Bloquant |
| 8 versions exporter_docx | Confusion | 🟠 Maintenance |
| Orchestrateur | Existe mais pas utilisé | 🟠 UX |
| Workflow titre→promesse | Extraction OK, génération non | 🟡 Feature |
| MCP Supabase | Configuré sans token | 🟡 Intégration |

### Ce qui MANQUE

| Fonctionnalité | Priorité |
|:---------------|:--------:|
| Mode agent autonome | 🔴 P0 |
| API REST | 🟠 P1 |
| OCR pour PDF scannés | 🟡 P2 |
| Interface web review | 🟡 P2 |
| Signature électronique | ⚪ P3 |

---

## Roadmap Priorisée

### Phase 1: Nettoyage (1 jour) 🔴 URGENT

```
┌─────────────────────────────────────────────────────────────┐
│  1.1 Nettoyer exporter_docx                                │
│      - Garder: exporter_docx.py (version actuelle)         │
│      - Archiver: 7 autres versions dans /archive/          │
│      - Impact: Maintenance simplifiée                      │
├─────────────────────────────────────────────────────────────┤
│  1.2 Finaliser template promesse                           │
│      - Ajouter sections manquantes (24 titres)             │
│      - Objectif: 60.9% → 80%+                              │
│      - Impact: Promesse utilisable en production           │
├─────────────────────────────────────────────────────────────┤
│  1.3 Documenter Python 3.12 requirement                    │
│      - Supabase incompatible Python 3.14                   │
│      - Mettre à jour requirements.txt                      │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Unification (1-2 jours) 🟠 IMPORTANT

```
┌─────────────────────────────────────────────────────────────┐
│  2.1 Unifier CLI avec orchestrateur                        │
│      - notaire.py → appelle orchestrateur_notaire.py       │
│      - Point d'entrée unique pour tous workflows           │
│      - Commandes: generer, extraire, valider, dashboard    │
├─────────────────────────────────────────────────────────────┤
│  2.2 Intégrer workflow titre→promesse→vente               │
│      - Hooker gestionnaire_titres dans orchestrateur       │
│      - Pipeline: PDF → extraction → génération → DOCX      │
│      - Test end-to-end complet                             │
├─────────────────────────────────────────────────────────────┤
│  2.3 Configurer MCP Supabase                               │
│      - Ajouter access-token dans mcp.json                  │
│      - Tester connexion base de données                    │
│      - Activer lecture/écriture directe                    │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Agent Autonome (2-3 jours) 🎯 OBJECTIF

```
┌─────────────────────────────────────────────────────────────┐
│  3.1 Mode agent "une commande"                             │
│                                                             │
│  Entrée:                                                    │
│    "Crée une promesse de vente pour Martin→Dupont,         │
│     appartement 67m² Lyon 3e, 245000€"                     │
│                                                             │
│  Agent fait automatiquement:                                │
│    1. Parse la demande → structure données                  │
│    2. Recherche Supabase si dossier existant               │
│    3. Complète données manquantes (questions)              │
│    4. Valide cohérence juridique                           │
│    5. Génère acte (template + assemblage + export)         │
│    6. Sauvegarde historique Supabase                       │
│    7. Retourne lien DOCX                                   │
│                                                             │
│  Sortie:                                                    │
│    "✅ Promesse générée: outputs/promesse_martin_2026.docx │
│     Sauvegardé dans Supabase: ref#2026-001"                │
├─────────────────────────────────────────────────────────────┤
│  3.2 Mode modification                                      │
│                                                             │
│  Entrée:                                                    │
│    "Modifie le prix à 250000€ dans la promesse 2026-001"   │
│                                                             │
│  Agent fait:                                                │
│    1. Charge données depuis Supabase                        │
│    2. Applique modification                                 │
│    3. Re-génère acte                                        │
│    4. Versionne (v1 → v2)                                  │
│    5. Sauvegarde nouvelle version                          │
├─────────────────────────────────────────────────────────────┤
│  3.3 Mode recherche                                         │
│                                                             │
│  Entrée:                                                    │
│    "Trouve tous les actes pour le vendeur Martin"          │
│                                                             │
│  Agent fait:                                                │
│    1. Query Supabase                                        │
│    2. Retourne liste avec metadata                          │
└─────────────────────────────────────────────────────────────┘
```

### Phase 4: Robustesse (1 semaine) 🟡 POLISH

```
┌─────────────────────────────────────────────────────────────┐
│  4.1 Tests end-to-end                                       │
│      - 10 scénarios vente, 10 promesse                     │
│      - Cas limites (PACS, divorce, SCI, etc.)              │
│      - CI/CD avec GitHub Actions                           │
├─────────────────────────────────────────────────────────────┤
│  4.2 OCR optionnel                                          │
│      - Intégrer pytesseract pour PDF scannés               │
│      - Fallback regex si OCR échoue                        │
├─────────────────────────────────────────────────────────────┤
│  4.3 Dashboard temps réel                                   │
│      - Métriques: actes générés, temps moyen, erreurs      │
│      - Connexion Supabase live                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Métriques de Succès

| Métrique | Actuel | Cible v1.0 |
|:---------|:------:|:----------:|
| Templates ≥80% conformité | 3/4 | **4/4** |
| Temps génération | 5.7s | <10s |
| Workflow une commande | ❌ | ✅ |
| Supabase intégré | Partiel | ✅ Complet |
| Mode modification | ❌ | ✅ |
| Tests automatisés | 40% | 70% |

---

## Prochaine Action Immédiate

**Commencer par Phase 1.1**: Nettoyer les 8 versions de exporter_docx

```bash
# Créer archive et garder version principale
mkdir execution/archive_exporter
mv execution/exporter_docx_*.py execution/archive_exporter/
# Garder uniquement exporter_docx.py
```

Cela simplifiera immédiatement la maintenance et évitera les confusions.

---

## Architecture Cible Agent v1.0

```
                    ┌─────────────────────┐
                    │   Utilisateur       │
                    │   (Notaire/Claude)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   MCP Supabase      │
                    │   (accès direct DB) │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Orchestrateur│    │   Extraction    │    │   Recherche     │
│   (notaire.py)│    │   (titres PDF)  │    │   (historique)  │
└───────┬───────┘    └─────────────────┘    └─────────────────┘
        │
        ├─────────────┬─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Valider   │ │ Assembler │ │ Exporter  │ │ Comparer  │
│ (schéma)  │ │ (Jinja2)  │ │ (DOCX)    │ │ (score)   │
└───────────┘ └───────────┘ └───────────┘ └───────────┘
```

---

*Généré automatiquement par l'audit du 24/01/2026*
