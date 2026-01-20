{# ============================================================================
   CLAUSE: Déclarations urbanistiques standard
   ID: declaration_urbanisme_standard
   Catégorie: urbanisme
   Type d'acte: promesse_vente, compromis, vente
   Obligatoire: Oui
   Variables requises: 
   Source: Trame vente lots de copropriété
   Date ajout: 2025-01-19
   ============================================================================ #}

Le PROMETTANT déclare qu'à sa connaissance :
- Le bien n'a fait l'objet d'aucune procédure de péril, d'insalubrité ou de mise en demeure au titre de la sécurité des équipements communs,
- Le bien n'est pas situé dans le périmètre d'une opération d'aménagement,
- Il n'existe pas de projet d'expropriation ou d'alignement,
- Le bien n'est pas situé dans un secteur sauvegardé ou de protection.

{% if urbanisme.note_urbanisme.date %}
Une note d'urbanisme a été délivrée le <<<VAR_START>>>{{ urbanisme.note_urbanisme.date | format_date }}<<<VAR_END>>> et demeure annexée.
{% endif %}