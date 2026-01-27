/**
 * Script spécifique pour le questionnaire vente maison
 * Gère les champs conditionnels additionnels
 */

document.addEventListener('DOMContentLoaded', () => {
    // Lotissement -> Association syndicale
    document.querySelectorAll('input[name="lotissement"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('lotissement_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Mur séparatif
    document.querySelectorAll('input[name="mur_separatif"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('mur_separatif_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Servitudes
    document.querySelectorAll('input[name="servitudes"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('servitudes_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Assainissement individuel
    document.querySelectorAll('input[name="assainissement_individuel"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('assainissement_individuel_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Construction propre
    document.querySelectorAll('input[name="construction_propre"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('construction_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Citerne gaz
    document.querySelectorAll('input[name="citerne_gaz"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('citerne_gaz_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Récupération eau de pluie
    document.querySelectorAll('input[name="recuperation_pluie"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('recuperation_pluie_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Procédures judiciaires
    document.querySelectorAll('input[name="procedures_judiciaires"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('procedures_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });
});

// Override collectFormData pour maison
const originalCollectFormData = typeof collectFormData === 'function' ? collectFormData : null;

function collectFormDataMaison() {
    const formEl = document.getElementById('questionnaireForm');
    const formDataObj = new FormData(formEl);

    const data = {
        type_questionnaire: CONFIG.type,
        date_soumission: new Date().toISOString(),
        vendeurs: [],
        coordonnees: {},
        terrain: {},
        batiment: {},
        contrats: {},
        prets: {},
        fiscal: {},
        observations: ''
    };

    // Vendeur 1
    const vendeur1 = {
        civilite: formDataObj.get('vendeur1_civilite'),
        nom: formDataObj.get('vendeur1_nom'),
        prenoms: formDataObj.get('vendeur1_prenoms'),
        date_naissance: formDataObj.get('vendeur1_date_naissance'),
        lieu_naissance: formDataObj.get('vendeur1_lieu_naissance'),
        nationalite: formDataObj.get('vendeur1_nationalite'),
        profession: formDataObj.get('vendeur1_profession'),
        situation_matrimoniale: formDataObj.get('vendeur1_situation'),
        residence_fiscale: formDataObj.get('vendeur1_residence_fiscale')
    };
    data.vendeurs.push(vendeur1);

    // Coordonnées
    data.coordonnees = {
        adresse: formDataObj.get('adresse'),
        code_postal: formDataObj.get('code_postal'),
        ville: formDataObj.get('ville'),
        tel_portable: formDataObj.get('tel_portable'),
        tel_domicile: formDataObj.get('tel_domicile'),
        email: formDataObj.get('email'),
        iban: formDataObj.get('iban')?.replace(/\s/g, ''),
        bic: formDataObj.get('bic'),
        banque: formDataObj.get('banque')
    };

    // Terrain
    data.terrain = {
        lotissement: formDataObj.get('lotissement'),
        association_syndicale: formDataObj.get('association_syndicale'),
        copropriete_horizontale: formDataObj.get('copropriete_horizontale'),
        bornage: formDataObj.get('bornage'),
        terrain_attenant: formDataObj.get('terrain_attenant'),
        terrain_boise: formDataObj.get('terrain_boise'),
        mur_separatif: formDataObj.get('mur_separatif'),
        terrain_pente: formDataObj.get('terrain_pente'),
        activites_polluantes: formDataObj.get('activites_polluantes'),
        zone_inondable: formDataObj.get('zone_inondable'),
        servitudes: formDataObj.get('servitudes'),
        details_servitudes: formDataObj.get('details_servitudes')
    };

    // Bâtiment
    data.batiment = {
        assainissement_individuel: formDataObj.get('assainissement_individuel'),
        tout_egout: formDataObj.get('tout_egout'),
        construction_propre: formDataObj.get('construction_propre'),
        travaux_moins_10_ans: formDataObj.get('travaux_moins_10_ans'),
        assurance_dommage_ouvrage: formDataObj.get('assurance_dommage_ouvrage'),
        cuve_mazout: formDataObj.get('cuve_mazout'),
        gaz_ville: formDataObj.get('gaz_ville'),
        citerne_gaz: formDataObj.get('citerne_gaz'),
        recuperation_pluie: formDataObj.get('recuperation_pluie')
    };

    // Contrats
    data.contrats = {
        maison_libre: formDataObj.get('maison_libre'),
        louee_precedemment: formDataObj.get('louee_precedemment'),
        contrat_affichage: formDataObj.get('contrat_affichage'),
        contrat_alarme: formDataObj.get('contrat_alarme'),
        autres_contrats: formDataObj.get('autres_contrats'),
        equipements_garantie: formDataObj.get('equipements_garantie')
    };

    // Prêts
    data.prets = {
        saisie_immobiliere: formDataObj.get('saisie_immobiliere'),
        prets_hypothecaires: formDataObj.get('prets_hypothecaires'),
        details_prets: formDataObj.get('details_prets'),
        credit_relais: formDataObj.get('credit_relais')
    };

    // Fiscal
    data.fiscal = {
        residence_principale: formDataObj.get('residence_principale'),
        avantage_fiscal: formDataObj.get('avantage_fiscal'),
        sinistre_avant: formDataObj.get('sinistre_avant'),
        sinistre_apres: formDataObj.get('sinistre_apres'),
        motivation_vente: formDataObj.getAll('motivation_vente')
    };

    data.observations = formDataObj.get('observations');

    data.metadata = {
        user_agent: navigator.userAgent,
        rgpd_consent: formDataObj.get('rgpd_consent') === 'on',
        rgpd_consent_date: new Date().toISOString()
    };

    return data;
}

// Remplacer la fonction de collecte
if (typeof window !== 'undefined') {
    window.collectFormData = collectFormDataMaison;
}
