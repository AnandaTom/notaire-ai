# Prochaines Étapes - Notomai Février 2026

> **Roadmap complète** post-implémentation Opus 4.6 Agent Teams

**Date**: 2026-02-11 | **Version**: 2.0.0 | **Équipe**: Tom (Backend), Augustin (Frontend), Payos (Infra)

---

## 🎯 Vision Globale (3 Mois)

```
FÉVRIER 2026         MARS 2026           AVRIL 2026
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Optimisation │ →  │ Frontend     │ →  │ Production   │
│ • Agents ✅   │    │ • Chatbot    │    │ • 5 études   │
│ • Coûts -93% │    │ • Workflow   │    │ • 100 actes  │
│ • API ✅      │    │ • Dashboard  │    │ • Feedback   │
└──────────────┘    └──────────────┘    └──────────────┘
```

**Objectifs Clés**:
1. **Tech**: Agents Opus 4.6 + Optimisations coûts → -93% API costs
2. **Product**: Frontend complet pour notaires (chatbot + workflow + dashboard)
3. **Business**: 5 études pilotes, 100 actes générés, feedback loop actif

---

## 📅 PHASE 1: Optimisations & Stabilisation (1-2 semaines)

**Responsables**: Tom + Payos | **Durée**: 6-10 jours

### Sprint 1A: Optimisations Coûts API (Jour 1-3)

**Objectif**: Réduire coûts de $260 → $17/mois (-93%)

**Tom**:
- [ ] **Jour 1**: Smart Opus usage
  - Implémenter `_choisir_modele()` dans orchestrateur
  - Règle: confiance >80% → Sonnet, <80% → Opus
  - Tests: 100 générations, vérifier 60% Sonnet
  - **Livrable**: `orchestrateur.py` updated

- [ ] **Jour 2**: Output optimization + Règles déterministes
  - Ajouter `max_tokens` à tous appels API
  - Forcer `response_format="json_object"`
  - Créer `detecter_type_acte_rapide()` (regex)
  - Remplacer schema-validator LLM par `jsonschema`
  - **Livrable**: -68% coûts

- [ ] **Jour 3**: Tests & Validation
  - 100 générations test (comparaison qualité avant/après)
  - Dashboard coûts Supabase
  - **Livrable**: Rapport coûts réels

**Payos**:
- [ ] **Jour 1-3**: Infrastructure monitoring
  - Table Supabase `api_costs_tracking`
  - Vue `v_daily_costs`
  - Alertes si coûts >$0.05/gen
  - **Livrable**: Dashboard coûts temps réel

**Métriques Succès**:
- ✅ Coût/gen: $0.26 → <$0.08
- ✅ Qualité: QA score maintenu ≥91/100
- ✅ Rapidité: <10s génération (maintenu)

**Documentation**: [docs/OPTIMISATION_COUTS_API.md](OPTIMISATION_COUTS_API.md)

---

### Sprint 1B: Prompt Caching & Cache Clauses (Jour 4-6)

**Tom**:
- [ ] **Jour 4**: Restructurer prompts pour caching
  - System prompts avec `cache_control: ephemeral`
  - Catalogue clauses en bloc cachable
  - **Livrable**: Prompts optimisés cache

- [ ] **Jour 5**: Implémenter clause cache
  - Table Supabase `clauses_suggestions_cache`
  - TTL 30 jours
  - Cache key = hash(type_acte + prix_range + pret + categorie)
  - **Livrable**: Cache actif

- [ ] **Jour 6**: Monitoring cache hit rates
  - Dashboard: prompt cache hit rate (target >70%)
  - Dashboard: clause cache hit rate (target >50% après 1 mois)
  - **Livrable**: Monitoring cache

**Métriques Succès**:
- ✅ Coût/gen final: <$0.02
- ✅ Cache hit rate semaine 1: >30%
- ✅ Cache hit rate mois 1: >60%

---

### Sprint 1C: Agents - Implémentations Manquantes (Jour 7-10)

**Tom**:
- [ ] **Jour 7-8**: Implémenter `clause-suggester` complet
  - Actuellement mock data
  - Vraie logique: scoring contextuel 45+ clauses
  - Intégration `clauses_catalogue.json`
  - Tests: 20 contextes différents
  - **Livrable**: `utils/suggerer_clauses.py`

