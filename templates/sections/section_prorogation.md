{# ============================================================================
   SECTION PROROGATION DE LA PROMESSE

   Utilisation: {% include 'sections/section_prorogation.md' %}
   Condition: {% if delais.prorogation %}

   Variables requises:
   - delais.prorogation.possible: true/false
   - delais.prorogation.duree_max: Durée maximum en jours
   - delais.prorogation.conditions: Conditions de prorogation
   - delais.prorogation.forme: "avenant", "LRAR", etc.
   ============================================================================ #}

### PROROGATION

{% if delais.prorogation and delais.prorogation.possible %}

Les parties conviennent que la présente promesse pourra être prorogée par avenant, dans les conditions suivantes :

**Durée de prorogation** - {% if delais.prorogation.duree_max %}La prorogation ne pourra excéder une durée de **{{ delais.prorogation.duree_max }} jours** à compter de la date d'expiration initiale de la promesse.{% else %}La durée de la prorogation sera librement convenue entre les parties.{% endif %}{% if delais.prorogation.prorogations_successives %} Plusieurs prorogations successives pourront être consenties, dans la limite d'une durée totale de {{ delais.prorogation.duree_totale_max | default(180) }} jours à compter de la date de signature des présentes.{% endif %}

**Conditions de la prorogation** - La prorogation sera subordonnée :
{% if delais.prorogation.accord_promettant %}- À l'accord exprès du PROMETTANT ;
{% endif %}{% if delais.prorogation.accord_beneficiaire %}- À l'accord exprès du BENEFICIAIRE ;
{% endif %}{% if delais.prorogation.motif_justifie %}- À la justification d'un motif légitime (retard bancaire, délai administratif, etc.) ;
{% endif %}{% if delais.prorogation.indemnite_supplementaire %}- Au versement d'une indemnité complémentaire de **{{ delais.prorogation.indemnite_supplementaire | format_nombre }} euros** ;
{% endif %}{% if delais.prorogation.conditions_specifiques %}
*Conditions particulières :* {{ delais.prorogation.conditions_specifiques }}
{% endif %}

**Forme de la prorogation** - {% if delais.prorogation.forme == "avenant" %}La prorogation sera constatée par **avenant** à la présente promesse, établi par le notaire soussigné et signé par les deux parties.{% elif delais.prorogation.forme == "LRAR" %}La prorogation pourra être sollicitée par lettre recommandée avec accusé de réception adressée à l'autre partie avec copie au notaire, au moins **{{ delais.prorogation.delai_demande | default(15) }} jours** avant l'expiration de la promesse. L'acceptation devra être notifiée dans les mêmes formes dans un délai de **{{ delais.prorogation.delai_reponse | default(8) }} jours**.{% else %}La prorogation sera constatée par tout acte écrit signé des deux parties.{% endif %}

**Effets de la prorogation** - En cas de prorogation : toutes les clauses et conditions de la présente promesse resteront applicables pendant la durée de la prorogation ;{% if delais.prorogation.conditions_suspensives_prolongees %} les délais de réalisation des conditions suspensives seront prorogés d'une durée équivalente ;{% endif %}{% if delais.prorogation.indemnite_conservee %} l'indemnité d'immobilisation restera acquise au séquestre ;{% endif %} la nouvelle date limite de réalisation sera expressément mentionnée dans l'avenant.

{% else %}

Les parties conviennent expressément qu'**aucune prorogation** de la présente promesse ne sera possible. À défaut de réalisation de la vente dans le délai imparti, la promesse sera caduque de plein droit et les parties seront déliées de tout engagement, sous réserve des dispositions relatives au sort de l'indemnité d'immobilisation.

{% if delais.prorogation and delais.prorogation.exception_force_majeure %}
*Exception :* Toutefois, en cas de force majeure rendant impossible la réalisation de la vente dans le délai imparti, les parties pourront convenir d'une prorogation limitée à la durée de l'empêchement, majorée de {{ delais.prorogation.delai_supplementaire | default(30) }} jours. Constituent notamment des cas de force majeure : les catastrophes naturelles, les décisions administratives suspendant les activités notariales, les épidémies entraînant la fermeture des services publics.
{% endif %}

{% endif %}

