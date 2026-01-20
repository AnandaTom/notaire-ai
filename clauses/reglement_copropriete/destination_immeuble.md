{# ============================================================================
   CLAUSE: Destination de l'immeuble
   ID: destination_immeuble
   Catégorie: reglement_copropriete
   Type d'acte: reglement_copropriete
   Obligatoire: Oui
   Variables requises: 
   Source: Trame reglement copropriete EDD
   Date ajout: 2025-01-19
   ============================================================================ #}

L'immeuble est destiné principalement à l'habitation.

{% if destination.commerce_autorise %}
Toutefois, les lots situés au rez-de-chaussée peuvent être affectés à usage commercial, à l'exclusion de toute activité pouvant nuire à la tranquillité des occupants ou à la bonne tenue de l'immeuble.

Sont notamment interdits : les activités bruyantes, les commerces alimentaires de restauration rapide, les établissements recevant du public après 22h.
{% endif %}

Toute modification de la destination d'un lot devra être préalablement autorisée par l'assemblée générale des copropriétaires statuant à la majorité de l'article <<<VAR_START>>>{{ destination.majorite_modification | default('26') }}<<<VAR_END>>> de la loi du 10 juillet 1965.