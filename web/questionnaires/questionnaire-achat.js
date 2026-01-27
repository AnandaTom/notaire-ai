/**
 * Script spécifique pour le questionnaire achat d'un bien
 * Gère les champs conditionnels additionnels
 */

document.addEventListener('DOMContentLoaded', () => {
    // Situation matrimoniale acheteur 1 -> Conjoint
    const situationSelect1 = document.getElementById('acheteur1_situation');
    if (situationSelect1) {
        situationSelect1.addEventListener('change', (e) => {
            const showConjoint = ['marie', 'pacse'].includes(e.target.value);
            document.getElementById('conjoint1_details')?.classList.toggle('visible', showConjoint);
        });
    }

    // Situation matrimoniale acheteur 2 -> Conjoint
    const situationSelect2 = document.getElementById('acheteur2_situation');
    if (situationSelect2) {
        situationSelect2.addEventListener('change', (e) => {
            const showConjoint = ['marie', 'pacse'].includes(e.target.value);
            document.getElementById('conjoint2_details')?.classList.toggle('visible', showConjoint);
        });
    }

    // Acquisition par société
    document.querySelectorAll('input[name="acquisition_societe"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('societe_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Prêt bancaire
    document.querySelectorAll('input[name="pret_bancaire"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('pret_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Prêt employeur
    document.querySelectorAll('input[name="pret_employeur"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('pret_employeur_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // PEL/CEL
    document.querySelectorAll('input[name="pel_cel"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('pel_cel_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Prêt à Taux Zéro
    document.querySelectorAll('input[name="pret_taux_zero"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('ptz_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Avantage fiscal
    document.querySelectorAll('input[name="avantage_fiscal"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('avantage_fiscal_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Donation
    document.querySelectorAll('input[name="donation"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('donation_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Bien en location
    document.querySelectorAll('input[name="bien_loue"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('location_details')?.classList.toggle('visible', e.target.value === 'oui');
        });
    });
});

// Override collectFormData pour achat
const originalCollectFormData = typeof collectFormData === 'function' ? collectFormData : null;

function collectFormDataAchat() {
    const formEl = document.getElementById('questionnaireForm');
    const formDataObj = new FormData(formEl);

    const data = {
        type_questionnaire: CONFIG.type,
        date_soumission: new Date().toISOString(),
        acheteurs: [],
        coordonnees: {},
        modalites_juridiques: {},
        financement: {},
        projets: {},
        observations: ''
    };

    // Acheteur 1
    const acheteur1 = {
        civilite: formDataObj.get('acheteur1_civilite'),
        nom: formDataObj.get('acheteur1_nom'),
        nom_naissance: formDataObj.get('acheteur1_nom_naissance'),
        prenoms: formDataObj.get('acheteur1_prenoms'),
        date_naissance: formDataObj.get('acheteur1_date_naissance'),
        lieu_naissance: formDataObj.get('acheteur1_lieu_naissance'),
        nationalite: formDataObj.get('acheteur1_nationalite'),
        profession: formDataObj.get('acheteur1_profession'),
        situation_matrimoniale: formDataObj.get('acheteur1_situation'),
        quote_part: formDataObj.get('acheteur1_quote_part')
    };

    // Si marié ou pacsé, ajouter les infos du conjoint
    if (['marie', 'pacse'].includes(acheteur1.situation_matrimoniale)) {
        acheteur1.conjoint = {
            civilite: formDataObj.get('conjoint1_civilite'),
            nom: formDataObj.get('conjoint1_nom'),
            prenoms: formDataObj.get('conjoint1_prenoms'),
            date_naissance: formDataObj.get('conjoint1_date_naissance'),
            lieu_naissance: formDataObj.get('conjoint1_lieu_naissance'),
            regime_matrimonial: formDataObj.get('conjoint1_regime'),
            date_mariage: formDataObj.get('conjoint1_date_mariage'),
            lieu_mariage: formDataObj.get('conjoint1_lieu_mariage')
        };
    }
    data.acheteurs.push(acheteur1);

    // Acheteur 2 (si renseigné)
    if (formDataObj.get('acheteur2_nom')) {
        const acheteur2 = {
            civilite: formDataObj.get('acheteur2_civilite'),
            nom: formDataObj.get('acheteur2_nom'),
            nom_naissance: formDataObj.get('acheteur2_nom_naissance'),
            prenoms: formDataObj.get('acheteur2_prenoms'),
            date_naissance: formDataObj.get('acheteur2_date_naissance'),
            lieu_naissance: formDataObj.get('acheteur2_lieu_naissance'),
            nationalite: formDataObj.get('acheteur2_nationalite'),
            profession: formDataObj.get('acheteur2_profession'),
            situation_matrimoniale: formDataObj.get('acheteur2_situation'),
            quote_part: formDataObj.get('acheteur2_quote_part')
        };

        if (['marie', 'pacse'].includes(acheteur2.situation_matrimoniale)) {
            acheteur2.conjoint = {
                civilite: formDataObj.get('conjoint2_civilite'),
                nom: formDataObj.get('conjoint2_nom'),
                prenoms: formDataObj.get('conjoint2_prenoms'),
                date_naissance: formDataObj.get('conjoint2_date_naissance'),
                lieu_naissance: formDataObj.get('conjoint2_lieu_naissance'),
                regime_matrimonial: formDataObj.get('conjoint2_regime'),
                date_mariage: formDataObj.get('conjoint2_date_mariage'),
                lieu_mariage: formDataObj.get('conjoint2_lieu_mariage')
            };
        }
        data.acheteurs.push(acheteur2);
    }

    // Coordonnées
    data.coordonnees = {
        adresse: formDataObj.get('adresse'),
        code_postal: formDataObj.get('code_postal'),
        ville: formDataObj.get('ville'),
        tel_portable: formDataObj.get('tel_portable'),
        tel_domicile: formDataObj.get('tel_domicile'),
        email: formDataObj.get('email')
    };

    // Modalités juridiques
    data.modalites_juridiques = {
        acquisition_societe: formDataObj.get('acquisition_societe'),
        denomination_societe: formDataObj.get('denomination_societe'),
        forme_societe: formDataObj.get('forme_societe'),
        siege_societe: formDataObj.get('siege_societe'),
        rcs_societe: formDataObj.get('rcs_societe'),
        representant_societe: formDataObj.get('representant_societe'),
        qualite_representant: formDataObj.get('qualite_representant')
    };

    // Financement
    data.financement = {
        pret_bancaire: formDataObj.get('pret_bancaire'),
        montant_pret: formDataObj.get('montant_pret'),
        duree_pret: formDataObj.get('duree_pret'),
        taux_pret: formDataObj.get('taux_pret'),
        banque_pret: formDataObj.get('banque_pret'),
        pret_employeur: formDataObj.get('pret_employeur'),
        montant_pret_employeur: formDataObj.get('montant_pret_employeur'),
        employeur: formDataObj.get('employeur'),
        pel_cel: formDataObj.get('pel_cel'),
        montant_pel_cel: formDataObj.get('montant_pel_cel'),
        pret_taux_zero: formDataObj.get('pret_taux_zero'),
        montant_ptz: formDataObj.get('montant_ptz'),
        apport_personnel: formDataObj.get('apport_personnel'),
        origine_apport: formDataObj.get('origine_apport'),
        avantage_fiscal: formDataObj.get('avantage_fiscal'),
        type_avantage_fiscal: formDataObj.get('type_avantage_fiscal'),
        donation: formDataObj.get('donation'),
        montant_donation: formDataObj.get('montant_donation'),
        donateur: formDataObj.get('donateur')
    };

    // Projets
    data.projets = {
        residence_principale: formDataObj.get('residence_principale'),
        bien_loue: formDataObj.get('bien_loue'),
        locataire_actuel: formDataObj.get('locataire_actuel'),
        montant_loyer: formDataObj.get('montant_loyer'),
        date_fin_bail: formDataObj.get('date_fin_bail'),
        vente_bien_actuel: formDataObj.get('vente_bien_actuel'),
        adresse_bien_actuel: formDataObj.get('adresse_bien_actuel'),
        statut_vente_actuel: formDataObj.get('statut_vente_actuel'),
        montant_vente_actuel: formDataObj.get('montant_vente_actuel')
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
    window.collectFormData = collectFormDataAchat;
}
