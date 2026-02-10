# Analyse Comparative Trames Viager K vs L

**Date**: 2026-02-04
**Version**: 2.0
**Phase**: 2.1 - Templates Spécialisés

---

## RÉSUMÉ EXÉCUTIF

**Trame à utiliser**: **L (Trame_promesse_copro_L.docx)** - SEULE trame viager complète

**Trame K**: Promesse classique NON-VIAGER (114 203 caractères, 0 mentions "viager")
**Trame L**: Promesse VIAGER complète (142 821 caractères, +25.1%, 8 mentions "viager", 66 mentions "rente")

---

## 1. SECTIONS SPÉCIFIQUES VIAGER (9 sections majeures)

### 1.1 TERMINOLOGIE VIAGER
- CRÉDIRENTIER: Le vendeur (reçoit la rente)
- DÉBIRENTIER: L'acquéreur (paie la rente)
- BOUQUET: Montant comptant (ex: 121 965 EUR)
- RENTE VIAGÈRE: Versement périodique jusqu'à décès (ex: 240 EUR/mois)
- DROIT D'USAGE ET D'HABITATION: Droit viager, personnel, incessible

**Statut**: OBLIGATOIRE - Définitions légales (Code civil)

---

### 1.2 SANTÉ DU PROMETTANT (Articles 1974-1975 Code civil)
- Avertissement décès dans 20 jours → nullité contrat
- Certificat médical recommandé (santé normale pour âge)
- Absence d'aléa → risque annulation

**Statut**: OBLIGATOIRE - Protection Code civil

---

### 1.3 RÉSERVE DROIT D'USAGE ET D'HABITATION
**Caractéristiques**:
- Personnel (crédirentier uniquement)
- Bourgeoisement habité (pas commercial)
- Incessible & non-transmissible
- Pas de location (peine de nullité)
- Hébergement service autorisé (santé/sécurité)

**Obligations crédirentier**:
- Taxe habitation, assurance risques locatifs
- Réparations courantes/locatives
- Bien revient libre après décès/abandon

**Obligations débirentier**:
- Grosses réparations (structure, toiture, chauffage)
- Maintien habitable
- Préservation état général

**Statut**: CRITIQUE - Structure fondamentale viager

---

### 1.4 ABANDON DROIT & MISE EN PLACE RENTE
**Mécanisme**:
- Abandon irrévocable avec préavis 2 mois
- Notification: recommandé AR ou huissier
- Rente mensuelle: 240 EUR/mois (exemple)
- Déclenchement: quand bien complètement libéré

**Processus libération**:
1. Organiser remise clés
2. Transmettre contrats fournitures
3. Relève consommations
4. Nouvelle adresse postale

**Statut**: TRÈS IMPORTANT - Transforme structure contrat

---

### 1.5 PRIX - CONDITIONS FINANCIÈRES
**Structure**:
- Bouquet (comptant): 121 965 EUR
- Rente viagère (si abandon): 240 EUR/mois
- Valeur économique: 121 965 EUR
- Valeur vénale réelle: 284 300 EUR
- Différence: 162 335 EUR (justification)

**Conventions rente**:
1. Virement automatique (5ème jour mois)
2. Révision annuelle (indexation INSEE)
3. Pas de certificat de vie si quittances touchées
4. Frais renouvellement privilège: à charge débirentier

**Statut**: CRITIQUE - Structure financière complète

---

### 1.6 ALIÉNATION PAR DÉBIRENTIER
**Obligations**:
- Informer crédirentier (article 1690 Code civil)
- Copie acte authentique sans frais
- Tous acquéreurs successifs garants solidaires
- Transfert privilège possible (bien valeur ≥)

**Statut**: TRÈS IMPORTANT - Pérennité rente

---

### 1.7 RÉVISION DE LA RENTE
**Indice**: INSEE IPC Base 2015 (hors tabac)
**Fréquence**: Annuelle (1er jour mois anniversaire)
**Formule**: `Nouveau = (Indice nouveau / Indice ancien) x Montant ancien`

**Cas particuliers**:
- Disparition indice → coefficient raccordement INSEE
- Pas nouvel indice → accord parties
- Défaut accord → montant figé

**Statut**: OBLIGATOIRE - Protection inflation

---

### 1.8 RACHAT DE LA RENTE
**Faculté débirentier**:
- Verser capital à assurance/organisme
- Génère rente équivalente + indexation identique
- Crédirentier donne mainlevée privilège

**Conséquences**:
- Dégagement privilège
- Arrêt renouvellements inscription
- Déistement tous droits action résolutoire

**Statut**: IMPORTANT - Flexibilité débirentier

---

### 1.9 CLAUSE PÉNALE & GARANTIE
**Déclenchement retard paiement**:
- Intérêt légal + 3 points (automatique)
- Pas mise en demeure nécessaire
- Jusqu'à paiement effectif

**Lien clause résolutoire**:
- Défaut paiement → action en résolution
- Crédirentier peut vendre bien pour se payer

**Statut**: TRÈS IMPORTANT - Protection crédirentier

---

## 2. STRUCTURE JSON VARIABLES VIAGER

### 2.1 Prix Structure
```json
{
  "prix": {
    "type_vente": "viager",
    "bouquet": {
      "montant": 121965.00,
      "devise": "EUR",
      "date_versement": "2021-01-15"
    },
    "valeur_economique": 121965.00,
    "valeur_venale": 284300.00,
    "difference": 162335.00,
    "rente_viagere": {
      "montant_mensuel": 240.00,
      "periodicite": "mensuelle",
      "jour_versement": 5,
      "date_debut": "2021-01-15",
      "compte_rib": "FR76...",
      "indexation": {
        "indice": "INSEE_IPC_Base2015",
        "hors_tabac": true,
        "frequence": "annuelle",
        "date_premiere_application": "2022-01-01",
        "formule": "proportionnelle"
      },
      "rachat": {
        "possible": true,
        "conditions": "capital_assurance_indexation_identique"
      }
    },
    "clause_penale": {
      "taux_interet": "legal_particuliers_plus_3",
      "automatique": true,
      "mise_en_demeure": false
    }
  }
}
```

