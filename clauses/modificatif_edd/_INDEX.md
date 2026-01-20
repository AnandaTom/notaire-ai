# Clauses - modificatif_edd

Total: 5 clauses

## Liste des clauses

### Autorisation de l'assemblée générale

- **ID**: `autorisation_ag`
- **Statut**: 🔴 OBLIGATOIRE
- **Type d'acte**: modificatif_edd
- **Fichier**: `autorisation_ag.md`
- **Variables**: assemblee_generale.date, assemblee_generale.resolution_numero, assemblee_generale.objet, assemblee_generale.majorite_requise, assemblee_generale.vote

### Certificat de non-recours

- **ID**: `certificat_non_recours`
- **Statut**: 🔴 OBLIGATOIRE
- **Type d'acte**: modificatif_edd
- **Fichier**: `certificat_non_recours.md`
- **Variables**: assemblee_generale.certificat_non_recours.date, assemblee_generale.certificat_non_recours.delivre_par

### Historique des modificatifs antérieurs

- **ID**: `historique_modificatifs`
- **Statut**: 🔴 OBLIGATOIRE
- **Type d'acte**: modificatif_edd
- **Fichier**: `historique_modificatifs.md`
- **Variables**: edd_origine, historique_modificatifs

### Division d'un lot en plusieurs

- **ID**: `division_lot`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: modificatif_edd
- **Fichier**: `division_lot.md`
- **Variables**: modifications

### Réunion de plusieurs lots en un seul

- **ID**: `reunion_lots`
- **Statut**: 🟢 Optionnelle
- **Type d'acte**: modificatif_edd
- **Fichier**: `reunion_lots.md`
- **Variables**: modifications