- [ ] **Jour 9-10**: Implémenter `post-generation-reviewer` complet
  - Actuellement mock data
  - 10 dimensions QA (bookmarks, quotités, prix, Carrez, etc.)
  - Python-docx pour extraction bookmarks
  - Décision PASS/WARNING/BLOCKED
  - **Livrable**: `utils/reviewer_qa.py`

**Payos**:
- [ ] **Jour 7-10**: Tests E2E génération parallèle
  - Pipeline complet: demande NL → DOCX
  - 50 actes test (promesses + ventes)
  - Comparaison parallel vs sequential
  - Validation speedup réel 2.5-3x
  - **Livrable**: Rapport benchmark

**Métriques Succès**:
- ✅ Clause suggester: précision >90%
- ✅ QA reviewer: détection erreurs >95%
- ✅ Speedup réel: ≥2.5x parallel vs sequential

---

## 📅 PHASE 2: Frontend Complet (3-4 semaines)

**Responsable**: Augustin | **Support**: Tom (API), Payos (Déploiement)

### Sprint 2A: Intégration Agents dans Chatbot (Semaine 1)

**Augustin**:
- [ ] **Intégrer endpoint `/agents/orchestrate`**
  - Remplacer appel actuel par nouvel endpoint
  - Afficher progression agents en temps réel
  - Card par agent: nom, status (✅/⏳/❌), durée
  - **Composant**: `<AgentsProgress />` dans `ChatArea.tsx`

- [ ] **Afficher speedup & QA score**
  - Badge "2.6x plus rapide que mode classique"
  - Score QA: 94/100 avec pastille couleur (vert/orange/rouge)
  - **Composant**: `<GenerationSummary />`

- [ ] **Afficher suggestions clauses**
  - Section expandable "3 clauses suggérées"
  - 🔴 CRITIQUES / 🟡 RECOMMANDÉES / 🟢 OPTIONNELLES
  - Clic → détails (justification + art. Code Civil)
  - **Composant**: `<ClauseSuggestions />`

**Tom** (Support):
- [ ] Endpoint SSE `/agents/orchestrate-stream` (progression temps réel)
- [ ] Documentation API pour Augustin

**Métriques Succès**:
- ✅ UX fluide: affichage progression <100ms
- ✅ Taux adoption clauses: >30% cliquées
- ✅ Feedback notaires: ≥4/5

---

### Sprint 2B: Workflow Multi-Étapes (Semaine 2-3)

**Augustin**:
- [ ] **State machine workflow** (zustand)
  - États: IDLE → PARSING → COLLECTING → VALIDATING → GENERATING → REVIEW → DONE
  - Transitions gérées automatiquement
  - Persistance état dans Supabase (reprendre où on en était)
  - **Composant**: `<WorkflowStateMachine />`

- [ ] **Formulaires dynamiques Q&R**
  - Render depuis `questions_promesse_vente.json` (97 questions, 21 sections)
  - Conditions d'affichage (skip si non applicable)
  - Validation temps réel: `POST /validation/champ`
  - Prefill 64% automatique
  - **Composant**: `<DynamicForm />` + `<Question />`

- [ ] **Progress sidebar**
  - 21 sections, check ✅ au fur et à mesure
  - % completion global
  - Click section → jump to
  - **Composant**: `<WorkflowSidebar />`

- [ ] **Mode hybride chat ↔ formulaire**
  - Toggle fluide entre les 2 modes
  - Chat → détecte entités → pre-remplit formulaire
  - Formulaire → génère résumé → affiche dans chat
  - **Composant**: `<HybridModeToggle />`

**Tom** (Support):
- [ ] API `/workflow/promesse/start` (déjà existe)
- [ ] API `/workflow/promesse/{id}/submit`
- [ ] API `/workflow/promesse/{id}/status`

**Métriques Succès**:
- ✅ Taux completion workflow: >80%
- ✅ Temps moyen complétion: <5 min
- ✅ Drop-off rate: <15%

---

### Sprint 2C: Review Document & Feedback (Semaine 4)

**Augustin**:
- [ ] **Document review composant**
  - Affichage DOCX généré section par section
  - Pas de full DOCX viewer (complexe), juste sections Markdown
  - **Composant**: `<DocumentReview />`

- [ ] **Feedback inline**
  - Click paragraphe → ouvrir panel feedback
  - Types: Erreur / Suggestion / Question
  - Envoi: `POST /api/feedback`
  - **Composant**: `<FeedbackPanel />`

