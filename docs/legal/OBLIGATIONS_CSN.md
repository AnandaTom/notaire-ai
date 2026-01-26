# Obligations envers le Conseil Supérieur du Notariat (CSN)

**Date**: 2026-01-26
**Statut**: Analyse complète

---

## 1. Contexte Réglementaire

### 1.1 Le Notariat et ses Institutions

| Institution | Rôle | Impact sur Notomai |
|-------------|------|-------------------|
| **CSN** (Conseil Supérieur du Notariat) | Représente la profession, définit les règles | Charte numérique, Label ETIK |
| **ADSN** (Association Développement Service Notarial) | Opérateur technique du notariat | Gère Real.not, Planète, clés de signature |
| **Chambres départementales** | Contrôle disciplinaire local | Peuvent recommander/interdire des outils |

### 1.2 Cadre Juridique

- **Décret 71-941 du 26/11/1971**: Réglementation profession notariale
- **Article 378 Code pénal**: Secret professionnel (1 an + 15 000€)
- **Règlement national des notaires**: Obligations déontologiques
- **RGPD**: Protection des données

---

## 2. Label ETIK - Analyse Complète

### 2.1 Qu'est-ce que le Label ETIK?

Le **Label ETIK** est une certification délivrée par le CSN aux entreprises numériques travaillant avec les notaires. Il est basé sur la **Charte pour un développement éthique du numérique notarial** (22 novembre 2018).

### 2.2 Est-il obligatoire?

| Question | Réponse |
|----------|---------|
| Obligatoire pour vendre aux notaires? | **NON** |
| Obligatoire pour accéder aux API notariat? | **OUI** (Planète, Real.not) |
| Recommandé commercialement? | **OUI** (gage de confiance) |

### 2.3 Avantages du Label

- Accès aux **API du notariat** (Planète, Real.not, télé@ctes)
- **Crédibilité** auprès des notaires
- Figurer sur la **liste officielle CSN** des entreprises labellisées
- Accès aux **normes d'interopérabilité**

