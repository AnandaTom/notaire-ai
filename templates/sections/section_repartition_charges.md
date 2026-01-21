## Dispositions légales et réglementaires sur la répartition des charges

{% if copropriete %}

Conformement aux dispositions de l'article 6-2 du decret n° 67-223 du 17 mars 1967, il est rappele les dispositions suivantes :

### Répartition des charges de copropriété

Les charges sont reparties entre le VENDEUR et l'ACQUEREUR de la maniere suivante :

{% if copropriete.repartition_charges %}
- **Provision sur charges** : Le VENDEUR reste redevable des provisions exigibles avant la date de vente.
- **Regularisation de charges** : Les regularisations de charges sont a la charge du proprietaire au moment de l'approbation des comptes.
{% else %}
- Les provisions sur charges courantes sont dues par le proprietaire au jour de l'exigibilite.
- Les provisions sur travaux sont dues par le proprietaire au jour du vote de ces travaux en assemblee generale.
{% endif %}

### Fonds de travaux

{% if copropriete.fonds_travaux %}
Le fonds de travaux prevu a l'article 14-2 de la loi du 10 juillet 1965 est attache au lot et suit le lot en cas de vente.
Le montant verse par le VENDEUR au fonds de travaux n'est pas remboursable.
{% endif %}

{% endif %}
