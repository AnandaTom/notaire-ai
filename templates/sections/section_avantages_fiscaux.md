## Avantages fiscaux liés à un engagement de location

{% if avantages_fiscaux %}

{% if avantages_fiscaux.dispositif %}
Le VENDEUR déclare bénéficier du dispositif fiscal <<<VAR_START>>>{{ avantages_fiscaux.dispositif }}<<<VAR_END>>> pour ce bien.

{% if avantages_fiscaux.duree_engagement %}
- **Durée d'engagement** : <<<VAR_START>>>{{ avantages_fiscaux.duree_engagement }}<<<VAR_END>>> ans
{% endif %}

{% if avantages_fiscaux.date_debut %}
- **Date de début** : <<<VAR_START>>>{{ avantages_fiscaux.date_debut }}<<<VAR_END>>>
{% endif %}

{% if avantages_fiscaux.date_fin %}
- **Date de fin d'engagement** : <<<VAR_START>>>{{ avantages_fiscaux.date_fin }}<<<VAR_END>>>
{% endif %}

{% if avantages_fiscaux.plafond_loyer %}
- **Plafond de loyer applicable** : <<<VAR_START>>>{{ avantages_fiscaux.plafond_loyer | format_nombre }}<<<VAR_END>>> EUR/m²/mois
{% endif %}

{% if avantages_fiscaux.plafond_ressources %}
- **Plafond de ressources des locataires** : {{ avantages_fiscaux.plafond_ressources }}
{% endif %}

{% if avantages_fiscaux.transfert_engagement %}
### Transfert de l'engagement

L'ACQUÉREUR s'engage à reprendre l'engagement de location souscrit par le VENDEUR et à respecter les conditions du dispositif {{ avantages_fiscaux.dispositif }} pour la durée restante, soit jusqu'au <<<VAR_START>>>{{ avantages_fiscaux.date_fin }}<<<VAR_END>>>.

Le non-respect de cet engagement pourrait entraîner la remise en cause de l'avantage fiscal et l'application de pénalités.
{% else %}
L'ACQUÉREUR est informé de l'existence de cet engagement mais ne souhaite pas le reprendre. Les conséquences fiscales seront supportées par le VENDEUR.
{% endif %}

{% else %}
Le VENDEUR déclare ne pas bénéficier actuellement d'un dispositif fiscal lié à un engagement de location (Pinel, Denormandie, etc.).
{% endif %}

{% endif %}

{% if ptz %}

## Prêt à Taux Zéro (PTZ)

{% if ptz.eligible %}
L'ACQUÉREUR remplit les conditions d'éligibilité au Prêt à Taux Zéro.

{% if ptz.montant_max %}
- **Montant maximum empruntable** : <<<VAR_START>>>{{ ptz.montant_max | format_nombre }}<<<VAR_END>>> EUR
{% endif %}

{% if ptz.zone %}
- **Zonage** : Zone {{ ptz.zone }}
{% endif %}

Les conditions détaillées et les modalités d'obtention sont disponibles auprès des établissements bancaires agréés.
{% else %}
Le bien ou l'ACQUÉREUR ne remplit pas les conditions d'éligibilité au Prêt à Taux Zéro.
{% endif %}

{% endif %}
