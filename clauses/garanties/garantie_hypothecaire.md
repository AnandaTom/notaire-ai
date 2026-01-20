{# ============================================================================
   CLAUSE: Garantie hypothécaire
   ID: garantie_hypothecaire
   Catégorie: garanties
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: 
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

Le PROMETTANT déclare que le bien n'est grevé d'aucune inscription hypothécaire, privilège ou autre charge.

{% if hypotheques_existantes %}
Toutefois, il existe actuellement les inscriptions suivantes :
{% for hypo in hypotheques_existantes %}
- <<<VAR_START>>>{{ hypo.type }}<<<VAR_END>>> au profit de <<<VAR_START>>>{{ hypo.beneficiaire }}<<<VAR_END>>>, inscrite le <<<VAR_START>>>{{ hypo.date_inscription }}<<<VAR_END>>>, pour un montant de <<<VAR_START>>>{{ hypo.montant | format_nombre }}<<<VAR_END>>> EUR.
{% endfor %}

Le PROMETTANT s'engage à faire radier ces inscriptions au plus tard le jour de la réitération authentique des présentes, les fonds nécessaires étant prélevés sur le prix de vente.
{% endif %}