### 2.4 Processus de Labellisation

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. CANDIDATURE │────▶│  2. AUDIT       │────▶│  3. DÉCISION    │
│  Dossier CSN    │     │  Bureau Veritas │     │  CSN            │
│                 │     │  172+ points    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   ~1 000€ frais           ~5 000€ audit          Valable 3 ans
```

### 2.5 Référentiel d'Audit (172+ points)

| Catégorie | Points de contrôle | Exemples |
|-----------|-------------------|----------|
| **Infrastructure** | ~40 | Hébergement, architecture, redondance |
| **Sécurité** | ~50 | Chiffrement, 2FA, pentest, logs |
| **RGPD** | ~30 | DPA, registre, droits personnes |
| **Code** | ~25 | Qualité, tests, documentation |
| **Déontologie** | ~20 | Secret pro, conflit intérêts, transparence IA |
| **Support** | ~10 | SLA, maintenance, formation |

### 2.6 Coût Estimé

| Poste | Coût |
|-------|------|
| Frais de dossier CSN | 1 000 - 2 000€ |
| Audit Bureau Veritas | 5 000 - 8 000€ |
| Mise en conformité (si gaps) | Variable |
| **TOTAL** | **6 000 - 10 000€** |
| Renouvellement (tous les 3 ans) | ~5 000€ |

### 2.7 Entreprises Labellisées (exemples)

- Quai des Notaires (1ère labellisée, 2020)
- Xelians
- Legapass
- Allaw
- ~15 entreprises au total (2026)

---

## 3. Charte Numérique Notariale - Exigences

### 3.1 Les 3 Piliers

#### Pilier 1: Protection des Clients

| Exigence | Notomai | Statut |
|----------|---------|--------|
| Confidentialité données | Chiffrement AES-256, RLS | ✅ |
| Pas de conflit d'intérêts | Pas de revente données | ✅ |
| Transparence tarifs | CGU claires | ✅ |

#### Pilier 2: Coopération avec la Profession

| Exigence | Notomai | Statut |
|----------|---------|--------|
| Respect secret professionnel | Engagement contractuel | ✅ |
| Interopérabilité | Formats standards (JSON, DOCX) | ✅ |
| Non-concurrence déloyale | Pas de service juridique direct | ✅ |

#### Pilier 3: Transparence Technologique

| Exigence | Notomai | Statut |
|----------|---------|--------|
| Information sur sous-traitants | Documenté (Supabase, Anthropic) | ✅ |
| Transparence algorithmes/IA | Mentionné dans CGU | ✅ |
| Explication résultats IA | Aide à la décision, pas décision | ✅ |

### 3.2 Article 3 - Transparence IA (Critique)

> *"Les signataires s'engagent à [...] savoir si [la prestation] intègre l'utilisation d'un algorithme. Dans ce dernier cas ils expliquent son rôle, et donnent les éléments d'information utiles pour comprendre le résultat du traitement opéré par celui-ci."*

**Notre conformité**:
- ✅ Mention IA dans CGU Article 2.3
- ✅ Description des usages (détection, suggestion, extraction)
- ✅ Clarification: "aide à la décision, pas décision"

---

## 4. Secret Professionnel - Obligations Critiques

### 4.1 Cadre Légal

**Article 378 Code pénal**:
> *"La révélation d'une information à caractère secret par une personne qui en est dépositaire [...] est punie d'un an d'emprisonnement et de 15 000 euros d'amende."*

### 4.2 Application à Notomai

| Situation | Risque | Notre protection |
|-----------|--------|------------------|
| Accès données par employés | ÉLEVÉ | Engagement confidentialité renforcé |
| Fuite base de données | CRITIQUE | Chiffrement AES-256 |
| Accès Anthropic aux données | MODÉRÉ | Données non utilisées pour entraînement |
| Hébergement hors UE | MODÉRÉ | Supabase EU (Francfort) |

### 4.3 Mesures Implémentées

1. **Chiffrement bout-en-bout** des données sensibles
2. **Isolation par office** (Row Level Security)
3. **Logs d'accès** horodatés et archivés
4. **Clause contractuelle** de confidentialité renforcée
5. **DPA** avec sous-traitants (Article 28 RGPD)

---

## 5. Interopérabilité avec le Notariat

### 5.1 Systèmes du Notariat

| Système | Fonction | Accès Notomai |
|---------|----------|---------------|
| **Planète** | Plateforme d'échanges (225k flux/jour) | ❌ Nécessite label ETIK |
| **Real.not** | Signature électronique qualifiée | ❌ Réservé aux notaires |
| **Télé@ctes** | Publication hypothèques | ❌ Via Planète |
| **MICEN** | Minutier Central Électronique | ❌ Réservé aux notaires |
| **Genapi** | Logiciel rédaction actes | ❌ Concurrent |

### 5.2 Notre Positionnement

Notomai est un **outil autonome** qui:
- ✅ Génère des DOCX compatibles avec tous logiciels
- ✅ Exporte en formats standards (JSON, PDF)
- ❌ Ne se connecte pas directement aux systèmes notariaux
- ⚠️ Pourrait à terme demander le label ETIK pour intégration

---

## 6. Recommandations Stratégiques

### 6.1 Court Terme (0-6 mois)

| Action | Priorité | Coût | Bénéfice |
|--------|----------|------|----------|
| Finaliser CGU avec avocat | HAUTE | 2 000€ | Protection juridique |
| Souscrire RC Pro | HAUTE | 2 000€/an | Couverture sinistres |
| Documenter conformité Charte CSN | MOYENNE | 0€ | Prêt pour audit |

### 6.2 Moyen Terme (6-18 mois)

| Action | Priorité | Coût | Bénéfice |
|--------|----------|------|----------|
| Demander Label ETIK | MOYENNE | 8 000€ | Crédibilité + API |
| Certification ISO 27001 | BASSE | 15 000€+ | Premium clients |

### 6.3 Décision: Label ETIK - Oui ou Non?

**Arguments POUR**:
- Accès aux API Planète (flux automatisés)
- Crédibilité commerciale
- Liste officielle CSN

**Arguments CONTRE**:
- Coût initial élevé (8-10k€)
- Audit tous les 3 ans
- Contraintes de conformité

**Recommandation**: Attendre **10-20 clients payants** avant de demander le label. Le label n'est pas nécessaire pour la phase de lancement.

---

## 7. Checklist de Conformité CSN

### Conformité Actuelle

- [x] Chiffrement AES-256 données au repos
- [x] Chiffrement TLS 1.3 en transit
- [x] Row Level Security (isolation offices)
- [x] Authentification 2FA documentée
- [x] Registre traitements RGPD
- [x] Politique de confidentialité
- [x] Transparence sur usage IA (CGU)
- [x] Hébergement UE (Francfort)
- [x] DPA sous-traitants

### À Faire

- [ ] CGU validées par avocat
- [ ] Assurance RC Pro souscrite
- [ ] Écran validation obligatoire (UI)
- [ ] Pentest externe (recommandé)
- [ ] Label ETIK (optionnel)

---

## 8. Questions Fréquentes

### Q1: Un notaire peut-il utiliser Notomai sans label ETIK?

**OUI**. Le label ETIK est pour l'éditeur, pas pour l'utilisateur. Le notaire peut librement choisir ses outils informatiques, tant qu'il respecte ses obligations déontologiques.

### Q2: Risque-t-on des sanctions de l'Ordre?

**NON**, si:
- Le notaire reste responsable des actes (notre CGU le garantit)
- Les données sont protégées (notre architecture le garantit)
- Pas de pratique déloyale ou trompeuse

### Q3: Faut-il informer la Chambre des Notaires?

**NON obligatoirement**, mais:
- Le notaire peut volontairement le mentionner
- En cas de contrôle, il doit pouvoir justifier la sécurité

### Q4: Peut-on être référencé par le CSN sans label?

**NON**. Seules les entreprises labellisées ETIK figurent sur la liste officielle du CSN.

---

## Sources

- [Conseil Supérieur du Notariat](https://www.csn.notaires.fr/fr)
- [Label ETIK - Éditions Langloÿs](https://editionslangloys.com/label-etik-du-conseil-superieur-du-notariat/)
- [Charte numérique notariale - Village des Notaires](https://www.village-notaires-patrimoine.com/CSN-Edition-d-une-charte-pour-le-developpement-ethique-du-numerique-notarial)
- [ADSN - Groupe](https://www.groupeadsn.fr/)
- [Labellisation LegalTechs - Banque des Territoires](https://www.banquedesterritoires.fr/legaltech/actualites/les-legaltechs-labelisees-par-le-conseil-superieur-du-notariat-csn)

---

*Document mis à jour le 2026-01-26*
