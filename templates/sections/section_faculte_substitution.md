{# ============================================================================
   SECTION FACULTE DE SUBSTITUTION

   Utilisation: {% include 'sections/section_faculte_substitution.md' %}
   Condition: Toujours inclure (gère les deux cas: avec ou sans substitution)

   Variables requises:
   - faculte_substitution.autorisee: true/false
   - faculte_substitution.conditions: Conditions de la substitution
   - faculte_substitution.delai_notification: Délai pour notifier (jours)
   - faculte_substitution.forme_notification: "LRAR" ou "acte"
   - faculte_substitution.restrictions: Restrictions éventuelles
   ============================================================================ #}

### FACULTE DE SUBSTITUTION

{% if faculte_substitution and faculte_substitution.autorisee %}

Le BENEFICIAIRE aura la faculté de se substituer, dans le bénéfice de la présente promesse, toute personne physique ou morale de son choix{% if faculte_substitution.restrictions %}, sous réserve des restrictions suivantes : {{ faculte_substitution.restrictions }}{% endif %}.

**Délai de notification** - Le BENEFICIAIRE devra notifier la substitution au PROMETTANT et au notaire soussigné au plus tard **{{ faculte_substitution.delai_notification | default(15) }} jours** avant la date de réalisation de la vente.

**Forme de la notification** - {% if faculte_substitution.forme_notification == "LRAR" %}La notification sera faite par lettre recommandée avec accusé de réception adressée au PROMETTANT et au notaire.{% else %}La notification sera faite par acte extrajudiciaire ou par déclaration au notaire soussigné.{% endif %}

**Contenu de la notification** - La notification devra comporter : l'identité complète du ou des substitués (état civil, adresse, profession) ; les conditions de financement du substitué ; l'acceptation expresse par le substitué des termes de la présente promesse.

{% if faculte_substitution.liberation_beneficiaire %}**Libération du BENEFICIAIRE** - En cas de substitution, le BENEFICIAIRE initial sera libéré de toutes ses obligations nées de la présente promesse, à compter de la notification de la substitution au PROMETTANT.{% else %}**Solidarité** - Le BENEFICIAIRE initial restera tenu solidairement avec le substitué de l'exécution des obligations résultant de la présente promesse jusqu'à la signature de l'acte authentique de vente.{% endif %}

{% if faculte_substitution.indemnite %}**Sort de l'indemnité d'immobilisation** - L'indemnité d'immobilisation versée par le BENEFICIAIRE initial sera {% if faculte_substitution.indemnite_transfert %}transférée au bénéfice du substitué, qui en deviendra créancier.{% else %}conservée au nom du BENEFICIAIRE initial qui pourra en obtenir le remboursement auprès du substitué.{% endif %}{% endif %}

**Responsabilité** - Le BENEFICIAIRE initial garantit le PROMETTANT : de la capacité et de la solvabilité du substitué ; de l'acceptation par le substitué de toutes les clauses et conditions de la présente promesse ; du paiement de l'intégralité du prix et des frais aux lieu et date convenus.

{% if faculte_substitution.sci_autorisee %}**Substitution par une SCI** - Il est expressément convenu que le BENEFICIAIRE pourra se substituer une société civile immobilière (SCI), même en cours de constitution, dont il serait associé. Dans ce cas, le BENEFICIAIRE devra justifier de l'immatriculation de la SCI avant la signature de l'acte authentique.{% endif %}

{% else %}

Le BENEFICIAIRE ne pourra se substituer, dans le bénéfice de la présente promesse, aucune personne physique ou morale. En conséquence, seul le BENEFICIAIRE désigné aux présentes, ou ses ayants droit en cas de décès, pourra lever l'option et acquérir le bien objet de la présente promesse.

{% if faculte_substitution and faculte_substitution.exception_sci %}*Exception :* Toutefois, par dérogation à ce qui précède, le BENEFICIAIRE pourra se substituer une société civile immobilière dont il serait l'associé unique ou majoritaire, à condition : d'en informer le PROMETTANT au moins {{ faculte_substitution.delai_exception | default(30) }} jours avant la date de réalisation ; de fournir les statuts de ladite société et son extrait Kbis ; de demeurer solidairement responsable de l'exécution des obligations.{% endif %}

{% endif %}