- [ ] **Téléchargement DOCX**
  - Bouton "Télécharger" avec QA badge
  - Si QA < 90 → warning "Document nécessite révision"
  - Tracking downloads Supabase
  - **Composant**: `<DownloadButton />`

**Tom** (Support):
- [ ] Endpoint `/files/{filename}` download (déjà existe)
- [ ] Logs downloads dans Supabase

**Métriques Succès**:
- ✅ Taux feedback: >20% actes
- ✅ Satisfaction download: >90%

---

## 📅 PHASE 3: Production & Pilotes (4-6 semaines)

**Responsables**: Toute l'équipe | **Durée**: 1-1.5 mois

### Sprint 3A: Préparation Production (Semaine 1)

**Payos**:
- [ ] **Fixer alertes Supabase critiques**
  - 8 vues SECURITY DEFINER → INVOKER ou filtres `WHERE etude_id`
  - 18 FK non indexées → créer index
  - RLS initplan: `auth.uid()` → `(select auth.uid())`
  - Edge Functions: activer `verify_jwt: true`
  - **Livrable**: Supabase sécurisé production

- [ ] **CI/CD Pipeline**
  - GitHub Actions: tests automatiques sur PR
  - Deploy auto Modal si tests pass
  - **Livrable**: `.github/workflows/deploy.yml`

- [ ] **Monitoring production**
  - Sentry pour erreurs frontend/backend
  - Logs structurés (JSON)
  - Alertes Slack si errors >10/h
  - **Livrable**: Monitoring actif

**Tom**:
- [ ] **Tests automatisés complets**
  - 257 tests actuels → 300+ tests
  - Coverage: >80%
  - Tests E2E: 10 workflows complets
  - **Livrable**: `pytest` all green

**Augustin**:
- [ ] **Polish UX final**
  - Animations fluides
  - Messages erreurs clairs
  - Loading states élégants
  - Mobile responsive (tablet minimum)
  - **Livrable**: Frontend production-ready

**Métriques Succès**:
- ✅ Tests: 100% pass
- ✅ Security: 0 alertes critiques Supabase
- ✅ Performance: Lighthouse score >85

---

### Sprint 3B: Onboarding Pilotes (Semaine 2-3)

**Objectif**: 5 études pilotes

**Toute l'équipe**:
- [ ] **Sélection 5 études**
  - Critères: volume moyen (10-20 actes/mois), early adopters, diversité géographique
  - Contacter via réseau notaires
  - **Livrable**: 5 études signées

- [ ] **Formation notaires** (1h par étude)
  - Démo produit
  - Création compte
  - Génération 1er acte guidé
  - Q&A
  - **Livrable**: 5 sessions formation

- [ ] **Documentation notaires**
  - Guide utilisateur PDF
  - FAQs
  - Vidéo tutoriel 5min
  - **Livrable**: Pack onboarding

**Métriques Succès**:
- ✅ 5 études activées
- ✅ Chaque étude génère ≥1 acte en semaine 1

---

### Sprint 3C: Monitoring & Itération (Semaine 4-6)

**Objectif**: 100 actes générés, feedback loop actif

**Toute l'équipe**:
- [ ] **Support notaires quotidien**
  - Slack channel dédié par étude
  - Réponse <2h questions
  - Bug fixes prioritaires <24h
  - **Livrable**: Support réactif

- [ ] **Collecte feedback structurée**
  - Survey après chaque acte: 5 questions
  - Call hebdo avec chaque étude
  - Tracker: bugs, feature requests, satisfactions
  - **Livrable**: Feedback dashboard

- [ ] **Itérations rapides**
  - Deploy fixes/features 2x/semaine
  - A/B testing si nécessaire
  - **Livrable**: 10+ itérations

**Métriques Succès**:
- ✅ 100 actes générés en 6 semaines
- ✅ Satisfaction moyenne: ≥4/5
- ✅ Taux retention: ≥80% (études actives après 1 mois)
- ✅ NPS: ≥40

---

## 📅 PHASE 4: Scaling & Monétisation (Avril-Mai 2026)

**Objectifs**: 50 études, pricing établi, profitabilité

### Sprint 4A: Scaling Infrastructure

**Payos**:
- [ ] Auto-scaling Modal (1 → 10 containers)
- [ ] CDN pour DOCX (CloudFlare)
- [ ] Database read replicas Supabase
- [ ] Rate limiting avancé (par étude)

