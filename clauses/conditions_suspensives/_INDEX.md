# Clauses - conditions_suspensives

Total: 6 clauses

## Liste des clauses

### Condition suspensive de prêt - Standard

- **ID**: `cs_pret_standard`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: promesse_vente, compromis
- **Fichier**: `cs_pret_standard.md`
- **Variables**: pret.montant, pret.duree_mois, pret.taux_maximum, pret.date_limite_obtention

### Condition suspensive de prêt avec PTZ

- **ID**: `cs_pret_ptz`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: promesse_vente, compromis
- **Fichier**: `cs_pret_ptz.md`
- **Variables**: pret_principal.montant, ptz.montant, pret.date_limite_obtention

### Réserve du droit de préemption urbain

- **ID**: `cs_preemption_urbain`
- **Statut**: 🔴 OBLIGATOIRE
- **Type d'acte**: promesse_vente, compromis, vente
- **Fichier**: `cs_preemption_urbain.md`
- **Variables**: bien.adresse.ville

### Réserve du droit de préemption du locataire

- **ID**: `cs_preemption_locataire`
- **Statut**: 🔴 OBLIGATOIRE
- **Type d'acte**: promesse_vente, compromis
- **Fichier**: `cs_preemption_locataire.md`
- **Variables**: locataire.nom

### Condition suspensive de vente d'un bien par l'acquéreur

- **ID**: `cs_vente_bien_acquereur`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: promesse_vente, compromis
- **Fichier**: `cs_vente_bien_acquereur.md`
- **Variables**: bien_a_vendre.adresse, condition.date_limite

### Condition suspensive d'obtention de permis de construire

- **ID**: `cs_permis_construire`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: promesse_vente, compromis
- **Fichier**: `cs_permis_construire.md`
- **Variables**: projet.description, projet.date_limite

