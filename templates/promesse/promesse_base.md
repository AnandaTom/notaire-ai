{# Template de Base pour toutes les Promesses de Vente #}
{# Ce template définit la structure commune, à étendre par les templates spécialisés #}

{# ============================================= #}
{# MACROS UTILITAIRES                           #}
{# ============================================= #}

{% macro format_date(date) %}
{% if date %}{{ date | format_date_fr }}{% else %}[DATE À COMPLÉTER]{% endif %}
{% endmacro %}

{% macro format_montant(montant) %}
{% if montant %}<<<VAR_START>>>{{ montant | format_nombre }}<<<VAR_END>>>{% else %}[MONTANT À COMPLÉTER]{% endif %}
{% endmacro %}

{% macro format_personne(p) %}
{% if p.civilite %}{{ p.civilite }} {% endif %}{{ p.nom | upper }} {{ p.prenoms }}{% if p.nom_naissance and p.nom_naissance != p.nom %}, née {{ p.nom_naissance | upper }}{% endif %}
{% endmacro %}

{# ============================================= #}
{# STRUCTURE DU DOCUMENT                        #}
{# ============================================= #}

{% block titre %}
# PROMESSE UNILATÉRALE DE VENTE
{% endblock %}

---

**Référence**: {{ reference | default('[RÉFÉRENCE]') }}

**Date**: {{ format_date(date_promesse) }}

**Type**: {% block type_promesse %}base{% endblock %}

---

{% block contenu_principal %}
{# À définir dans les templates spécialisés #}
{% endblock %}

---

{% block pied_page %}
*Document généré par Notomai - {{ now().strftime('%d/%m/%Y %H:%M') }}*
{% endblock %}
