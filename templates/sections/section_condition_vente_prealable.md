{# ============================================================================
   SECTION CONDITION SUSPENSIVE - VENTE D'UN BIEN PREALABLE

   Utilisation: {% include 'sections/section_condition_vente_prealable.md' %}
   Condition: {% if conditions_suspensives.vente_bien_prealable %}

   Variables requises:
   - conditions_suspensives.vente_bien_prealable.existe: true/false
   - conditions_suspensives.vente_bien_prealable.description_bien: Description du bien à vendre
   - conditions_suspensives.vente_bien_prealable.adresse: Adresse du bien
   - conditions_suspensives.vente_bien_prealable.date_limite: Date limite de réalisation
   - conditions_suspensives.vente_bien_prealable.delai_notification: Délai pour notifier la vente (jours)
   - conditions_suspensives.vente_bien_prealable.prix_minimum: Prix minimum attendu (optionnel)
   ============================================================================ #}

**Condition suspensive de vente d'un bien préalable** - La présente promesse est conclue sous la condition suspensive de la vente par {{ "le BENEFICIAIRE" if conditions_suspensives.vente_bien_prealable.partie == "beneficiaire" else "le PROMETTANT" }} du bien lui appartenant ci-après désigné :

*Désignation du bien à vendre :* {{ conditions_suspensives.vente_bien_prealable.description_bien | default("Un bien immobilier") }}{% if conditions_suspensives.vente_bien_prealable.adresse %}, situé à : {{ conditions_suspensives.vente_bien_prealable.adresse }}{% endif %}{% if conditions_suspensives.vente_bien_prealable.prix_minimum %}. Le prix de vente devra être au minimum de **{{ conditions_suspensives.vente_bien_prealable.prix_minimum | format_nombre }} euros** ({{ conditions_suspensives.vente_bien_prealable.prix_minimum | montant_en_lettres }}).{% endif %}

*Délai de réalisation :* Cette condition devra être réalisée au plus tard le **{{ conditions_suspensives.vente_bien_prealable.date_limite | default("(date à préciser)") }}**.

*Notification :* {{ "Le BENEFICIAIRE" if conditions_suspensives.vente_bien_prealable.partie == "beneficiaire" else "Le PROMETTANT" }} devra notifier la réalisation de cette condition au notaire soussigné dans un délai de **{{ conditions_suspensives.vente_bien_prealable.delai_notification | default(8) }} jours** suivant la signature de l'acte de vente du bien ci-dessus désigné, en justifiant de ladite vente par tout document utile.

{% if conditions_suspensives.vente_bien_prealable.compromis_signe %}*Situation actuelle :* {{ "Le BENEFICIAIRE" if conditions_suspensives.vente_bien_prealable.partie == "beneficiaire" else "Le PROMETTANT" }} déclare qu'un compromis de vente a été signé le {{ conditions_suspensives.vente_bien_prealable.date_compromis | default("(date)") }} avec {{ conditions_suspensives.vente_bien_prealable.acquereur | default("un acquéreur") }} pour un prix de {{ conditions_suspensives.vente_bien_prealable.prix_compromis | default(0) | format_nombre }} euros.{% endif %}

*Défaillance de la condition :* À défaut de réalisation de cette condition dans le délai imparti, la présente promesse sera caduque de plein droit ; l'indemnité d'immobilisation, si elle a été versée, sera restituée au BENEFICIAIRE ; aucune des parties ne pourra prétendre à une quelconque indemnité de l'autre.

{% if conditions_suspensives.vente_bien_prealable.renonciation_possible %}*Renonciation :* Le BENEFICIAIRE se réserve la faculté de renoncer au bénéfice de cette condition suspensive, sous réserve d'en informer le PROMETTANT et le notaire par lettre recommandée avec accusé de réception, dans un délai de {{ conditions_suspensives.vente_bien_prealable.delai_renonciation | default(15) }} jours avant la date limite de réalisation.{% endif %}