**Métriques**:
- ✅ Supporte 50 études concurrentes
- ✅ Latence P95 <5s

---

### Sprint 4B: Pricing & Business Model

**Tom + Business**:
- [ ] **Modèles de pricing**
  1. Freemium: 10 actes/mois gratuit
  2. Pro: 50€/mois, actes illimités
  3. Enterprise: 500€/mois, white-label + support dédié

- [ ] **Implémentation billing**
  - Stripe integration
  - Usage tracking Supabase
  - Invoicing automatique

**Métriques**:
- ✅ 10 études payantes mois 1
- ✅ MRR: 5000€

---

### Sprint 4C: Features Avancées

**Augustin + Tom**:
- [ ] **Conversion Promesse → Vente**
  - Bouton "Générer vente depuis promesse"
  - Conservation 80% données
  - **Impact**: 2x actes par dossier

- [ ] **Templates additionnels**
  - Donation-partage
  - Testament
  - Bail commercial
  - **Impact**: Elargir marché

- [ ] **Analytics dashboard étude**
  - Temps moyen par acte
  - Répartition types actes
  - Économies vs méthode manuelle
  - **Impact**: Retention + upsell

---

## 🎯 Métriques Globales (6 Mois)

| KPI | Fin Fév | Fin Mars | Fin Avril | Cible 6 Mois |
|-----|---------|----------|-----------|--------------|
| **Études pilotes** | 5 | 10 | 20 | 50 |
| **Actes générés** | 50 | 200 | 500 | 2000 |
| **Coût API/mois** | $17 | $34 | $85 | $340 |
| **MRR** | 0€ | 0€ | 5k€ | 25k€ |
| **Satisfaction** | 4/5 | 4.2/5 | 4.5/5 | 4.5/5 |
| **Temps/acte** | 5min | 4min | 3min | 2min |

---

## 🚦 Priorisation & Focus

### 🔴 CRITIQUE (Blocker si pas fait)

1. ✅ Optimisations coûts API (-93%)
2. ✅ Agents implémentations complètes
3. ⏳ Frontend workflow multi-étapes
4. ⏳ Sécurité Supabase (8 fixes)
5. ⏳ Tests E2E complets

### 🟡 IMPORTANT (Nécessaire pour pilotes)

6. ⏳ Document review + feedback
7. ⏳ Onboarding 5 études
8. ⏳ Support réactif <2h
9. ⏳ Monitoring production

### 🟢 NICE-TO-HAVE (Peut attendre post-pilotes)

10. ⏸️ Templates additionnels
11. ⏸️ Analytics dashboard étude
12. ⏸️ Mobile app
13. ⏸️ White-label enterprise

---

## 🎓 Ressources & Documentation

**Technique**:
- Architecture: [CLAUDE.md](../CLAUDE.md)
- Agents: [directives/agents_opus_46.md](../directives/agents_opus_46.md)
- Optimisations: [OPTIMISATION_COUTS_API.md](OPTIMISATION_COUTS_API.md)
- Audit: [AUDIT_GENERAL_FEVRIER_2026.md](AUDIT_GENERAL_FEVRIER_2026.md)

**Workflow**:
- Notaire: [directives/workflow_notaire.md](../directives/workflow_notaire.md)
- Skills: [SKILLS_AGENTS_GUIDE.md](SKILLS_AGENTS_GUIDE.md)

**API**:
- Endpoints: [api/agents.py](../api/agents.py)
- Main: [api/main.py](../api/main.py)

---

## 🤝 Responsabilités Équipe

### Tom (Backend & Agents)
- Optimisations coûts API
- Implémentations agents manquantes
- Tests E2E
- Support API pour Augustin

### Augustin (Frontend)
- Workflow multi-étapes
- Formulaires dynamiques
- Document review
- UX polish

### Payos (Infrastructure & DevOps)
- Sécurité Supabase
- CI/CD pipeline
- Monitoring production
- Scaling infrastructure

---

## 📞 Points d'Équipe

**Daily standups** (15min, 9h30):
- Hier: réalisé
- Aujourd'hui: plan
- Blockers

**Weekly review** (1h, vendredi 17h):
- Métriques semaine
- Démos features
- Retro: keep/drop/try

**Monthly planning** (2h, 1er du mois):
- OKRs mois prochain
- Roadmap ajustements
- Ressources besoins

---

*Document créé le 11/02/2026 - Roadmap vivante, mise à jour hebdomadaire*
