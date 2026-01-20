{# ============================================================================
   CLAUSE: Information DPE classe F ou G
   ID: dpe_passoire
   Catégorie: diagnostics
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: diagnostics.dpe.classe_energie
   Source: Ajout - Loi Climat
   Date ajout: 2025-01-19
   ============================================================================ #}

{%- if diagnostics.dpe.classe_energie in ['F', 'G'] -%}

Le BENEFICIAIRE est informé que le bien présente une classe de performance énergétique <<<VAR_START>>>{{ diagnostics.dpe.classe_energie }}<<<VAR_END>>>.

Conformément à la loi Climat et Résilience du 22 août 2021, les logements classés G ne pourront plus être proposés à la location à compter du 1er janvier 2025, les logements classés F à compter du 1er janvier 2028, et les logements classés E à compter du 1er janvier 2034.

Le BENEFICIAIRE déclare avoir été informé de cette situation et des travaux de rénovation énergétique qui pourraient s'avérer nécessaires.

{%- endif -%}