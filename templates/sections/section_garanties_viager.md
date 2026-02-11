{# Section Garanties Viager — Privilège, Clause pénale, Résolutoire #}
{# Activée si: prix.type_vente == "viager" #}

# GARANTIES – PRIVILÈGE DU VENDEUR

{% if garanties and garanties.privilege %}
## Inscription du privilège

Le crédirentier bénéficiera de l'inscription d'un **privilège de vendeur** sur le bien objet des présentes :
- **Durée initiale** : {{ garanties.privilege.duree_initiale_annees | default(15) }} ans.
{% if garanties.privilege.renouvelable %}
- Le privilège sera **renouvelable** à son expiration, aux frais du débirentier.
{% endif %}
- **Rang** : {{ garanties.privilege.rang | default("premier rang") }}.

Les frais de renouvellement de l'inscription du privilège seront à la charge du **débirentier**.
{% endif %}

{% if garanties and garanties.solidarite_acquereurs %}
## Solidarité des acquéreurs successifs

En cas de revente du bien, tous les acquéreurs successifs seront tenus **solidairement** au service de la rente viagère. Cette solidarité ne pourra être levée que par le consentement exprès du crédirentier.
{% endif %}

## Clause pénale – Retard de paiement

{% if prix.clause_penale %}
En cas de retard dans le paiement de la rente ou de toute autre somme due en vertu du présent acte :

- Les sommes dues porteront intérêt au **taux légal majoré de {{ prix.clause_penale.taux_majoration | default(3) }} points**.
{% if prix.clause_penale.automatique %}
- Les intérêts de retard courront **de plein droit**, sans qu'il soit besoin d'une mise en demeure préalable.
{% else %}
- Les intérêts de retard courront à compter de la mise en demeure adressée par le crédirentier.
{% endif %}
- Les intérêts courront jusqu'à complet paiement des sommes dues.
{% else %}
En cas de retard dans le paiement de la rente, les sommes dues porteront intérêt au **taux légal majoré de trois points**, de plein droit et sans mise en demeure préalable.
{% endif %}

## Clause résolutoire

À défaut de paiement de la rente pendant une durée de **deux mois** consécutifs, le crédirentier pourra, s'il le souhaite, poursuivre la **résolution** du présent contrat.

Dans ce cas :
- Les sommes versées au titre du bouquet et des arrérages de rente resteront **acquises** au crédirentier à titre de dommages et intérêts.
- Le crédirentier retrouvera la **pleine propriété** du bien, libre de toute charge.
- Le débirentier devra **libérer les lieux** dans un délai d'un mois à compter de la signification de la résolution.

{% if garanties and garanties.transfert_possible and garanties.transfert_possible.autorise %}
## Transfert du privilège

Le débirentier pourra, avec l'accord du crédirentier, transférer le privilège sur un autre bien immobilier, sous réserve que la valeur de ce bien soit **{{ garanties.transfert_possible.condition_valeur | default("supérieure ou égale") }}** à celle du bien objet des présentes.
{% endif %}
