{FIRST_PAGE_HEADER_START}
{{ reference_acte }}
{{ initiales_notaire }}/

**Le {{ date_acte.day }} {{ date_acte.month|mois_en_lettres }} {{ date_acte.year }}**
**DONATION-PARTAGE**
**Par {{ donateur_1.civilite }} {{ donateur_1.prenom }} {{ donateur_1.nom|upper }}**
**Et {{ donateur_2.civilite }} {{ donateur_2.prenom }} {{ donateur_2.nom|upper }} née {{ donateur_2.nom_naissance|upper }}**
**Au profit de leurs {{ nombre_enfants_lettres }} enfants**
***************************************************************
{FIRST_PAGE_HEADER_END}

**L'AN {{ date_acte.year|nombre_en_lettres|upper }},**
**LE {{ date_acte.day|jour_en_lettres|upper }} {{ date_acte.month|mois_en_lettres|upper }}**
**À {{ donateur_1.adresse.ville|upper }} ({{ donateur_1.adresse.code_postal }}), {{ donateur_1.adresse.numero }} {{ donateur_1.adresse.voie }},**
**{{ notaire.civilite }} {{ notaire.prenom }} {{ notaire.nom|upper }}, Notaire au sein de la société par actions simplifiée dénommée « {{ notaire.nom_societe }} » titulaire d'un Office notarial situé à {{ notaire.office.ville|upper }} ({{ notaire.office.departement }}), {{ notaire.office.adresse }}, identifié sous le numéro CRPCEN {{ notaire.crpcen }},**

**EST ETABLIE LA PRESENTE DONATION-PARTAGE**

## IDENTIFICATION DES PARTIES

### DONATEURS

Monsieur {{ donateur_1.prenom }} {{ donateur_1.deuxieme_prenom }} **{{ donateur_1.nom|upper }}**, {{ donateur_1.profession }}, et Madame {{ donateur_2.prenom }} {{ donateur_2.deuxieme_prenom }} {{ donateur_2.troisieme_prenom }} **{{ donateur_2.nom_naissance|upper }}**, {{ donateur_2.profession }}, demeurant ensemble à {{ donateur_1.adresse.ville|upper }} ({{ donateur_1.adresse.code_postal }}) {{ donateur_1.adresse.numero }} {{ donateur_1.adresse.voie }}.