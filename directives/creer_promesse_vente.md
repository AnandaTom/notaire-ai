# Directive : Création d'une Promesse Unilatérale de Vente - Lots de Copropriété

## Objectif

Guider la création complète d'une **promesse unilatérale de vente** de lots de copropriété, de la collecte des informations jusqu'à l'export DOCX fidèle à la trame originale.

---

## Différences avec l'acte de vente définitif

| Élément | Promesse Unilatérale | Acte de Vente |
|---------|----------------------|---------------|
| **Parties** | Promettant / Bénéficiaire | Vendeur / Acquéreur |
| **Engagement** | Unilatéral (promettant seul) | Synallagmatique (réciproque) |
| **Indemnité d'immobilisation** | Obligatoire (généralement 10%) | Non applicable |
| **Option** | Le bénéficiaire a une option | Pas d'option |
| **Délai de réalisation** | Date limite pour réitérer | Transfert immédiat |
| **Conditions suspensives** | Fréquentes (prêt, préemption) | Rares |

---

## Ressources

| Ressource | Chemin |
|-----------|--------|
| Template DOCX original | `docs_originels/Trame promesse unilatérale de vente lots de copropriété.docx` |
| Template Jinja2 | `templates/promesse_vente_lots_copropriete.md` |
| Schéma variables | `schemas/variables_promesse_vente.json` |
| Questions notaire | `schemas/questions_promesse_vente.json` |
| Script assemblage | `execution/assembler_acte.py` |
| Script export DOCX | `execution/exporter_docx.py` |
| Script validation | `execution/valider_acte.py` |

---

## Flux de travail

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CRÉATION PROMESSE UNILATÉRALE DE VENTE               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. COLLECTE DES INFORMATIONS                                          │
│     ├─► Consulter schemas/questions_promesse_vente.json                │
│     ├─► Poser les questions au notaire par sections                    │
│     └─► Sauvegarder dans .tmp/donnees_client.json                      │
│                                                                        │
│  2. VALIDATION DES DONNÉES                                             │
│     ├─► Exécuter valider_acte.py                                       │
│     ├─► Vérifier quotités = 100%                                       │
│     ├─► Vérifier indemnité immobilisation (généralement 10%)           │
│     ├─► Vérifier cohérence prêt/prix                                   │
│     └─► Vérifier délais (réalisation > date obtention prêt)            │
│                                                                        │
│  3. ASSEMBLAGE MARKDOWN                                                │
│     ├─► Exécuter assembler_acte.py                                     │
│     └─► Template promesse_vente_lots_copropriete.md + données          │
│                                                                        │
│  4. EXPORT DOCX                                                        │
│     ├─► Exécuter exporter_docx.py                                      │
│     └─► Formatage 100% fidèle à la trame originale                     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Étape 1 : Collecte des informations

### Sections obligatoires

1. **Informations sur l'acte** - Date, référence, notaires
2. **Promettant(s)** - Identité complète, situation matrimoniale
3. **Bénéficiaire(s)** - Identité complète, situation matrimoniale
4. **Quotités acquises** - Répartition ou à déterminer
5. **Désignation du bien** - Adresse, cadastre
6. **Lots de copropriété** - Numéro, tantièmes, Carrez
7. **Copropriété** - EDD, syndic, immatriculation
8. **Prix** - Montant, modalités
9. **Négociation** - Agent immobilier (si applicable)
10. **Indemnité d'immobilisation** - Montant, versement
11. **Délais** - Réalisation, rétractation
12. **Conditions suspensives** - Prêt, préemption, autres
13. **Financement** - Apport, prêt sollicité
14. **Usage du bien** - Actuel, destination
15. **Origine de propriété** - Chaîne de propriété
16. **Diagnostics** - DDT complet
17. **Travaux** - Si réalisés par le promettant
18. **Urbanisme** - Notes, certificats
19. **Clauses optionnelles** - Exécution forcée, substitution

### Points critiques spécifiques à la promesse

| Point | Vérification |
|-------|--------------|
| **Indemnité d'immobilisation** | Généralement 10% du prix - vérifier avec le notaire |
| **Délai de réalisation** | Doit être postérieur à la date d'obtention du prêt |
| **Délai de rétractation** | 10 jours légaux - ne pas réduire |
| **Condition suspensive prêt** | Montant, taux, durée doivent être cohérents |
| **Quotités** | Peuvent être "à déterminer" lors de la réitération |
| **Séquestre** | Préciser qui séquestre l'indemnité (généralement le notaire) |

### Exemple de dialogue

```
Agent: Bonjour, je vais vous aider à créer une promesse unilatérale
       de vente. Commençons par les informations générales.

Agent: Quelle est la date prévue de signature de la promesse ?
Notaire: Le 15 mars 2025

Agent: Y a-t-il un notaire assistant le bénéficiaire ?
Notaire: Non, je suis seul

Agent: Passons au promettant (vendeur). Combien de promettants ?
Notaire: Un seul, Madame MARTIN

Agent: [... suite des questions selon questions_promesse_vente.json ...]

Agent: Pour l'indemnité d'immobilisation, quel montant est prévu ?
Notaire: 24 500 euros, soit 10% du prix

Agent: Comment sera-t-elle versée ?
Notaire: Par virement séquestre chez moi dans les 15 jours suivant
         l'expiration du délai de rétractation

Agent: Quelle est la date limite de réalisation ?
Notaire: Le 30 juin 2025
```

---

## Étape 2 : Validation des données

### Commande

```bash
python execution/valider_acte.py \
    --donnees .tmp/donnees_client.json \
    --schema schemas/variables_promesse_vente.json \
    --type promesse_vente
```