### 2.2 Droit Usage Habitation
```json
{
  "bien": {
    "droit_usage_habitation": {
      "reserve": true,
      "nature": "viager_personnel",
      "beneficiaire": "promettant",
      "restrictions": {
        "habitation_bourgeoise": true,
        "incessible": true,
        "non_transmissible": true,
        "pas_cession": true,
        "pas_location": true,
        "hebergement_service_autorise": true
      },
      "obligations_credirentier": {
        "taxe_habitation": true,
        "assurance_risques_locatifs": true,
        "assurance_rc": true,
        "reparations_courantes": true,
        "liberer_apres_deces_abandon": true
      },
      "obligations_debirentier": {
        "grosses_reparations": true,
        "maintenir_habitable": true,
        "preservation_etat": true
      },
      "fin": "deces_ou_abandon",
      "abandon": {
        "possible": true,
        "preavis_jours": 60,
        "notification": "recommande_AR_ou_huissier",
        "irrevocable": true,
        "declenche_rente": true
      }
    }
  }
}
```

### 2.3 Santé Promettant
```json
{
  "promettants": [{
    "sante": {
      "certificat_medical": {
        "existe": true,
        "date": "2020-12-15",
        "medecin": "Dr. Martin",
        "conclusion": "état_sante_normal_pour_age"
      },
      "declaration_sante": {
        "maladies_graves": false,
        "hospitalisation_recente": false
      },
      "avertissement_art_1974_1975": true
    }
  }]
}
```

### 2.4 Privilège & Garanties
```json
{
  "garanties": {
    "privilege": {
      "inscrit": true,
      "duree_initiale_annees": 15,
      "renouvelable": true,
      "frais_renouvellement": "debirentier",
      "rang": "premier",
      "concurrence": false
    },
    "solidarite_acquereurs": true,
    "transfert_possible": {
      "autorise": true,
      "condition_valeur": "superieure_ou_egale"
    }
  }
}
```

---

## 3. DIFFÉRENCES STRUCTURELLES K vs L

| Aspect | Trame K (Classique) | Trame L (Viager) |
|--------|-------------------|-----------------|
| **Type** | Promesse classique | Promesse viager |
| **Paiement** | Comptant ou prêt | Bouquet + rente |
| **Occupation** | Acquéreur immédiat | Vendeur conserve droit |
| **Durée** | Délai réalisation fixe | Jusqu'à décès vendeur |
| **Rente** | N/A | 120-360 EUR/mois |
| **Indexation** | N/A | INSEE annuelle |
| **Privilège** | N/A | Inscription 12-15 ans |
| **Clause résolutoire** | Prêt | Défaut paiement rente |
| **Abandon droit** | N/A | Préavis 2 mois → rente |
| **Caractères** | 114 203 | 142 821 (+25.1%) |
| **Tables** | 19 | 77 (+58) |

---

## 4. DÉTECTION AUTOMATIQUE VIAGER

### 4.1 Marqueurs Obligatoires
- `prix.type_vente == "viager"` OU
- `prix.rente_viagere` existe OU
- `prix.bouquet` existe OU
- `bien.droit_usage_habitation.reserve == true`

### 4.2 Niveau de Confiance
| Marqueurs Présents | Confiance | Action |
|--------------------|-----------|--------|
| ≥3 marqueurs | 95% | Détection viager confirmée |
| 2 marqueurs | 75% | Probable viager, demander confirmation |
| 1 marqueur | 40% | Avertissement, vérifier avec notaire |
| 0 marqueur | 5% | Pas viager |

---

## 5. PROCHAINES ÉTAPES

### Phase 2.1 Suite
1. ✅ Analyse trames K et L
2. 🔄 Enrichir `schemas/variables_promesse_vente.json` v4.1.0
3. ⏳ Créer `templates/promesse_viager.md`
4. ⏳ Ajouter questions viager dans `schemas/questions_promesse_vente.json` v3.2.0
5. ⏳ Tester génération viager E2E

### Questions Viager (19 nouvelles)
**Section 15_viager**:
1. Type de vente (viager / classique)
2. Montant bouquet
3. Montant rente mensuelle
4. Réserve droit usage et habitation ?
5. Indexation (indice, fréquence)
6. Certificat médical disponible ?
7. Date certificat médical
8. Rachat rente autorisé ?
9. Privilège déjà inscrit ?
10. Durée privilège
11. Clause pénale intérêt (légal, légal+3, autre)
12. Abandon droit possible ?
13. Préavis abandon (jours)
14. Valeur économique
15. Valeur vénale
16. Solidarité acquéreurs successifs ?
17. Transfert privilège autorisé ?
18. Grosses réparations à charge (crédirentier / débirentier)
19. Taxe habitation à charge (crédirentier / débirentier)

---

## 6. FICHIERS SOURCES

- **Référence principale**: `docs_original/Trame_promesse_copro_L.docx`
- **Comparaison**: `docs_original/Trame_promesse_copro_K.docx`
- **Schéma**: `schemas/variables_promesse_vente.json` (à enrichir v4.0.0 → v4.1.0)
- **Questions**: `schemas/questions_promesse_vente.json` (à enrichir v3.1.0 → v3.2.0)
- **Template**: `templates/promesse_viager.md` (à créer)

---

*Généré par analyse automatique - Agent ac34fe8 - Phase 2.1 v1.9.0*
