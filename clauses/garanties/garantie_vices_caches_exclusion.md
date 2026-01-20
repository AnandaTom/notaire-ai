{# ============================================================================
   CLAUSE: Exclusion de garantie des vices cachés
   ID: garantie_vices_caches_exclusion
   Catégorie: garanties
   Type d'acte: vente
   Obligatoire: Non
   Variables requises: 
   Source: Clause standard vente particulier à particulier
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if vendeur.non_professionnel == true -%}

Le BENEFICIAIRE prendra le bien dans l'état où il se trouvera le jour de l'entrée en jouissance, sans recours contre le PROMETTANT pour quelque cause que ce soit, notamment en raison :
- des vices apparents,
- des vices cachés.

Cette exonération de garantie ne s'applique pas si le PROMETTANT a la qualité de vendeur professionnel ou s'il avait connaissance des vices.

{%- endif -%}