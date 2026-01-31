{# Section: PROPRIÉTÉ JOUISSANCE — Transfert de propriété et jouissance #}
{# Applicable: Toutes catégories (copro, hors-copro, terrain) #}
{# Condition: Toujours présente (section fixe) #}

# Propriété jouissance

Le **BENEFICIAIRE** sera propriétaire des **BIENS** objet de la promesse le jour de la constatation de la vente en la forme authentique et il en aura la jouissance à compter du même jour par la prise de possession réelle, les **BIENS** devant être impérativement, à cette même date, libres de toute location ou occupation.

Le **PROMETTANT** déclare que les **BIENS** n'ont pas, avant ce jour, fait l'objet d'un congé pouvant donner lieu à l'exercice d'un droit de préemption.

{% if jouissance %}
{% if jouissance.date_entree != "signature" %}
Par exception, la jouissance sera reportée au {{ jouissance.date_entree | format_date }}.
{% endif %}

{% if jouissance.occupation_actuelle %}
Le **PROMETTANT** déclare que le bien est actuellement {{ jouissance.occupation_actuelle }}.
{% if jouissance.bail_en_cours %}
Un bail est en cours, consenti à {{ jouissance.bail_en_cours.locataire | default("un locataire") }}{% if jouissance.bail_en_cours.loyer %}, moyennant un loyer de {{ jouissance.bail_en_cours.loyer | format_nombre }} EUR {{ jouissance.bail_en_cours.periodicite | default("par mois") }}{% endif %}.
{% if jouissance.bail_en_cours.conge_delivre %}
Un congé a été délivré le {{ jouissance.bail_en_cours.date_conge | format_date }} pour le {{ jouissance.bail_en_cours.date_effet_conge | format_date }}.
{% endif %}
{% endif %}
{% endif %}

{% if jouissance.indemnite_occupation %}
En cas d'occupation par le **PROMETTANT** au-delà de la date de jouissance convenue, une indemnité d'occupation de {{ jouissance.indemnite_occupation | format_nombre }} EUR par jour sera due au **BENEFICIAIRE**.
{% endif %}
{% endif %}
