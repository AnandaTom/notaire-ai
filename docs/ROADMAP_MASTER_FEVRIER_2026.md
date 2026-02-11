# Roadmap Master — Notomai Février 2026

> **Document consolidé unique** — État actuel, Sprint 15 jours, Roadmap 6 semaines
> **Date**: 11/02/2026 | **Version**: 2.0.0 | **Équipe**: Tom, Augustin, Payos

---

## 📋 Table des Matières

1. [État Actuel & Audit Génération](#1-état-actuel--audit-génération)
2. [Sprint 1 (15 jours) — Production-Ready](#2-sprint-1-15-jours--production-ready)
3. [Sprints 2-4 (6 semaines) — Architecture & Performance](#3-sprints-2-4-6-semaines--architecture--performance)
4. [Prochaines Étapes Génération Promesses & Actes](#4-prochaines-étapes-génération-promesses--actes)
5. [Métriques & Risques](#5-métriques--risques)

---

## 1. État Actuel & Audit Génération

### 1.1 Architecture Globale

```
✅ PRODUCTION-READY (v2.0.0)
├─ 7 templates PROD (conformité 80-92%)
├─ 257 tests passing (3 skipped)
├─ API complète (promesse, vente, viager)
├─ Supabase intégré (18 tables)
├─ Modal déployé
└─ Pipeline 5.7s (assemblage → export)

⚠️ DETTE TECHNIQUE IDENTIFIÉE
├─ 30 exception handlers trop larges (🔴 CRITIQUE)
├─ 2 God classes (1,500+ lignes) (🔴 CRITIQUE)
├─ Cache non-borné → fuite mémoire (🔴 CRITIQUE)
├─ 44 print() au lieu de logger (⚠️ HAUTE)
└─ Pas de tests E2E pipeline complet (⚠️ HAUTE)
```

### 1.2 État des Templates

| Template | Conformité | Statut | Bookmarks | Notes |
|----------|-----------|--------|-----------|-------|
| **Vente lots copropriété** | **80.2%** | ✅ PROD | 361 | Template de référence |
| **Promesse copropriété** | **88.9%** | ✅ PROD | 298 | Sous-type: creation |
| **Promesse hors copropriété** | NEW | ✅ PROD | - | +3 sections conditionnelles |
| **Promesse terrain à bâtir** | NEW | ✅ PROD | - | Support lotissement |
| **Promesse viager** | NEW | ✅ PROD | - | **+4 sections viager** |
| **Règlement copropriété** | **85.5%** | ✅ PROD | 116 | 22 tableaux |
| **Modificatif EDD** | **91.7%** | ✅ PROD | 60 | Template le plus abouti |

**Couverture complète**: 3 catégories de biens + viager cross-catégorie + 6 sous-types conditionnels

### 1.3 Pipeline de Génération (Audit Détaillé)

```
┌────────────────────────────────────────────────────────────┐
│              PIPELINE ACTUEL (5.7s)                         │
├────────────────────────────────────────────────────────────┤
│ 1. Validation (50ms)                                       │
│    - Schema JSON (jsonschema)                              │
│    - Règles sémantiques (quotités, prix, Carrez)          │
│    - Validation viager (bouquet + rente obligatoires)      │
│                                                            │
│ 2. Détection 3 Niveaux (20ms)                             │
│    - Niveau 1: Catégorie (copro/hors copro/terrain)       │
│    - Niveau 2: Type (standard/premium/mobilier)            │
│    - Niveau 3: Sous-type (viager/lotissement/creation)     │
│    - Confiance: 70-95%                                     │
│                                                            │
│ 3. Assemblage Jinja2 (1.5s)                               │
│    - Sélection template selon détection                    │
│    - Sections conditionnelles (57 deepcopy)                │
│    - Evaluation conditions ({% if %})                      │
│    - Rendu Markdown final                                  │
│                                                            │
│ 4. Export DOCX (3.5s)                                      │
│    - Markdown → python-docx                                │
│    - Formatage (Times 11pt, 60mm marge)                    │
│    - Génération bookmarks                                  │
│                                                            │
│ 5. Vérification (0.7s)                                     │
│    - Comparaison structure vs trame                        │
│    - Calcul conformité (80-92%)                            │
│                                                            │
│ TOTAL: 5.7s (~8 pages/seconde)                             │
└────────────────────────────────────────────────────────────┘
```

**Points forts**:
- ✅ Détection multi-niveaux fiable (confiance 70-95%)
- ✅ Support viager cross-catégorie (toutes catégories de biens)
- ✅ Validation temps réel champ par champ
- ✅ Enrichissement cadastre automatique (APIs gouv.fr)
- ✅ 257 tests automatisés couvrant E2E + cross-catégories

**Points faibles identifiés**:
- ❌ 57 appels `deepcopy()` → overhead ~100ms évitable
- ❌ Pas de parallélisation (séquentiel uniquement)
- ❌ Cache non-borné → fuite mémoire sur Modal
- ❌ Pas de QA automatique post-génération

### 1.4 API Endpoints — État Complet

#### Génération Promesses (v2.0.0 — Support Viager)

| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/promesses/detecter-type` | POST | Détection 3 niveaux (retourne `categorie_bien`, `type_promesse`, `sous_type`) | ✅ PROD |
| `/promesses/generer` | POST | Génération complète avec `sous_type` dans response | ✅ PROD |
| `/promesses/valider` | POST | Validation avec règles viager (bouquet/rente obligatoires) | ✅ PROD |
| `/questions/promesse` | GET | Questions filtrées (`?sous_type=viager` → 20 questions viager) | ✅ PROD |
| `/workflow/promesse/start` | POST | Démarrer workflow (accepte `sous_type` dans body) | ✅ PROD |
| `/workflow/promesse/{id}/generate` | POST | Génération DOCX (retourne `sous_type`) | ✅ PROD |
| `/workflow/promesse/{id}/generate-stream` | GET | Génération SSE (progression temps réel) | 🟡 MOCK |

#### Validation & Cadastre

| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/validation/donnees` | POST | Validation complète | ✅ PROD |
| `/validation/champ` | POST | Validation temps réel champ | ✅ PROD |
| `/cadastre/geocoder` | POST | Adresse → code INSEE | ✅ PROD |
| `/cadastre/parcelle` | GET | Parcelle → données cadastrales | ✅ PROD |
| `/cadastre/enrichir` | POST | Enrichissement auto | ✅ PROD |

**État**: 12/13 endpoints PROD, 1 endpoint SSE à implémenter (mock actuellement)

### 1.5 Base de Données — Supabase (18 Tables)

| Table | Statut | Role | Notes |
|-------|--------|------|-------|
| `etudes` | ✅ | Tenant (étude notariale) | Multi-tenant actif |
| `notaire_users` | ✅ | Profils notaires | Auth Supabase |
| `dossiers` | ✅ | Dossiers avec `donnees_questionnaire` JSONB | État workflow |
| `conversations` | ✅ | Historique chatbot + `agent_state` | Mémoire agent |
| `feedbacks` | ✅ | Retours notaires | Self-annealing |
| `promesses_generees` | ✅ | Historique promesses + analytics viager | **v2.0.0** |
| `qr_sessions` | ✅ | Sessions Q&R avec `sous_type` | **v2.0.0** |
| `actes_generes` | ✅ | Documents générés | Tracking conformité |
| `clients` | ✅ | Chiffrement E2E | RGPD |
| `form_submissions` | ✅ | Formulaires clients (tokens 7j) | Sécurisé |
| `documents_client` | ✅ | Upload documents (CNI, etc.) | Stockage |
| `templates` | ✅ | Catalogue templates | Conformité score |
| `evenements_dossier` | ✅ | Timeline dossier | Audit trail |
| `rappels` | ✅ | Alertes + échéances | Notifications |
| `audit_logs` | ✅ | Sécurité + traçabilité | Compliance |
| `rgpd_requests` | ✅ | Droit d'accès/suppression | RGPD |
| `agent_api_keys` | ✅ | Clés API par étude | Auth agents |
| `api_costs_tracking` | 🟡 | Tracking coûts API | À créer |

**Sécurité**:
- ⚠️ 8 vues `SECURITY DEFINER` à corriger (bypass RLS)
- ⚠️ 2 Edge Functions `verify_jwt: false` à sécuriser
- ⚠️ 18 FK non indexées (performance)
- ⚠️ ~20 RLS policies avec `auth.uid()` à optimiser

### 1.6 Tests — Couverture Complète

```
257 tests passing (3 skipped)

BREAKDOWN:
├─ Détection viager: 6 tests (multi-marqueurs, seuils, cross-catégories)
├─ Validation viager: 4 tests (bouquet, rente, warnings santé)
├─ E2E viager: 3 tests (complet, abandon DUH, rachat rente)
├─ E2E cross-catégories: 4 tests (viager+copro, viager+hors copro, non-régressions)
├─ Détection sous-types: 6 tests (lotissement, groupe, servitudes)
├─ Validation sections conditionnelles: 6 tests
├─ E2E sections conditionnelles: 3 tests
├─ Gestionnaire promesses: 25 tests (legacy)
├─ Pipeline complet: 200 tests (assemblage, export, validation, cadastre)

SKIPPED:
- 3 tests nécessitant Anthropic API (génération agents)
```

**Coverage**: ~75% (objectif Sprint 1: >80%)

### 1.7 Audit Spécifique Génération — Gaps & Opportunités

#### ✅ Ce qui fonctionne bien

1. **Détection intelligente 3 niveaux**
   - Précision: 70-95% selon complexité
   - Viager cross-catégorie détecté correctement
   - Fallback explicite si confiance <70%

2. **Validation complète**
   - Schema JSON + règles sémantiques
   - Validation temps réel champ par champ
   - Règles viager (bouquet + rente obligatoires)

3. **Templates modulaires**
   - Sections conditionnelles ({% if %})
   - Sections réutilisables (templates/sections/)
   - Conformité 80-92% vs trames originales

4. **Enrichissement automatique**
   - Cadastre via APIs gouv.fr (500ms)
   - Prefill 64% depuis titre de propriété
   - Multi-parties ("Martin & Pierre → Dupont & Thomas")

#### ❌ Ce qui doit être amélioré

1. **Performance**
   - ❌ 57 deepcopy inutiles → overhead ~100ms
   - ❌ Pipeline séquentiel (pas de parallélisation)
   - ❌ Cache non-borné (fuite mémoire Modal)
   - ❌ Pas de benchmark automatisé (régression non détectée)

2. **Qualité**
   - ❌ Pas de QA automatique post-génération
   - ❌ Pas de suggestions clauses contextuelles
   - ❌ Exception handlers trop larges (30 instances)
   - ❌ Print au lieu de logger (44 instances)

3. **Maintenabilité**
   - ❌ God classes (1,548 lignes gestionnaire_promesses.py)
   - ❌ Type hints incomplets (40% seulement)
   - ❌ Pas d'abstraction stockage (couplage Supabase fort)

4. **UX Frontend**
   - ❌ Pas de workflow multi-étapes visuel
   - ❌ Pas de formulaires dynamiques (97 questions schema)
   - ❌ Pas de streaming génération (SSE mock)
   - ❌ Pas de review paragraphe par paragraphe

---

## 2. Sprint 1 (15 jours) — Production-Ready

**Dates**: 11/02 - 03/03/2026 (3 semaines)

### Objectifs Globaux

| Pilier | Objectif | Métrique |
|--------|----------|----------|
| **💰 Coûts** | Réduire de 93% | $260 → $17/mois |
| **🛡️ Stabilité** | 0 erreurs silencieuses | 30 → 0 exception handlers |
| **📊 Qualité** | Logging structuré | 44 print → 100% logger |
| **⚡ Performance** | Pas de fuite mémoire | Cache LRU borné |
| **🎨 UX** | Workflow complet | Chat + formulaire + review |
| **👥 Pilotes** | Onboarding prêt | 5 études contactées |

### Vue d'Ensemble

```
SEMAINE 1 (Jour 1-5)     SEMAINE 2 (Jour 6-10)    SEMAINE 3 (Jour 11-15)
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ TOM              │     │ AUGUSTIN         │     │ TOUS             │
│ • Optimisations  │     │ • Workflow UX    │     │ • Tests E2E      │
│ • Exception fix  │     │ • Formulaires    │     │ • Sécurité       │
│ • Cache LRU      │     │ • SSE Progress   │     │ • Démo pilotes   │
│                  │     │                  │     │                  │
│ PAYOS            │     │ TOM              │     │ DELIVERABLE      │
│ • Monitoring     │     │ • Support API    │     │ • 5 études       │
│ • Migrations     │     │ • Tests backend  │     │ • App complète   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 📅 SEMAINE 1: Backend Optimisations & Stabilisation

#### JOUR 1 (Mardi 11/02) — Tom: Smart Opus Usage + 🔴 Exception Handlers (Partie 1)

**MATIN (09h-13h): Smart Opus Usage**
- [ ] 09h00-10h30: Lire OPTIMISATION_COUTS_API.md
- [ ] 10h30-12h30: Implémenter `_choisir_modele()` dans orchestrateur.py
  ```python
  def _choisir_modele(self, type_operation: str, confiance: float) -> str:
      """Sonnet si confiance >80%, Opus sinon"""
      if type_operation == "detection" and confiance > 0.80:
          return "claude-sonnet-4-5-20250929"
      elif type_operation == "validation":
          return "claude-haiku-4-5-20251001"  # Déterministe
      else:
          return "claude-opus-4-6"
  ```
- [ ] 12h30-13h00: Tests rapides smart routing

**APRÈS-MIDI (14h-17h30): 🔴 CRITIQUE - Remplacer Exception Handlers**
- [ ] 14h00-15h00: Lire RECOMMANDATIONS_AMELIORATIONS_2026.md (Item 1)
- [ ] 15h00-17h30: Corriger gestionnaire_promesses.py (11 instances)
  ```python
  # ❌ AVANT
  try:
      resultat = self._evaluer_condition(condition, donnees)
  except Exception as e:
      warnings.append(f"Erreur: {e}")  # Silencieux !

  # ✅ APRÈS
  try:
      resultat = self._evaluer_condition(condition, donnees)
  except KeyError as e:
      warnings.append(f"Champ manquant: {e}")
  except ValueError as e:
      logger.error(f"Valeur incorrecte: {e}")
      raise ValidationError(f"Données invalides: {e}")
  ```

**Livrables**:
- ✅ orchestrateur.py updated avec smart routing
- ✅ gestionnaire_promesses.py: 11/30 exception handlers corrigés
- ✅ Tests: Exception spécifiques levées correctement

**Métriques**:
- Target: 60% Sonnet, 35% Haiku, 5% Opus
- Coût/gen: $0.26 → $0.10
- Exception handlers: 30 → 19 (11 corrigés)

---

#### JOUR 2 (Mercredi 12/02) — Tom: 🔴 Exception Handlers (Partie 2) + Logging Standardisé

**MATIN (09h-13h): 🔴 Exception Handlers Fin**
- [ ] 09h00-11h00: Corriger orchestrateur.py (8 instances)
- [ ] 11h00-13h00: Corriger gestionnaire_titres.py (7 instances)

**APRÈS-MIDI (14h-17h30): ⚠️ Logging Standardisé**
- [ ] 14h00-15h00: Créer execution/utils/logger.py
  ```python
  import logging
  from rich.logging import RichHandler

  def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
      logger = logging.getLogger(name)
      logger.setLevel(level)
      handler = RichHandler(rich_tracebacks=True)
      formatter = logging.Formatter(
          '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )
      handler.setFormatter(formatter)
      logger.addHandler(handler)
      return logger
  ```
- [ ] 15h00-16h30: Remplacer print() dans core/ (8 fichiers)
- [ ] 16h30-17h30: Tests: vérifier logs structurés

**Livrables**:
- ✅ execution/utils/logger.py créé
- ✅ Exception handlers: 19 → 4 (15 corrigés supplémentaires)
- ✅ Print statements: 44 → 0 dans core/
- ✅ Logs structurés avec timestamp, level, context

**Métriques**:
- Exception handlers: 30 → 4 (26 corrigés)
- Print vs logger: 0% → 100% logger dans core/

---

#### JOUR 2 (Mercredi 12/02) — Payos: Infrastructure Monitoring

**Objectif**: Dashboard coûts temps réel

**Tâches**:
- [ ] 09h00-11h00: Créer table Supabase api_costs_tracking
  ```sql
  CREATE TABLE api_costs_tracking (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      etude_id UUID REFERENCES etudes(id),
      operation VARCHAR(50),  -- detection, validation, generation
      model VARCHAR(50),      -- opus-4-6, sonnet-4-5, haiku-4-5
      input_tokens INT,
      output_tokens INT,
      cost_usd DECIMAL(10,6),
      created_at TIMESTAMPTZ DEFAULT NOW()
  );

  CREATE INDEX idx_costs_etude_date ON api_costs_tracking(etude_id, created_at);
  CREATE INDEX idx_costs_model ON api_costs_tracking(model);
  ```
- [ ] 11h00-13h00: Créer vue v_daily_costs
- [ ] 14h00-16h00: Dashboard Grafana ou Metabase
- [ ] 16h00-17h30: Alertes Slack si coûts >$0.05/gen

**Livrables**:
- ✅ Migration 20260212_api_costs_tracking.sql
- ✅ Dashboard temps réel
- ✅ Alertes Slack configurées

---

#### JOUR 3 (Jeudi 13/02) — Tom: Output Optimization + 🔴 Scalabilité Fixes

**MATIN (09h-13h): Output Optimization + Règles Déterministes**
- [ ] 09h00-10h30: Ajouter max_tokens à tous appels API
  - Détection type: 100 tokens
  - Validation: 200 tokens
  - Suggestions clauses: 500 tokens
  - QA review: 300 tokens
- [ ] 10h30-12h00: Créer validation_deterministe.py
  ```python
  def valider_champs_obligatoires(donnees: dict, schema: dict) -> ResultatValidation:
      """Validation sans LLM via jsonschema"""
      import jsonschema
      try:
          jsonschema.validate(donnees, schema)
          return ResultatValidation(valide=True, erreurs=[])
      except jsonschema.ValidationError as e:
          return ResultatValidation(valide=False, erreurs=[str(e)])
  ```
- [ ] 12h00-13h00: Créer detecter_type_acte_rapide() (regex, 70% cas)

**APRÈS-MIDI (14h-17h30): 🔴 CRITIQUE - Scalabilité Fixes**
- [ ] 14h00-15h30: Corriger cache non-borné dans assembler_acte.py
  ```python
  # ❌ AVANT - Fuite mémoire sur Modal
  _env_cache: Dict[str, Environment] = {}  # Jamais vidé !

  # ✅ APRÈS - Cache LRU borné
  from functools import lru_cache

  @lru_cache(maxsize=10)
  def _get_cached_environment(template_dir: str) -> Environment:
      """Cache LRU avec limite de 10 templates."""
      return Environment(loader=FileSystemLoader(template_dir))
  ```
- [ ] 15h30-17h30: Tests scalabilité
  - Test 200 générations successives (vérifier pas de fuite mémoire)
  - Test validation déterministe (0 LLM calls sur 80% cas)
  - Test détection rapide (70% cas sans LLM)

**Livrables**:
- ✅ validation_deterministe.py créé
- ✅ detecter_type_acte_rapide() dans gestionnaire_promesses.py
- ✅ Cache LRU borné dans assembler_acte.py
- ✅ Tests: 200 générations sans fuite mémoire

**Métriques**:
- Coût/gen: $0.10 → $0.03 (validation déterministe + détection rapide)
- Cache hit rate: 40% (template copro réutilisé)
- Mémoire: Stable après 200 générations (pas de fuite)

---

#### JOUR 4-5 (Vendredi 14/02 - Lundi 17/02) — Tom: Validation Tests + Prompt Caching

**JOUR 4 (Vendredi 14/02): Tests & Validation**
- [ ] 09h00-12h00: Suite de tests comparatifs (100 générations)
  - 50 avant optimisations (baseline)
  - 50 après optimisations (smart routing, validation déterministe, cache LRU)
  - Métriques: coût, durée, QA score, erreurs, mémoire
- [ ] 14h00-16h00: Analyse des résultats
  - Tableau comparatif (coût, durée, qualité)
  - Identification régression potentielle
  - Ajustements si QA score baisse >2%
- [ ] 16h00-17h30: Documentation dans OPTIMISATION_COUTS_API.md

**JOUR 5 (Lundi 17/02): Prompt Caching & Clause Suggester**
- [ ] 09h00-12h00: Restructurer prompts pour caching
  ```python
  system_prompt = [
      {
          "type": "text",
          "text": "Tu es un agent spécialisé...",
          "cache_control": {"type": "ephemeral"}  # Cache 5min
      },
      {
          "type": "text",
          "text": f"Catalogue clauses:\n{json.dumps(clauses_catalogue)}",
          "cache_control": {"type": "ephemeral"}
      }
  ]
  ```
- [ ] 14h00-17h00: Implémenter clause-suggester complet
  - Remplacer mock data actuel
  - Logique scoring contextuel (prix, prêt, catégorie)
  - Intégration clauses_catalogue.json (45+ clauses)
  - Tests: 20 contextes

**Livrables**:
- ✅ Rapport comparatif (CSV + analyse)
- ✅ Documentation mise à jour
- ✅ Prompts avec cache_control
- ✅ utils/suggerer_clauses.py complet
- ✅ Tests: 20/20 passing

**Métriques**:
- Coût/gen après optimisations: <$0.02 (objectif atteint)
- QA score: ≥91/100 (maintenu)
- Cache hit rate semaine 1: >20%
- Clause suggester précision: >85%

---

#### JOUR 4-5 — Payos: Migrations Supabase & Sécurité (Partie 1)

**JOUR 4**:
- [ ] 09h00-11h00: Appliquer 3 migrations en attente
  - 20260130_categorie_bien.sql
  - 20260202_feedback_processing.sql
  - 20260210_viager_support.sql
- [ ] 11h00-13h00: Vérifier intégrité données post-migration
- [ ] 14h00-17h00: Créer migration 20260214_fix_security_definer.sql
  - Convertir 4 premières vues SECURITY DEFINER → INVOKER

**JOUR 5**:
- [ ] 09h00-17h00: Continuer fixes sécurité (4 vues restantes)

**Livrables**:
- ✅ 3 migrations appliquées
- ✅ 8/8 vues SECURITY DEFINER corrigées

---

### 📅 SEMAINE 2: Frontend Workflow Complet

#### JOUR 6-7 (Mardi 18/02 - Mercredi 19/02) — Augustin: State Machine + DynamicForm

**JOUR 6 (Mardi 18/02)**:
- [ ] 09h00-12h00: Setup zustand state machine
  ```typescript
  // store/workflowStore.ts
  import create from 'zustand';

  type WorkflowState = 'IDLE' | 'PARSING' | 'COLLECTING' | 'VALIDATING' | 'GENERATING' | 'REVIEW' | 'DONE';

  interface WorkflowStore {
    state: WorkflowState;
    workflowId: string | null;
    currentSection: string;
    sections: Section[];
    progress: number;

    setState: (state: WorkflowState) => void;
    nextSection: () => void;
    saveProgress: () => Promise<void>;
  }

  export const useWorkflow = create<WorkflowStore>((set, get) => ({
    state: 'IDLE',
    // ...
    saveProgress: async () => {
      const { workflowId, sections } = get();
      await fetch(`/workflow/promesse/${workflowId}/submit`, {
        method: 'POST',
        body: JSON.stringify({ sections })
      });
    }
  }));
  ```
- [ ] 14h00-17h00: Créer composant <WorkflowStateMachine />
  - Transitions automatiques
  - Persistance Supabase
  - Recovery si refresh page

**JOUR 7 (Mercredi 19/02)**:
- [ ] 09h00-13h00: Composant <DynamicQuestion />
  ```tsx
  interface QuestionProps {
    question: Question;
    value: any;
    onChange: (value: any) => void;
    onValidate: (valid: boolean) => void;
  }

  export function DynamicQuestion({ question, value, onChange, onValidate }: QuestionProps) {
    const [validationMsg, setValidationMsg] = useState('');

    // Validation temps réel via API
    const validateField = async (val: any) => {
      const res = await fetch('/validation/champ', {
        method: 'POST',
        body: JSON.stringify({
          type_acte: 'promesse_vente',
          chemin: question.variable_path,
          valeur: val
        })
      });
      const data = await res.json();
      setValidationMsg(data.messages[0]?.message || '');
      onValidate(data.valide);
    };

    // Render selon type: texte, choix, date, nombre, oui_non
    // ...
  }
  ```
- [ ] 14h00-17h00: Composant <DynamicForm /> parent
  - Charge questions depuis API
  - Évalue conditions d'affichage
  - Gère progression section par section

**Livrables**:
- ✅ store/workflowStore.ts
- ✅ components/WorkflowStateMachine.tsx
- ✅ components/DynamicQuestion.tsx
- ✅ components/DynamicForm.tsx

---

#### JOUR 6-7 — Tom: Support API pour Augustin

**Tâches**:
- [ ] 09h00-11h00: Tester /workflow/promesse/start end-to-end
- [ ] 11h00-13h00: Tester /workflow/promesse/{id}/submit
- [ ] 14h00-16h00: Créer endpoint SSE /workflow/promesse/{id}/generate-stream
  ```python
  @app.get("/workflow/promesse/{workflow_id}/generate-stream")
  async def generate_stream(workflow_id: str):
      async def event_generator():
          yield f"data: {json.dumps({'etape': 'detection', 'statut': 'en_cours'})}\n\n"
          # ... 7 étapes
          yield f"data: {json.dumps({'etape': 'done', 'fichier_docx': url})}\n\n"

      return StreamingResponse(event_generator(), media_type="text/event-stream")
  ```
- [ ] 16h00-17h30: Documentation API pour Augustin (OpenAPI/Swagger)

**Livrables**:
- ✅ 3 endpoints testés + doc
- ✅ SSE endpoint fonctionnel

---

#### JOUR 8-9 (Jeudi 20/02 - Vendredi 21/02) — Augustin: Workflow UX + SSE Progress

**JOUR 8 (Jeudi 20/02)**:
- [ ] 09h00-12h00: Composant <WorkflowSidebar />
  - 21 sections, check ✅ au fur et à mesure
  - % completion global
  - Click section → jump to (si complétée)
- [ ] 14h00-17h00: Composant <HybridModeToggle />
  - Switch fluide chat ↔ formulaire
  - Chat pre-remplit formulaire
  - Formulaire génère résumé chat

**JOUR 9 (Vendredi 21/02)**:
- [ ] 09h00-13h00: Composant <GenerationProgress /> avec SSE
  ```tsx
  export function GenerationProgress({ workflowId }: { workflowId: string }) {
    const [steps, setSteps] = useState<Step[]>([]);

    useEffect(() => {
      const eventSource = new EventSource(
        `/workflow/promesse/${workflowId}/generate-stream`
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setSteps(prev => [...prev, data]);
      };

      return () => eventSource.close();
    }, [workflowId]);

    return (
      <div className="space-y-2">
        {steps.map(step => (
          <StepIndicator key={step.etape} step={step} />
        ))}
      </div>
    );
  }
  ```
- [ ] 14h00-17h00: Polish animations + loading states

**Livrables**:
- ✅ components/WorkflowSidebar.tsx
- ✅ components/HybridModeToggle.tsx
- ✅ components/GenerationProgress.tsx
- ✅ Animations fluides (<100ms response)

---

#### JOUR 8-9 — Tom: Implémenter post-generation-reviewer

**Tâches**:
- [ ] 09h00-13h00: Créer utils/reviewer_qa.py
  ```python
  from docx import Document

  class PostGenerationReviewer:
      def review(self, docx_path: str, donnees: dict) -> ReviewResult:
          """QA 10 dimensions"""
          doc = Document(docx_path)

          checks = [
              self._check_bookmarks_count(doc, expected=298),
              self._check_quotites_totalisent_100(donnees),
              self._check_prix_coherent(donnees),
              self._check_carrez_present(donnees),
              # ... 6 autres checks
          ]

          score = sum(c.score for c in checks) / len(checks)
          decision = "PASS" if score >= 90 else "WARNING" if score >= 70 else "BLOCKED"

          return ReviewResult(score=score, decision=decision, checks=checks)
  ```
- [ ] 14h00-17h00: Tests sur 20 DOCX générés

**Livrables**:
- ✅ utils/reviewer_qa.py
- ✅ Tests: 20/20 PASS

---

#### JOUR 10 (Lundi 24/02) — Augustin: Document Review + Feedback

**Tâches**:
- [ ] 09h00-12h00: Composant <DocumentReview />
  - Affichage sections Markdown
  - Pas de full DOCX viewer (trop complexe)
  - Bouton download avec QA badge
- [ ] 14h00-17h00: Composant <FeedbackPanel />
  ```tsx
  interface FeedbackPanelProps {
    section: string;
    onSubmit: (feedback: Feedback) => void;
  }

  export function FeedbackPanel({ section, onSubmit }: FeedbackPanelProps) {
    const [type, setType] = useState<'erreur' | 'suggestion' | 'question'>('suggestion');
    const [contenu, setContenu] = useState('');

    const handleSubmit = async () => {
      await fetch('/api/feedback', {
        method: 'POST',
        body: JSON.stringify({ section, type, contenu })
      });
      onSubmit({ section, type, contenu });
    };

    return (
      <div className="bg-white p-4 rounded-lg shadow">
        <select value={type} onChange={e => setType(e.target.value)}>
          <option value="erreur">🔴 Erreur</option>
          <option value="suggestion">🟡 Suggestion</option>
          <option value="question">🔵 Question</option>
        </select>
        <textarea value={contenu} onChange={e => setContenu(e.target.value)} />
        <button onClick={handleSubmit}>Envoyer feedback</button>
      </div>
    );
  }
  ```

**Livrables**:
- ✅ components/DocumentReview.tsx
- ✅ components/FeedbackPanel.tsx

---

#### JOUR 10 — Payos: Sécurité Supabase (Partie 2)

**Tâches**:
- [ ] 09h00-11h00: Activer verify_jwt: true sur Edge Functions
- [ ] 11h00-13h00: Fixer RLS policies auth.uid() → (select auth.uid())
  ```sql
  -- Avant (lent)
  CREATE POLICY "dossiers_etude_policy" ON dossiers
  FOR ALL USING (etude_id = auth.uid());

  -- Après (rapide)
  CREATE POLICY "dossiers_etude_policy" ON dossiers
  FOR ALL USING (etude_id = (select auth.uid()));
  ```
- [ ] 14h00-17h00: Créer 18 index manquants sur FK

**Livrables**:
- ✅ Migration 20260224_fix_rls_performance.sql
- ✅ 0 alertes critiques Supabase Advisor

---

### 📅 SEMAINE 3: Tests, Sécurité & Préparation Pilotes

#### JOUR 11-12 (Mardi 25/02 - Mercredi 26/02) — Tous: Tests E2E Complets

**Objectif**: 300+ tests, 100% passing, coverage >80%

**Tom**:
- [ ] Écrire 50 nouveaux tests backend
  - Tests smart routing modèle
  - Tests cache clauses
  - Tests reviewer QA
  - Tests E2E workflows complets

**Augustin**:
- [ ] Écrire tests frontend (Jest + React Testing Library)
  - Tests composants workflow
  - Tests integration API
  - Tests SSE

**Payos**:
- [ ] CI/CD pipeline GitHub Actions
  ```yaml
  # .github/workflows/test.yml
  name: Tests
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
        - run: pip install -r requirements.txt
        - run: pytest --cov=execution --cov-report=xml
        - run: cd frontend && npm test
  ```

**Livrables**:
- ✅ 300+ tests total
- ✅ Coverage >80%
- ✅ CI/CD actif

---

#### JOUR 13-14 (Jeudi 27/02 - Vendredi 28/02) — Tous: Polish Final & Documentation

**Tom**:
- [ ] Documentation API complète (Swagger/OpenAPI)
- [ ] Guide déploiement Modal
- [ ] Scripts utilitaires pour études (création compte, etc.)

**Augustin**:
- [ ] Polish UX final
  - Animations fluides
  - Messages erreurs clairs
  - Loading states élégants
  - Mobile responsive (tablet minimum)
- [ ] Guide utilisateur notaire (PDF + vidéo)

**Payos**:
- [ ] Monitoring production (Sentry)
- [ ] Alertes Slack
- [ ] Dashboard Grafana/Metabase

**Livrables**:
- ✅ App production-ready
- ✅ Documentation complète
- ✅ Monitoring actif

---

#### JOUR 15 (Lundi 03/03) — Tous: Préparation Démo Pilotes

**Matin (09h-13h)**: Répétition démo
- [ ] 09h00-10h00: Dry-run démo complète (30min)
- [ ] 10h00-11h00: Feedback interne + ajustements
- [ ] 11h00-12h00: 2ème dry-run
- [ ] 12h00-13h00: Finalisation slides + script

**Après-midi (14h-17h)**: Onboarding matériel
- [ ] 14h00-15h00: Créer pack onboarding
  - Guide utilisateur PDF (10 pages)
  - Vidéo tutoriel 5min
  - FAQ (20 questions)
  - Email template premier contact
- [ ] 15h00-16h00: Créer 5 comptes études test
- [ ] 16h00-17h00: Scheduler 5 démos semaine suivante

**Livrables**:
- ✅ Démo 30min rodée
- ✅ Pack onboarding complet
- ✅ 5 études contactées

---

## 3. Sprints 2-4 (6 semaines) — Architecture & Performance

### Sprint 2 (2 semaines) — Architecture & Maintenabilité

**Dates**: 04/03 - 17/03/2026

#### Travaux Prioritaires

**1. Extraire God Classes (1 semaine)**

**Avant** (problème):
```python
# gestionnaire_promesses.py — 1,548 lignes
class GestionnairePromesses:
    def detecter_type(): ...        # Détection
    def valider(): ...               # Validation
    def generer(): ...               # Génération
    def convertir(): ...             # Conversion
    def _sauvegarder_supabase(): ... # Persistance
    # ... 30 autres méthodes
```

**Après** (solution):
```python
# promesse_detector.py — 200 lignes
class PromesseDetector:
    def detecter_categorie_bien(): ...
    def detecter_type(): ...
    def detecter_sous_type(): ...

# promesse_validator.py — 300 lignes
class PromesseValidator:
    def valider(): ...
    def _valider_regle(): ...

# promesse_generator.py — 400 lignes
class PromesseGenerator:
    def generer(): ...
    def _selectionner_template(): ...

# promesse_converter.py — 300 lignes
class PromesseConverter:
    def titre_vers_promesse(): ...
    def promesse_vers_vente(): ...
```

**Bénéfices**:
- ✅ Meilleure testabilité (mock partiel possible)
- ✅ Réutilisabilité (composition > héritage)
- ✅ Maintenance simplifiée (responsabilités claires)

**2. Abstraction Stockage (3 jours)**

**Interface Repository**:
```python
class StorageRepository(ABC):
    @abstractmethod
    def save_promesse(self, data: dict) -> str: ...

    @abstractmethod
    def get_promesse(self, id: str) -> Optional[dict]: ...

# Implémentations
class SupabaseStorage(StorageRepository): ...
class LocalJSONStorage(StorageRepository): ...  # Tests
class PostgreSQLStorage(StorageRepository): ... # Future
```

**Bénéfices**:
- ✅ Tests unitaires 10x plus rapides (pas de Supabase)
- ✅ Possibilité de swap backend
- ✅ Respect du principe d'inversion de dépendances

**3. Type Hints Complets (3 jours)**

**Avant**:
```python
def _convertir_titre_vers_promesse(self, titre, beneficiaires, options):
    ...
```

**Après**:
```python
def _convertir_titre_vers_promesse(
    self,
    titre: Dict[str, Any],
    beneficiaires: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convertit un titre de propriété en données de promesse.

    Raises:
        ValueError: Si titre manque des champs obligatoires
    """
    ...
```

**Bénéfices**:
- ✅ Autocomplétion IDE
- ✅ Détection erreurs avant runtime (mypy)
- ✅ Documentation implicite

#### Livrables Sprint 2

| Livrable | Impact | Tests |
|----------|--------|-------|
| 4 classes spécialisées | LOC max: 1,548 → 400 | 100 tests unitaires |
| StorageRepository | Tests 10x plus rapides | Integration suite |
| Type hints 100% | mypy strict passing | CI/CD validation |

---

### Sprint 3 (2 semaines) — Performance & Innovations

**Dates**: 18/03 - 31/03/2026

#### Travaux Prioritaires

**1. Optimiser Deepcopy (2 jours)**

**Problème**: 57 appels à `copy.deepcopy()`, overhead total ~100ms.

**Solution**: Copie sélective des chemins mutés uniquement.

```python
# ❌ AVANT - Copie tout
donnees_copy = copy.deepcopy(donnees)  # 800+ clés

# ✅ APRÈS - Copie shallow + deep ciblé
donnees_copy = donnees.copy()  # Shallow
if "promettants" in donnees:
    donnees_copy["promettants"] = copy.deepcopy(donnees["promettants"])
```

**Gain**: 10-15% performance globale (5.7s → 5.0s).

**2. Benchmarks Performance (2 jours)**

**pytest-benchmark** avec alertes CI/CD:

```python
def test_pipeline_complet_performance(benchmark):
    result = benchmark(workflow_rapide, "promesse_vente", donnees_test)
    assert benchmark.stats['mean'] < 6.0, "Pipeline trop lent"
```

**CI/CD**: Alerte si régression >10% entre PR et master.

**3. Génération Parallélisée — Agent Teams (1 semaine)**

**Architecture actuelle (séquentielle)**:
```
Validation (50ms) → Détection (20ms) → Assemblage (1500ms) → Export (3500ms)
= 5070ms total
```

**Architecture proposée (parallèle)**:
```
┌─ Cadastre enrichment (500ms) ─┐
├─ Collecte Q&R (prefill 64%)  ─┤
├─ Template audit (conformité)  ─┤ → Orchestrator (Opus)
└─ Schema validation (120ms)   ─┘
         ↓ (max 500ms en parallèle)
    Assemblage (1500ms)
         ↓
┌─ Export DOCX (3500ms) ────────┐
└─ Clause suggester (2000ms)   ─┤ → Parallèle
         ↓
   Post-generation QA (1000ms)
```

**Gain théorique**: 2.5-3x plus rapide (5s → 2s).

**Implémentation**: Opus 4.6 Agent Teams avec orchestrateur intelligent.

#### Livrables Sprint 3

| Livrable | Impact | Métrique |
|----------|--------|----------|
| Deepcopy optimisé | +10-15% performance | 5.7s → 5.0s |
| Benchmarks CI/CD | Monitoring continu | Alerte si >10% regression |
| Agent Teams | 2-3x plus rapide | 5s → 2s |

---

### Sprint 4 (2 semaines) — Fonctionnalités Avancées

**Dates**: 01/04 - 14/04/2026

#### Innovations Fonctionnelles

**1. Support Multi-Langue (2-3 semaines)**

Templates bilingues FR/EN pour transactions internationales.

```jinja2
{% set lang = acte.langue | default('fr') %}

## {{ _('DESIGNATION_DU_BIEN', lang) }}

{{ _('UN_APPARTEMENT_SITUE', lang) }} {{ bien.adresse.adresse }}
```

**Fichiers de traduction** (`locales/en.json`):
```json
{
  "DESIGNATION_DU_BIEN": "PROPERTY DESCRIPTION",
  "UN_APPARTEMENT_SITUE": "An apartment located at"
}
```

**2. Preview Temps Réel (1 semaine)**

Mode "Live Preview" via WebSocket:

```
Frontend (React) → WebSocket → Backend (Modal)
   ↓
   User remplit "prix.montant"
   ↓
   Backend → Assemblage partiel → Markdown preview
   ↓
   Frontend affiche section "PRIX ET PAIEMENT" en temps réel
```

**Bénéfices**:
- ✅ Meilleure UX (feedback immédiat)
- ✅ Détection erreurs avant génération finale
- ✅ Confiance notaire (voit document se construire)

#### Livrables Sprint 4

| Livrable | Impact | Target |
|----------|--------|--------|
| Templates i18n | Marchés internationaux | FR + EN |
| Preview WebSocket | UX premium | Feedback <100ms |

---

## 4. Prochaines Étapes Génération Promesses & Actes

### 4.1 Amélioration Immédiate — Court Terme (1-2 mois)

#### A. Performance Génération

**Objectif**: Passer de 5.7s → 2s par génération

**Actions**:
1. **Optimiser deepcopy** (Jour 1-2)
   - Remplacer 57 appels deepcopy par copie sélective
   - Gain: 10-15% (5.7s → 5.0s)

2. **Paralléliser tâches indépendantes** (Semaine 1-2)
   - Cadastre enrichment + validation en parallèle
   - Export DOCX + clause suggester en parallèle
   - Gain: 40-50% (5.0s → 2.5-3.0s)

3. **Agent Teams Opus 4.6** (Semaine 3-4)
   - Orchestrateur intelligent coordonnant 6 agents
   - Gain théorique: 2.5-3x (5.7s → 2s)

**Métriques**:
- ✅ Durée génération: <2s
- ✅ QA score maintenu: ≥91/100
- ✅ Coût/gen: <$0.01 (optimisations + parallélisation)

#### B. Qualité & Fiabilité

**Objectif**: 0 erreurs en production, QA automatique 100%

**Actions**:
1. **QA Reviewer automatique** (Jour 8-9)
   - 10 dimensions de vérification
   - Score PASS/WARNING/BLOCKED
   - Blocage livraison si score <90

2. **Suggestions clauses intelligentes** (Jour 5)
   - Scoring contextuel (prix, prêt, catégorie, parties)
   - Intégration 45+ clauses catalogue
   - Précision >90%

3. **Validation sémantique avancée** (Sprint 2)
   - Détection incohérences (dates, quotités, prix)
   - Warnings préventifs (conditions suspensives, viager sans certificat médical)
   - Intégration règles métier notariales

**Métriques**:
- ✅ Taux erreurs production: <1%
- ✅ Suggestions clauses adoptées: >30%
- ✅ QA score moyen: >93/100

#### C. Templates — Couverture Exhaustive

**Objectif**: Couvrir les 13 trames anonymisées restantes

**Priorités**:
1. **Donation-partage** (3-4 jours)
   - Template + schéma + questions
   - Sections: réserve héréditaire, rapport donations antérieures
   - Conformité target: >85%

2. **Bail commercial** (3-4 jours)
   - Clauses spécifiques: loyer, charges, destination, durée
   - Conformité target: >85%

3. **Testament** (2-3 jours)
   - Types: olographe, authentique, mystique
   - Clauses: légataires, révocation, exécuteur testamentaire
   - Conformité target: >85%

**Planning**: Intégrer 1 nouveau template par semaine après Sprint 1

**Métriques**:
- ✅ 10/13 templates PROD fin Sprint 2
- ✅ 13/13 templates PROD fin Sprint 4
- ✅ Conformité moyenne: >85%

### 4.2 Amélioration Structurelle — Moyen Terme (2-4 mois)

#### A. Refactoring Architecture

**Objectif**: Maintenabilité long-terme, scalabilité 10x

**Actions Sprint 2**:
1. **Extraire God classes** (Semaine 1)
   - gestionnaire_promesses.py (1,548 lignes) → 4 classes (200-400 lignes)
   - orchestrateur.py (1,470 lignes) → 3 classes
   - Bénéfice: testabilité +300%

2. **Abstraction stockage** (Jours 6-8)
   - Interface StorageRepository
   - Implémentations: Supabase, LocalJSON, PostgreSQL
   - Bénéfice: tests 10x plus rapides

3. **Type hints complets** (Jours 9-11)
   - 40% → 100% couverture
   - Validation mypy en CI/CD
   - Bénéfice: détection erreurs avant runtime

**Métriques**:
- ✅ LOC max fichier: 1,548 → <500
- ✅ Tests unitaires: +100 tests
- ✅ Type hints: 100%

#### B. Monitoring & Observabilité

**Objectif**: Visibilité complète pipeline production

**Actions Sprint 1-2**:
1. **Logging structuré** (Jour 2)
   - 44 print() → logger avec levels
   - Format JSON (timestamp, level, context, trace_id)
   - Intégration Sentry

2. **Métriques temps réel** (Jour 2-3 Payos)
   - Dashboard Grafana: coûts, durée, QA score, erreurs
   - Alertes: coût >$0.05/gen, erreur >10/h, QA <85
   - Retention: 90 jours

3. **Benchmarks automatisés** (Sprint 3)
   - pytest-benchmark dans CI/CD
   - Alerte si régression >10% entre PR et master
   - Historique performance sur 6 mois

**Métriques**:
- ✅ Temps détection erreur: <5min
- ✅ Visibilité 100% sur pipeline
- ✅ Alertes automatiques

#### C. UX Frontend — Workflow Complet

**Objectif**: Notaire autonome de A à Z sans formation

**Actions Sprint 1 (Semaine 2-3)**:
1. **State machine workflow** (Jour 6-7)
   - États: IDLE → PARSING → COLLECTING → VALIDATING → GENERATING → REVIEW → DONE
   - Persistance Supabase (reprendre où on en était)
   - Recovery automatique

2. **Formulaires dynamiques** (Jour 7-9)
   - Rendu depuis questions_promesse_vente.json (97 questions)
   - Conditions d'affichage (skip si non applicable)
   - Validation temps réel par champ
   - Prefill 64% automatique

3. **Mode hybride chat ↔ formulaire** (Jour 8)
   - Toggle fluide entre les 2 modes
   - Chat → détecte entités → pre-remplit formulaire
   - Formulaire → génère résumé → affiche dans chat

4. **Review & feedback inline** (Jour 10)
   - Affichage DOCX section par section
   - Click paragraphe → panel feedback (erreur/suggestion/question)
   - Intégration self-annealing

**Métriques**:
- ✅ Taux completion workflow: >80%
- ✅ Temps moyen: <5min
- ✅ Taux feedback: >20%
- ✅ Drop-off rate: <15%

### 4.3 Innovations Long Terme — Visionnaire (4-6 mois)

#### A. IA Générative Avancée

**Objectif**: Génération contextualisée ultra-précise

**Pistes**:
1. **Fine-tuning modèle notarial**
   - Dataset: 10,000+ actes anonymisés
   - Vocabulaire juridique spécialisé
   - Conformité +5-10%

2. **Détection anomalies sémantiques**
   - Prix incohérent vs marché local
   - Quotités non conformes Code Civil
   - Clauses contradictoires

3. **Génération clauses sur-mesure**
   - Au-delà du catalogue: création dynamique
   - Adaptation situation unique client
   - Validation avocat/notaire

**Métriques**:
- ✅ Conformité: 85% → 95%
- ✅ Détection anomalies: >98%
- ✅ Satisfaction clauses: >4.5/5

#### B. Intégrations Écosystème Notarial

**Objectif**: Hub central étude notariale

**Intégrations**:
1. **APIs métiers**
   - CRIDON (doctrine notariale)
   - Fichier Central des Dernières Volontés
   - Registre National des Crédits aux Particuliers
   - BODACC (vérifications entreprises)

2. **Connecteurs outils**
   - Genapi (comptabilité étude)
   - Fiducial (facturation)
   - Real (répertoire actes)

3. **Blockchain notariale**
   - Horodatage actes
   - Certificats authenticité
   - Traçabilité complète

**Métriques**:
- ✅ APIs intégrées: 5+
- ✅ Réduction saisie manuelle: -60%
- ✅ Conformité réglementaire: 100%

#### C. Scalabilité Internationale

**Objectif**: Expansion marchés européens

**Actions**:
1. **Multi-langue** (Sprint 4)
   - Templates bilingues FR/EN
   - Traduction automatique clauses
   - Adaptation vocabulaire juridique local

2. **Multi-juridictions**
   - Droit français, belge, suisse, luxembourgeois
   - Adaptation règles locales (quotités, fiscalité)
   - Conformité multi-réglementaire

3. **Multi-devises**
   - Support EUR, CHF, USD, GBP
   - Conversion automatique
   - Historique taux change

**Métriques**:
- ✅ Marchés: 4 pays (FR, BE, CH, LU)
- ✅ Langues: 3 (FR, EN, NL)
- ✅ Conformité: >90% par juridiction

### 4.4 Priorisation & Roadmap

```
COURT TERME (1-2 mois) — Sprint 1-2
┌─────────────────────────────────┐
│ 1. Performance (5.7s → 2s)      │ 🔴 CRITIQUE
│ 2. QA automatique               │ 🔴 CRITIQUE
│ 3. Frontend workflow complet    │ 🔴 CRITIQUE
│ 4. Sécurité Supabase            │ 🔴 CRITIQUE
│ 5. Logging structuré            │ 🟡 IMPORTANT
│ 6. Suggestions clauses          │ 🟡 IMPORTANT
└─────────────────────────────────┘

MOYEN TERME (2-4 mois) — Sprint 3-4
┌─────────────────────────────────┐
│ 7. Refactoring God classes      │ 🟡 IMPORTANT
│ 8. Abstraction stockage         │ 🟡 IMPORTANT
│ 9. Type hints 100%              │ 🟢 NICE-TO-HAVE
│ 10. Templates additionnels (3)  │ 🟡 IMPORTANT
│ 11. Multi-langue (FR/EN)        │ 🟢 NICE-TO-HAVE
│ 12. Preview temps réel          │ 🟢 NICE-TO-HAVE
└─────────────────────────────────┘

LONG TERME (4-6 mois) — Sprint 5-8
┌─────────────────────────────────┐
│ 13. Fine-tuning modèle          │ 🟢 VISIONNAIRE
│ 14. Intégrations APIs métiers   │ 🟡 IMPORTANT
│ 15. Multi-juridictions          │ 🟢 VISIONNAIRE
│ 16. Blockchain notariale        │ 🟢 VISIONNAIRE
└─────────────────────────────────┘
```

---

## 5. Métriques & Risques

### 5.1 Métriques de Succès Globales

#### Évolution sur 4 Sprints

| Métrique | Baseline (v2.0.0) | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 |
|----------|-------------------|----------|----------|----------|----------|
| **Coût/gen** | $0.26 | $0.02 | $0.02 | $0.01 | $0.01 |
| **Durée gen** | 8s | <10s | <10s | 2s | 2s |
| **Exception handlers** | 30 | 0 | 0 | 0 | 0 |
| **LOC max fichier** | 1,548 | 1,548 | 400 | 400 | 400 |
| **Tests** | 257 | 300+ | 350+ | 400+ | 450+ |
| **Type hints** | 40% | 40% | 100% | 100% | 100% |
| **Langues** | FR | FR | FR | FR | FR+EN |
| **Preview** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Fuite mémoire** | ✅ | ❌ | ❌ | ❌ | ❌ |

#### Métriques Business (6 Mois)

| KPI | Fin Fév | Fin Mars | Fin Avril | Cible 6 Mois |
|-----|---------|----------|-----------|--------------|
| **Études pilotes** | 5 | 10 | 20 | 50 |
| **Actes générés** | 50 | 200 | 500 | 2000 |
| **Coût API/mois** | $17 | $34 | $85 | $340 |
| **MRR** | 0€ | 0€ | 5k€ | 25k€ |
| **Satisfaction** | 4/5 | 4.2/5 | 4.5/5 | 4.5/5 |
| **Temps/acte** | 5min | 4min | 3min | 2min |

### 5.2 Risques & Mitigations

#### Risques Techniques Sprint 1

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Optimisations dégradent qualité** | Moyenne | Élevé | Tests comparatifs jour 4, rollback si QA <89 |
| **Exception handlers cassent comportement** | Faible | Élevé | Tests unitaires + E2E complets avant merge |
| **Logging trop verbeux dégrade perf** | Faible | Moyen | Level INFO par défaut, DEBUG sur demande |
| **Cache LRU trop petit (10 templates)** | Faible | Faible | Monitorer hit rate, augmenter si <40% |
| **SSE ne fonctionne pas cross-browser** | Faible | Moyen | Fallback polling si EventSource unavailable |
| **Migrations Supabase cassent prod** | Faible | Élevé | Backup avant migration, test sur staging |
| **Sprint 1 surchargé** | Moyenne | Élevé | Jour 14 buffer (polish), sacrifiable si retard |

#### Risques Produit

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **UX trop complexe pour notaires** | Moyenne | Élevé | User testing jour 14, simplifier si besoin |
| **Études pilotes refusent** | Faible | Élevé | Offre gratuite 3 mois, support dédié |
| **Bugs bloquants découverts tard** | Moyenne | Moyen | Tests E2E jour 11-12, bug bash jour 13 |

#### Risques Architecturaux Sprint 2-4

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Refactoring God classes casse prod** | Faible | Élevé | Tests 100% coverage + staging validation |
| **Agent Teams trop complexe** | Moyenne | Moyen | POC semaine 1 Sprint 3, pivot si échec |
| **Traduction EN juridique incorrecte** | Moyenne | Élevé | Validation avocat UK + notaire bilingue |

### 5.3 Rituels Équipe

#### Daily Standup (9h30, 15min)
- **Format**: Hier / Aujourd'hui / Blockers
- **Channel**: Slack #sprint-feb-2026
- **Record**: Google Doc partagé

#### Mid-Sprint Review (Jour 8, 17h, 1h)
- **Objectif**: Démo progrès semaine 1
- **Participants**: Tom, Augustin, Payos
- **Agenda**:
  - Démo optimisations coûts (Tom)
  - Démo monitoring (Payos)
  - Démo workflow WIP (Augustin)
  - Ajustements semaine 2

#### Sprint Review (Jour 15, 17h, 1h)
- **Objectif**: Démo complète + retro
- **Participants**: Équipe + stakeholders
- **Agenda**:
  - Démo app complète (30min)
  - Métriques sprint (15min)
  - Retro: Keep/Drop/Try (15min)

### 5.4 Définition de "Done"

#### Pour chaque tâche:
- [ ] Code écrit + tests
- [ ] Tests passent localement
- [ ] Code review (si applicable)
- [ ] Documentation mise à jour
- [ ] Déployé sur staging
- [ ] Validation QA

#### Pour le sprint:
- [ ] Toutes tâches P0 complétées
- [ ] 300+ tests passing
- [ ] 0 alertes critiques Supabase
- [ ] Démo 30min fonctionnelle
- [ ] 5 études contactées
- [ ] Documentation complète
- [ ] Monitoring production actif

---

## 📚 Documentation Référence

| Document | Usage |
|----------|-------|
| **ROADMAP_MASTER_FEVRIER_2026.md** | **CE DOCUMENT** - Consolidation complète |
| [AUDIT_GENERAL_FEVRIER_2026.md](AUDIT_GENERAL_FEVRIER_2026.md) | État système (templates, API, BDD, Agent Teams) |
| [RECOMMANDATIONS_AMELIORATIONS_2026.md](RECOMMANDATIONS_AMELIORATIONS_2026.md) | 13 recommandations techniques détaillées |
| [OPTIMISATION_COUTS_API.md](OPTIMISATION_COUTS_API.md) | Stratégies réduction coûts API |
| [CLAUDE.md](../CLAUDE.md) | Architecture 3 couches + instructions agents |

---

## ✅ Checklist Démarrage Sprint 1

**Avant Jour 1**:
- [ ] Créer Jira board
- [ ] Créer Slack channel #sprint-feb-2026
- [ ] Kick-off meeting (1h): présenter plan
- [ ] Chaque dev crée sa branche: `sprint/feb-2026-{nom}`
- [ ] Setup staging environment

**Jour 1 Matin**:
- [ ] Standup 9h30
- [ ] Chacun confirme ses tâches jour 1
- [ ] Blockers identifiés

---

*Document créé le 11/02/2026 - Roadmap Master consolidant tous les plans sprint*
*Sources: AUDIT + SPRINT_PLAN + SPRINT_INTEGRATION + SPRINT_ROADMAP + PROCHAINES_ETAPES + RECOMMANDATIONS*