### Règles de validation spécifiques

1. **Indemnité d'immobilisation**
   - Généralement entre 5% et 10% du prix
   - Alerte si < 5% ou > 15%

2. **Délais cohérents**
   ```
   Date signature < Date obtention prêt < Date réalisation
   ```

3. **Conditions suspensives**
   - Si prêt : montant + apport >= prix + frais estimés
   - Taux maximum réaliste (vérifier marché actuel)

4. **Quotités**
   - Si déterminées : doivent totaliser 100%
   - Si "à déterminer" : acceptable

---

## Étape 3 : Assemblage Markdown

### Commande

```bash
python execution/assembler_acte.py \
    --template promesse_vente_lots_copropriete.md \
    --donnees .tmp/donnees_client.json \
    --output .tmp/actes_generes/
```

### Sections conditionnelles du template

Le template inclut des sections conditionnelles selon les données :

| Section | Condition |
|---------|-----------|
| Notaire assistant | `acte.notaire_beneficiaire` présent |
| Meubles et mobilier | `meubles.inclus == true` |
| Négociation | `negociation.avec_agent == true` |
| Division cadastrale | `bien.division_cadastrale` présent |
| Travaux réalisés | `travaux.travaux_realises` non vide |
| Condition prêt | `conditions_suspensives.pret.applicable == true` |

---

## Étape 4 : Export DOCX

### Commande

```bash
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/promesse_vente_{client}.docx
```

### Formatage DOCX (identique à la trame)

| Paramètre | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Marges | G=60mm, D=15mm, H/B=25mm |
| Retrait 1ère ligne | 12.51mm |
| Interligne | Simple |
| Heading 1 | Bold, ALL CAPS, underline, centré |
| Heading 2 | Bold, small caps, underline, centré |
| Heading 3 | Bold, underline, centré |
| Heading 4 | Bold only, 6pt avant |

**IMPORTANT** : Ces valeurs sont codées en dur dans `exporter_docx.py` et ne doivent **JAMAIS** être modifiées.

---

## Annexes standards

Liste des annexes généralement jointes à une promesse de vente :

1. Plans cadastral et géoportail
2. Plans des lots et plan de masse
3. Diagnostic Carrez
4. Note d'urbanisme
5. Note de voirie
6. Certificat de non-péril
7. Factures travaux et attestation décennale (si applicable)
8. Diagnostic amiante parties privatives
9. Diagnostic amiante parties communes
10. État de l'installation intérieure d'électricité
11. Diagnostic de performances énergétiques (DPE)
12. État des risques
13. Données environnementales (BASIAS, BASOL, Géorisques)
14. Attestation de mise à jour annuelle copropriété
15. Carnet d'entretien
16. Fiche synthétique
17. Procès-verbaux AG des trois dernières années

### Flexibilité des annexes

L'agent peut **ajouter ou retirer** des annexes selon le contexte :

- **Ajouter** : Mandat de l'agent, attestation de garantie financière, etc.
- **Retirer** : Diagnostic plomb si immeuble post-1949, etc.

---

## Clauses optionnelles

### Clauses fréquemment incluses

- **Exécution forcée** (art. 1221 Code civil) - par défaut incluse
- **Réserve du droit de préemption** - généralement incluse
- **Convention sur les charges de copropriété**
- **Convention sur les travaux votés**

### Clauses pouvant être ajoutées

- **Clause de substitution** - permet au bénéficiaire de se faire substituer
- **Clause pénale** - pénalité en cas de non-exécution
- **Condition suspensive particulière** - vente d'un autre bien, obtention d'un permis, etc.

### Clauses pouvant être retirées

- **Condition suspensive de prêt** - si paiement comptant intégral
- **Sections diagnostics** - si non applicables (ex: plomb pour immeuble récent)

---

## Erreurs fréquentes à éviter

| Erreur | Conséquence | Vérification |
|--------|-------------|--------------|
| Quotités ne totalisant pas 100% | Acte invalide | Validation automatique |
| Indemnité trop faible | Risque pour le promettant | Alerte si < 5% |
| Date réalisation < date obtention prêt | Condition impossible | Validation automatique |
| Oubli du délai de rétractation | Illégal | Toujours 10 jours minimum |
| Carrez manquant pour appartement | Non-conforme | Obligatoire si > 8m² |

---

## Pipeline complet

### Commande en une ligne

```bash
# 1. Valider
python execution/valider_acte.py --donnees .tmp/donnees_client.json --schema schemas/variables_promesse_vente.json && \
# 2. Assembler
python execution/assembler_acte.py --template promesse_vente_lots_copropriete.md --donnees .tmp/donnees_client.json --output .tmp/actes_generes/ && \
# 3. Exporter
python execution/exporter_docx.py --input .tmp/actes_generes/*/acte.md --output outputs/promesse_vente.docx
```

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création initiale | Agent |

---

## Voir aussi

- [directives/creer_acte.md](creer_acte.md) - Création d'un acte de vente définitif
- [directives/collecte_informations.md](collecte_informations.md) - Guide de collecte
- [directives/formatage_docx.md](formatage_docx.md) - Spécifications formatage
- [directives/validation_donnees.md](validation_donnees.md) - Règles de validation
- [schemas/variables_promesse_vente.json](../schemas/variables_promesse_vente.json) - Schéma des variables
- [schemas/questions_promesse_vente.json](../schemas/questions_promesse_vente.json) - Questions à poser
- [templates/promesse_vente_lots_copropriete.md](../templates/promesse_vente_lots_copropriete.md) - Template Jinja2
