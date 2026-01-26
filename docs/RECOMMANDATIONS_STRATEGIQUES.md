# Recommandations Stratégiques - Notomai Agent

> Document généré le 26 janvier 2026 - Version 1.0
> Objectif : Créer un agent de génération d'actes notariaux EXCELLENT

---

## Table des Matières

1. [Résumé Exécutif](#résumé-exécutif)
2. [État Actuel](#état-actuel)
3. [Améliorations Prioritaires](#améliorations-prioritaires)
4. [Améliorations Templates](#améliorations-templates)
5. [Améliorations Agent Autonome](#améliorations-agent-autonome)
6. [Améliorations Processus](#améliorations-processus)
7. [Améliorations Performance](#améliorations-performance)
8. [Feuille de Route](#feuille-de-route)

---

## Résumé Exécutif

### Forces du Système Actuel

| Composant | Score | Points Forts |
|-----------|-------|--------------|
| Architecture 3 couches | 9/10 | Séparation claire des responsabilités |
| Documentation | 8/10 | 22 directives complètes |
| Templates Vente | 8.5/10 | 85.1% conformité, PROD |
| Agent Autonome | 7/10 | NL parsing fonctionnel |
| Pipeline Performance | 8/10 | ~2.3s génération complète |

### Faiblesses Critiques

| Problème | Impact | Priorité |
|----------|--------|----------|
| Template Promesse incomplet (60.9%) | Bloque production | P0 |
| Agent sans validation intégrée | Erreurs silencieuses | P1 |
| Pas de support multi-parties | Limite cas réels | P1 |
| Pas de dialogue multi-tour | UX limitée | P2 |

---

## État Actuel

### Conformité Templates

```
┌────────────────────────────────────────────────────────────────┐
│  Template                    │ Conformité │ Statut            │
├────────────────────────────────────────────────────────────────┤
│  Règlement copropriété       │   85.5%    │ ✅ PRODUCTION     │
│  Modificatif EDD             │   91.7%    │ ✅ PRODUCTION     │
│  Acte de Vente               │   85.1%    │ ✅ PRODUCTION     │
│  Promesse de Vente           │   60.9%    │ ❌ DÉVELOPPEMENT  │
└────────────────────────────────────────────────────────────────┘
```

### Lacune Majeure : Promesse de Vente

Le template `promesse_vente_lots_copropriete.md` :
- **1522 lignes** actuellement
- **MANQUE** : `{% include 'sections/partie_developpee.md' %}`
- **RÉSULTAT** : Documents générés incomplets (~60% du contenu)

### Capacités Agent

```
┌─────────────────────────────────────────────────────────────────┐
│  Fonctionnalité              │ Implémenté │ Qualité           │
├─────────────────────────────────────────────────────────────────┤
│  Parsing langage naturel     │    ✅      │ Bon (regex)       │
│  Détection d'intention       │    ✅      │ Bon (8 types)     │
│  Extraction entités          │    ✅      │ Moyen (simple)    │
│  Validation données          │    ❌      │ Non intégré       │
│  Multi-parties (A & B → C)   │    ❌      │ Non supporté      │
│  Dialogue multi-tour         │    ❌      │ Stateless         │
│  Apprentissage corrections   │    ⚠️      │ Logging seul      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Améliorations Prioritaires

### P0 : Compléter le Template Promesse (CRITIQUE)

**Problème** : Le template promesse ne génère que 60% du document nécessaire.

**Solution** :
```markdown
# Avant la section "DONT ACTE" (ligne ~1517), ajouter :

# PARTIE DÉVELOPPÉE

{% include 'sections/partie_developpee_promesse.md' %}
```

**Fichier à créer** : `sections/partie_developpee_promesse.md`
- Adapter la partie développée pour les spécificités promesse
- Conditions suspensives (prêt, vente préalable, etc.)
- Délai de réitération
- Indemnité d'immobilisation
- Faculté de substitution

**Impact** : Template passe de 60.9% à ~85%+ conformité

### P1 : Intégrer Validation dans l'Agent

**Problème** : L'agent parse la demande mais ne valide pas les données.

**Solution** dans `agent_autonome.py` :

```python
def executer(self, demande: str) -> ResultatAgent:
    # 1. Parser
    analyse = self.parseur.analyser(demande)

    # 2. NOUVEAU: Valider avant génération
    donnees = self._construire_donnees(analyse)
    validation = self._valider_donnees(donnees, analyse.type_acte)

    if not validation.valide:
        return ResultatAgent(
            succes=False,
            message=f"Données incomplètes : {', '.join(validation.champs_manquants)}",
            suggestions=validation.suggestions
        )

    # 3. Générer seulement si valide
    return self._generer_acte(analyse, donnees)
```

**Impact** : Évite les erreurs silencieuses, améliore UX

### P1 : Support Multi-Parties

**Problème** : "Martin & Pierre → Dupont & Thomas" ne fonctionne pas.

**Solution** dans `ParseurDemandeNL` :

```python
# Nouveau pattern pour multi-parties
PATTERN_FLECHE_MULTI = re.compile(
    r'(?P<vendeurs>[\w\s]+(?:\s*(?:&|et)\s*[\w\s]+)*)\s*[→->]+\s*(?P<acquereurs>[\w\s]+(?:\s*(?:&|et)\s*[\w\s]+)*)',
    re.IGNORECASE
)

def _extraire_parties_multiples(self, texte: str) -> Tuple[List[Dict], List[Dict]]:
    """Extrait plusieurs vendeurs et acquéreurs."""
    match = self.PATTERN_FLECHE_MULTI.search(texte)
    if not match:
        return [], []

    vendeurs = self._parser_liste_noms(match.group('vendeurs'))
    acquereurs = self._parser_liste_noms(match.group('acquereurs'))

    return vendeurs, acquereurs
```

**Impact** : Gère 80%+ des cas réels (couples, indivisions)

---

## Améliorations Templates

### 1. Créer `partie_developpee_promesse.md`

Structure recommandée :

```markdown
{# ============================================================================
   PARTIE DÉVELOPPÉE - PROMESSE DE VENTE
   Sections spécifiques aux promesses unilatérales de vente
   ============================================================================ #}

### CONDITIONS SUSPENSIVES

{% if conditions_suspensives %}

#### Condition suspensive de prêt
{% if conditions_suspensives.pret and conditions_suspensives.pret.applicable %}
La réalisation de la présente promesse est subordonnée à l'obtention par le
**BÉNÉFICIAIRE** d'un ou plusieurs prêts...
[contenu complet]
{% endif %}

#### Condition suspensive de vente préalable
{% if conditions_suspensives.vente_prealable %}
[contenu]
{% endif %}

{% endif %}

### DÉLAI DE RÉALISATION

La présente promesse est consentie pour une durée de
**{{ delai_realisation.duree | default('QUATRE') }} mois** à compter...

### INDEMNITÉ D'IMMOBILISATION

Le **BÉNÉFICIAIRE** verse au **PROMETTANT** une indemnité d'immobilisation de
**{{ indemnite_immobilisation.montant_lettres }}** soit
**{{ indemnite_immobilisation.pourcentage | default(5) }}%** du prix de vente...

### FACULTÉ DE SUBSTITUTION

{% if faculte_substitution.autorisee %}
Le **BÉNÉFICIAIRE** peut se substituer toute personne physique ou morale...
{% endif %}

{# Inclure les sections communes #}
{% include 'sections/partie_developpee.md' %}
```

### 2. Améliorer Structure partie_developpee.md

Ajouter des guards conditionnels plus explicites :

```markdown
{# Section DIAGNOSTICS - toujours présente #}
### DIAGNOSTICS TECHNIQUES

{% if diagnostics %}
{% include 'sections/section_diagnostics_complets.md' %}
{% else %}
*(Diagnostics à compléter)*
{% endif %}

{# Section COPROPRIÉTÉ - conditionnelle #}
{% if copropriete %}
### COPROPRIÉTÉ
{% include 'sections/section_copropriete_reglementations.md' %}
{% endif %}
```

### 3. Standardiser les Variables

Créer un fichier de référence des variables obligatoires :

| Variable | Promesse | Vente | Type | Obligatoire |
|----------|----------|-------|------|-------------|
| `promettants` / `vendeurs` | promettants | vendeurs | List[Personne] | Oui |
| `beneficiaires` / `acquereurs` | beneficiaires | acquereurs | List[Personne] | Oui |
| `bien` | Oui | Oui | Dict | Oui |
| `prix` | Oui | Oui | Dict | Oui |
| `conditions_suspensives` | Oui | Non | Dict | Promesse |
| `indemnite_immobilisation` | Oui | Non | Dict | Promesse |

---

## Améliorations Agent Autonome

### 1. Score de Confiance Détaillé

Remplacer le score unique par un breakdown :

```python
@dataclass
class ScoreConfianceDetaille:
    global_score: float  # 0.0 - 1.0

    # Breakdown par catégorie
    vendeur_score: float
    acquereur_score: float
    bien_score: float
    prix_score: float
    type_acte_score: float

    # Champs détectés vs requis
    champs_detectes: List[str]
    champs_manquants: List[str]
    champs_optionnels_manquants: List[str]

    def explication(self) -> str:
        """Génère une explication lisible du score."""
        return f"""
Score global: {self.global_score:.0%}
- Vendeur: {self.vendeur_score:.0%} {'✓' if self.vendeur_score > 0.7 else '!'}
- Acquéreur: {self.acquereur_score:.0%} {'✓' if self.acquereur_score > 0.7 else '!'}
- Bien: {self.bien_score:.0%} {'✓' if self.bien_score > 0.7 else '!'}
- Prix: {self.prix_score:.0%} {'✓' if self.prix_score > 0.7 else '!'}

Manquant: {', '.join(self.champs_manquants) or 'Rien'}
"""
```

### 2. Mode Interactif Intelligent

Ajouter un mode qui pose des questions :

```python
class AgentInteractif(AgentNotaire):
    """Agent avec capacité de dialogue."""

    def executer_interactif(self, demande: str) -> Generator[str, str, ResultatAgent]:
        """Exécute en mode interactif avec questions/réponses."""
        analyse = self.parseur.analyser(demande)

        # Si confiance faible, demander clarification
        if analyse.confiance < 0.7:
            for champ in analyse.champs_manquants[:3]:
                question = self._generer_question(champ)
                reponse = yield question  # Attend réponse utilisateur
                self._integrer_reponse(analyse, champ, reponse)

        # Confirmer avant génération
        resume = self._generer_resume(analyse)
        confirmation = yield f"Je vais générer :\n{resume}\n\nConfirmer ? (oui/non)"

        if confirmation.lower() in ('oui', 'o', 'yes', 'y'):
            return self._generer_acte(analyse)
        else:
            return ResultatAgent(succes=False, message="Génération annulée")
```

### 3. Suggestions Contextuelles

L'agent devrait suggérer des clauses pertinentes :

```python
def _suggerer_clauses(self, analyse: DemandeAnalysee) -> List[str]:
    """Suggère des clauses basées sur le contexte."""
    suggestions = []

    # Si plusieurs acquéreurs → suggérer convention d'indivision
    if len(analyse.acquereurs or []) > 1:
        suggestions.append("Convention d'indivision entre acquéreurs")

    # Si prix > 300k → suggérer prêt
    if (analyse.prix or {}).get('montant', 0) > 300000:
        suggestions.append("Condition suspensive de prêt")

    # Si appartement → diagnostics copropriété
    if (analyse.bien or {}).get('type') == 'appartement':
        suggestions.append("Documents copropriété obligatoires")

    return suggestions
```

### 4. Apprentissage des Corrections

Implémenter un système de feedback effectif :

```python
class ApprentissageAgent:
    """Gère l'apprentissage continu de l'agent."""

    def __init__(self, db_path: Path):
        self.corrections_db = db_path / "corrections.jsonl"
        self.patterns_enrichis = {}

    def enregistrer_correction(self, original: str, corrige: str, champ: str):
        """Enregistre une correction pour apprentissage."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "original": original,
            "corrige": corrige,
            "champ": champ
        }
        with open(self.corrections_db, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Mettre à jour les patterns si fréquent
        self._analyser_pattern(original, corrige, champ)

    def _analyser_pattern(self, original: str, corrige: str, champ: str):
        """Analyse si un pattern doit être enrichi."""
        # Si la même correction apparaît 3+ fois, créer un nouveau pattern
        key = f"{champ}:{original.lower()}"
        self.patterns_enrichis[key] = self.patterns_enrichis.get(key, 0) + 1

        if self.patterns_enrichis[key] >= 3:
            self._ajouter_pattern(original, corrige, champ)
```

---

## Améliorations Processus

### 1. Workflow Unifié "One Command"

Objectif : `python notaire.py "Crée promesse Martin→Dupont, 450k€"` génère un DOCX complet.

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW "ONE COMMAND"                        │
├─────────────────────────────────────────────────────────────────┤
│  1. PARSING           │ Analyse NL → DemandeAnalysee            │
│  2. VALIDATION        │ Vérifie complétude + cohérence         │
│  3. ENRICHISSEMENT    │ Charge exemple + fusionne données       │
│  4. SUGGESTION        │ Propose clauses contextuelles           │
│  5. GÉNÉRATION        │ Template + Jinja2 → Markdown            │
│  6. EXPORT            │ Markdown → DOCX formaté                 │
│  7. VÉRIFICATION      │ Compare structure → score conformité   │
│  8. ARCHIVAGE         │ Sauvegarde Supabase + local            │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Tests Automatisés Étendus

Créer une suite de tests exhaustive :

```python
# tests/test_generation_complete.py

@pytest.mark.parametrize("demande,expected_type,min_conformite", [
    ("Crée promesse Martin→Dupont 450k€", "promesse_vente", 0.80),
    ("Génère vente Société ABC à M. Durant, 1.2M€", "vente", 0.85),
    ("Martin & Pierre → Dupont & Thomas, appart 67m²", "promesse_vente", 0.75),
])
def test_generation_complete(demande, expected_type, min_conformite):
    """Teste la génération end-to-end."""
    agent = AgentNotaire()
    resultat = agent.executer(demande)

    assert resultat.succes, f"Échec: {resultat.message}"
    assert resultat.fichier_genere is not None

    # Vérifier conformité
    score = comparer_documents(resultat.fichier_genere, f"docs_originels/{expected_type}.docx")
    assert score >= min_conformite, f"Conformité {score:.0%} < {min_conformite:.0%}"
```

### 3. CLI Amélioré

Nouvelles commandes utiles :

```bash
# Statut des templates
python notaire.py template status
# → Affiche conformité de chaque template

# Validation données
python notaire.py valider donnees.json --type promesse
# → Vérifie complétude et suggère corrections

# Mode debug
python notaire.py agent "Crée promesse..." --debug
# → Affiche chaque étape du parsing

# Génération avec preview
python notaire.py agent "Crée promesse..." --preview
# → Montre ce qui sera généré avant confirmation
```

---

## Améliorations Performance

### Métriques Actuelles

| Étape | Temps Actuel | Objectif |
|-------|--------------|----------|
| Parsing NL | ~50ms | <50ms ✓ |
| Validation | ~100ms | <100ms ✓ |
| Assemblage | ~200ms | <150ms |
| Export DOCX | ~500ms | <400ms |
| Vérification | ~1.5s | <1s |
| **TOTAL** | **~2.35s** | **<2s** |

### Optimisations Proposées

1. **Cache Templates Compilés**
```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_compiled_template(template_name: str):
    """Cache les templates Jinja2 compilés."""
    return jinja_env.get_template(template_name)
```

2. **Parallélisation Export**
```python
import asyncio

async def exporter_parallele(markdown: str, formats: List[str]):
    """Exporte en parallèle vers plusieurs formats."""
    tasks = [
        asyncio.create_task(exporter_docx(markdown)) if 'docx' in formats else None,
        asyncio.create_task(exporter_pdf(markdown)) if 'pdf' in formats else None,
    ]
    return await asyncio.gather(*[t for t in tasks if t])
```

3. **Lazy Loading Sections**
```python
# Ne charger les sections que si nécessaires
def assembler_template(template_name: str, donnees: dict):
    sections_requises = detecter_sections_requises(donnees)

    # Charger uniquement les sections nécessaires
    for section in sections_requises:
        load_section(section)
```

---

## Feuille de Route

### Sprint 1 (Semaine 1-2) - CRITIQUE

| Tâche | Effort | Impact | Responsable |
|-------|--------|--------|-------------|
| Compléter template promesse | 3j | ⭐⭐⭐⭐⭐ | Dev |
| Créer partie_developpee_promesse.md | 2j | ⭐⭐⭐⭐⭐ | Dev |
| Intégrer validation dans agent | 2j | ⭐⭐⭐⭐ | Dev |
| Tests génération promesse | 1j | ⭐⭐⭐ | QA |

**Objectif** : Template promesse ≥85% conformité

### Sprint 2 (Semaine 3-4) - IMPORTANT

| Tâche | Effort | Impact |
|-------|--------|--------|
| Support multi-parties | 3j | ⭐⭐⭐⭐ |
| Score confiance détaillé | 2j | ⭐⭐⭐ |
| CLI template status | 1j | ⭐⭐⭐ |
| Documentation mise à jour | 2j | ⭐⭐⭐ |

**Objectif** : Agent gère 90% des cas réels

### Sprint 3 (Semaine 5-6) - NICE TO HAVE

| Tâche | Effort | Impact |
|-------|--------|--------|
| Mode interactif | 3j | ⭐⭐⭐ |
| Suggestions contextuelles | 2j | ⭐⭐⭐ |
| Apprentissage corrections | 3j | ⭐⭐⭐ |
| Optimisations performance | 2j | ⭐⭐ |

**Objectif** : UX excellente, temps <2s

### Sprint 4+ (Long terme)

- Intégration NLP (spaCy/Transformers)
- API REST complète
- Dashboard analytics
- Multi-tenant production

---

## Checklist Implémentation

### Template Promesse
- [ ] Ajouter `{% include 'sections/partie_developpee_promesse.md' %}` avant "DONT ACTE"
- [ ] Créer `sections/partie_developpee_promesse.md` avec sections spécifiques
- [ ] Ajouter conditions suspensives
- [ ] Ajouter indemnité d'immobilisation
- [ ] Ajouter délai de réalisation
- [ ] Ajouter faculté de substitution
- [ ] Tester avec `comparer_documents_v2.py`
- [ ] Valider conformité ≥85%

### Agent Autonome
- [ ] Ajouter appel `_valider_donnees()` dans `executer()`
- [ ] Créer `PATTERN_FLECHE_MULTI` pour multi-parties
- [ ] Implémenter `_extraire_parties_multiples()`
- [ ] Ajouter `ScoreConfianceDetaille` dataclass
- [ ] Tests unitaires nouveaux patterns

### Documentation
- [ ] Mettre à jour CLAUDE.md (conformité templates)
- [ ] Créer README.md
- [ ] Documenter API dans QUICKSTART.md
- [ ] Ajouter FAQ courante

---

## Conclusion

Pour avoir un **agent excellent** de génération d'actes notariaux, les priorités sont :

1. **CRITIQUE** : Compléter le template promesse (de 60.9% → 85%+)
2. **IMPORTANT** : Intégrer la validation dans le flux agent
3. **IMPORTANT** : Supporter les cas multi-parties
4. **NICE TO HAVE** : Mode interactif et apprentissage

Avec ces améliorations, l'agent Notomai pourra :
- Générer des promesses ET ventes 100% conformes
- Gérer 95%+ des cas notariaux courants
- Offrir une UX fluide et intelligente
- S'améliorer continuellement

---

*Document créé le 26 janvier 2026*
*Notomai v1.3.0*
