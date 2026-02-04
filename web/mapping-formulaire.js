/**
 * Mapping Formulaire → Pipeline
 *
 * Traduit les données des formulaires clients (vendeur/acquéreur)
 * vers le format JSON attendu par le moteur de génération d'actes.
 *
 * Référence: schemas/variables_promesse_vente.json et schemas/variables_vente.json
 */

/**
 * Point d'entrée principal.
 * @param {Object} formData - Données déchiffrées du formulaire
 * @param {string} typePartie - 'vendeur_appartement', 'vendeur_maison', 'acquereur', 'vendeur'
 * @returns {Object} Données au format pipeline
 */
function mapFormToPipeline(formData, typePartie) {
    if (typePartie.startsWith('vendeur')) {
        return mapVendeur(formData, typePartie);
    }
    if (typePartie === 'acquereur' || typePartie === 'acheteur') {
        return mapAcquereur(formData);
    }
    return formData;
}

// ============================================
// MAPPING VENDEUR
// ============================================

function mapVendeur(data, typePartie) {
    const result = {};

    // Vendeurs (promettants pour promesse)
    const vendeurs = mapVendeurs(data);
    result.vendeurs = vendeurs;
    result.promettants = vendeurs; // Alias pour promesse

    // Copropriété
    if (data.copropriete) {
        result.copropriete = mapCopropriete(data.copropriete);
    }

    // Travaux
    if (data.travaux) {
        result.travaux = mapTravaux(data.travaux);
    }

    // Fiscal / Déclarations
    if (data.fiscal) {
        result.declarations_promettant = mapFiscal(data.fiscal);
    }

    // Prêts existants du vendeur
    if (data.prets) {
        result.garanties_hypothecaires = mapPretsVendeur(data.prets);
    }

    return result;
}

function mapVendeurs(data) {
    const vendeurs = [];

    // Vendeur 1 - soit dans data.vendeurs[0], soit à plat
    if (data.vendeurs && data.vendeurs.length > 0) {
        data.vendeurs.forEach(v => {
            vendeurs.push(mapPersonnePhysique(v, data.coordonnees));
        });
    } else {
        // Format à plat (vendeur1_nom, vendeur1_prenoms...)
        const v1 = mapPersonnePhysiqueFlat(data, 'vendeur1', data.coordonnees || data);
        if (v1.nom) vendeurs.push(v1);

        // Vendeur 2
        const v2 = mapPersonnePhysiqueFlat(data, 'vendeur2', data.coordonnees || data);
        if (v2.nom) vendeurs.push(v2);
    }

    return vendeurs;
}

/**
 * Mappe une personne depuis un objet structuré (questionnaire-common.js)
 */
function mapPersonnePhysique(personne, coordonnees) {
    const result = {
        civilite: personne.civilite || undefined,
        nom: personne.nom || '',
        prenoms: personne.prenoms || '',
        date_naissance: personne.date_naissance || '',
        lieu_naissance: personne.lieu_naissance || '',
        nationalite: personne.nationalite || 'Française',
        profession: personne.profession || '',
        resident_fiscal: personne.residence_fiscale !== 'non_resident'
    };

    // Adresse (dans coordonnees ou dans personne)
    const addr = coordonnees || personne;
    if (addr.adresse || addr.code_postal) {
        result.adresse = addr.adresse || '';
        result.code_postal = addr.code_postal || '';
        result.ville = addr.ville || '';
    }

    // Situation matrimoniale
    const regime = personne.situation_matrimoniale || personne.situation;
    if (regime) {
        result.situation_matrimoniale = {
            statut: mapStatutMatrimonial(regime),
            regime_matrimonial: personne.regime_matrimonial || undefined,
            contrat_mariage: personne.date_mariage ? {
                date: personne.date_mariage,
                lieu: personne.lieu_mariage || ''
            } : undefined,
            conjoint: personne.conjoint_nom ? {
                nom: personne.conjoint_nom,
                prenoms: personne.conjoint_prenoms || ''
            } : undefined
        };
    }

    // Coordonnées
    if (addr.tel_portable || addr.email) {
        result.coordonnees = {
            telephone: addr.tel_portable || addr.tel_domicile || addr.telephone || '',
            email: addr.email || ''
        };
    }

    return cleanObject(result);
}

/**
 * Mappe une personne depuis des champs à plat (vendeur1_nom, vendeur1_prenoms...)
 */
function mapPersonnePhysiqueFlat(data, prefix, coordonnees) {
    const get = (field) => data[`${prefix}_${field}`] || data[field] || '';

    const result = {
        civilite: get('civilite') || undefined,
        nom: get('nom'),
        prenoms: get('prenoms'),
        date_naissance: get('date_naissance'),
        lieu_naissance: get('lieu_naissance'),
        nationalite: get('nationalite') || 'Française',
        profession: get('profession'),
        resident_fiscal: get('residence_fiscale') !== 'non_resident'
    };

    // Adresse
    if (coordonnees) {
        result.adresse = coordonnees.adresse || get('adresse') || '';
        result.code_postal = coordonnees.code_postal || get('code_postal') || '';
        result.ville = coordonnees.ville || get('ville') || '';
    }

    // Situation matrimoniale
    const regime = get('situation');
    if (regime) {
        result.situation_matrimoniale = {
            statut: mapStatutMatrimonial(regime),
            regime_matrimonial: get('regime_matrimonial') || undefined,
            contrat_mariage: get('date_mariage') ? {
                date: get('date_mariage'),
                lieu: get('lieu_mariage') || ''
            } : undefined
        };
    }

    // Coordonnées
    const tel = coordonnees?.tel_portable || get('telephone') || '';
    const email = coordonnees?.email || get('email') || '';
    if (tel || email) {
        result.coordonnees = { telephone: tel, email };
    }

    return cleanObject(result);
}

// ============================================
// MAPPING ACQUÉREUR
// ============================================

function mapAcquereur(data) {
    const result = {};

    // Acquéreurs (bénéficiaires pour promesse)
    const acquereurs = [];

    if (data.acheteurs && data.acheteurs.length > 0) {
        data.acheteurs.forEach(a => {
            acquereurs.push(mapPersonnePhysique(a, data.coordonnees));
        });
    } else if (data.acquereur) {
        // Format fill.html (objet unique)
        const acq = data.acquereur;
        const pp = acq.personne_physique || acq;
        const mapped = {
            civilite: pp.civilite || undefined,
            nom: pp.nom || '',
            prenoms: Array.isArray(pp.prenoms) ? pp.prenoms.join(' ') : (pp.prenoms || ''),
            date_naissance: pp.date_naissance || '',
            lieu_naissance: pp.lieu_naissance || '',
            nationalite: pp.nationalite || 'Française',
            profession: pp.profession || ''
        };

        // Adresse
        if (acq.adresse) {
            mapped.adresse = acq.adresse.adresse || '';
            mapped.code_postal = acq.adresse.code_postal || '';
            mapped.ville = acq.adresse.ville || '';
        }

        // Situation matrimoniale
        if (acq.situation_matrimoniale) {
            mapped.situation_matrimoniale = {
                statut: mapStatutMatrimonial(acq.situation_matrimoniale.regime || acq.situation_matrimoniale.statut),
                conjoint: acq.situation_matrimoniale.conjoint || undefined
            };
        }

        // Coordonnées
        if (acq.contact) {
            mapped.coordonnees = {
                telephone: acq.contact.telephone || '',
                email: acq.contact.email || ''
            };
        }

        acquereurs.push(cleanObject(mapped));
    }

    result.acquereurs = acquereurs;
    result.beneficiaires = acquereurs; // Alias pour promesse

    // Financement
    if (data.financement || data.pret_montant || data.apport_personnel) {
        result.financement = mapFinancement(data);

        // Conditions suspensives de prêt
        if (data.pret_montant || data.financement?.prets?.length > 0) {
            result.conditions_suspensives = {
                pret: {
                    applicable: true,
                    montant_maximum: parseFloat(data.pret_montant) || data.financement?.prets?.[0]?.montant || 0,
                    taux_maximum: parseFloat(data.pret_taux_max) || undefined,
                    duree_minimum_mois: parseInt(data.pret_duree) || undefined
                }
            };
        }
    }

    return result;
}

// ============================================
// MAPPING COPROPRIÉTÉ
// ============================================

function mapCopropriete(copro) {
    const result = {};

    if (copro.nom_syndic) {
        result.syndic = { nom: copro.nom_syndic };
    }

    if (copro.fonds_travaux) {
        result.fonds_travaux = { existe: copro.fonds_travaux === 'oui' };
    }

    if (copro.difficultes_copro === 'oui') {
        result._difficultes = copro.details_difficultes || '';
    }

    return cleanObject(result);
}

// ============================================
// MAPPING TRAVAUX
// ============================================

function mapTravaux(travaux) {
    const result = { travaux_realises: [] };

    if (travaux.travaux_parties_communes === 'oui' && travaux.details_travaux) {
        result.travaux_realises.push({
            description: travaux.details_travaux,
            declaration_prealable_requise: travaux.autorisation_travaux === 'oui'
        });
    }

    return result;
}

// ============================================
// MAPPING FISCAL / DÉCLARATIONS
// ============================================

function mapFiscal(fiscal) {
    return cleanObject({
        absence_location: fiscal.bien_libre === 'oui',
        garantie_eviction: true,
        garantie_jouissance: true,
        impots_taxes: {
            regime_fiscal_location: fiscal.avantage_fiscal === 'oui'
                ? (fiscal.type_avantage_fiscal || 'autre')
                : 'aucun'
        }
    });
}

// ============================================
// MAPPING PRÊTS VENDEUR
// ============================================

function mapPretsVendeur(prets) {
    return cleanObject({
        inscriptions: prets.prets_hypothecaires === 'oui' ? [{
            type: 'hypotheque_conventionnelle',
            beneficiaire: prets.details_prets || ''
        }] : []
    });
}

// ============================================
// MAPPING FINANCEMENT
// ============================================

function mapFinancement(data) {
    const result = {};

    // Depuis fill.html / achat-bien.html
    const apport = parseFloat(data.apport_personnel) || 0;
    const pretMontant = parseFloat(data.pret_montant) || 0;

    if (apport > 0) result.apport_personnel = apport;
    if (pretMontant > 0) result.pret_sollicite = pretMontant;

    // Depuis structure financement
    if (data.financement) {
        if (data.financement.apport_personnel) result.apport_personnel = data.financement.apport_personnel;
        if (data.financement.prets) result.pret_sollicite = data.financement.prets.reduce((sum, p) => sum + (p.montant || 0), 0);
    }

    return cleanObject(result);
}

// ============================================
// FUSION VENDEUR + ACQUÉREUR (DOSSIER)
// ============================================

/**
 * Combine les données vendeur + acquéreur pour un dossier complet.
 * @param {Object[]} submissionsDecryptees - [{data, type_partie}, ...]
 * @param {Object} metadonnees - {prix_montant, adresse_bien, ...}
 * @returns {Object} Données complètes pour le pipeline
 */
function combinerDonneesDossier(submissionsDecryptees, metadonnees = {}) {
    let merged = {};

    submissionsDecryptees.forEach(sub => {
        const mapped = mapFormToPipeline(sub.data, sub.type_partie);
        merged = { ...merged, ...mapped };
    });

    // Ajouter les métadonnées du dossier (bien, prix)
    if (metadonnees.prix_montant) {
        merged.prix = { montant: parseFloat(metadonnees.prix_montant) };
    }

    if (metadonnees.adresse_bien) {
        merged.bien = {
            adresse: {
                numero: '',
                voie: metadonnees.adresse_bien,
                code_postal: metadonnees.code_postal_bien || '',
                ville: metadonnees.ville_bien || ''
            }
        };
    }

    return merged;
}

// ============================================
// VALIDATION PRÉ-GÉNÉRATION
// ============================================

/**
 * Valide les données avant envoi à l'API de génération.
 * @param {Object} donneesPipeline - Données mappées
 * @returns {{valide: boolean, erreurs: string[], avertissements: string[], completude: number}}
 */
function validerAvantGeneration(donneesPipeline) {
    const erreurs = [];
    const avertissements = [];

    // Vendeurs / Promettants
    const vendeurs = donneesPipeline.vendeurs || donneesPipeline.promettants || [];
    if (vendeurs.length === 0) {
        erreurs.push('Aucun vendeur renseigné');
    } else {
        vendeurs.forEach((v, i) => {
            if (!v.nom) erreurs.push(`Vendeur ${i + 1} : nom manquant`);
            if (!v.prenoms) erreurs.push(`Vendeur ${i + 1} : prénoms manquants`);
            if (!v.date_naissance) avertissements.push(`Vendeur ${i + 1} : date de naissance manquante`);
            if (!v.adresse) avertissements.push(`Vendeur ${i + 1} : adresse manquante`);
        });
    }

    // Acquéreurs / Bénéficiaires
    const acquereurs = donneesPipeline.acquereurs || donneesPipeline.beneficiaires || [];
    if (acquereurs.length === 0) {
        erreurs.push('Aucun acquéreur renseigné');
    } else {
        acquereurs.forEach((a, i) => {
            if (!a.nom) erreurs.push(`Acquéreur ${i + 1} : nom manquant`);
            if (!a.prenoms) erreurs.push(`Acquéreur ${i + 1} : prénoms manquants`);
            if (!a.date_naissance) avertissements.push(`Acquéreur ${i + 1} : date de naissance manquante`);
        });
    }

    // Bien
    if (!donneesPipeline.bien?.adresse) {
        avertissements.push('Adresse du bien non renseignée');
    }

    // Prix
    if (!donneesPipeline.prix?.montant || donneesPipeline.prix.montant <= 0) {
        avertissements.push('Prix de vente non renseigné');
    }

    // Complétude
    const completude = calculerCompletude(donneesPipeline);

    return { valide: erreurs.length === 0, erreurs, avertissements, completude };
}

function calculerCompletude(donnees) {
    const checks = [
        (donnees.vendeurs || donnees.promettants || []).length > 0,
        (donnees.vendeurs || donnees.promettants || [])[0]?.nom,
        (donnees.vendeurs || donnees.promettants || [])[0]?.prenoms,
        (donnees.vendeurs || donnees.promettants || [])[0]?.date_naissance,
        (donnees.vendeurs || donnees.promettants || [])[0]?.adresse,
        (donnees.acquereurs || donnees.beneficiaires || []).length > 0,
        (donnees.acquereurs || donnees.beneficiaires || [])[0]?.nom,
        (donnees.acquereurs || donnees.beneficiaires || [])[0]?.prenoms,
        donnees.bien?.adresse,
        donnees.prix?.montant > 0,
        donnees.financement?.apport_personnel || donnees.financement?.pret_sollicite
    ];

    const remplis = checks.filter(Boolean).length;
    return Math.round((remplis / checks.length) * 100);
}

// ============================================
// UTILITAIRES
// ============================================

function mapStatutMatrimonial(regime) {
    const mapping = {
        'celibataire': 'celibataire',
        'marie': 'marie',
        'mariee': 'marie',
        'pacse': 'pacse',
        'pacsee': 'pacse',
        'divorce': 'divorce',
        'divorcee': 'divorce',
        'veuf': 'veuf',
        'veuve': 'veuf',
        'separe': 'separe',
        'separee': 'separe',
        'concubinage': 'celibataire'
    };
    return mapping[(regime || '').toLowerCase()] || regime || 'celibataire';
}

/**
 * Supprime les clés undefined/null/'' d'un objet
 */
function cleanObject(obj) {
    if (!obj || typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) return obj.map(cleanObject).filter(Boolean);

    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
        if (value === undefined || value === null || value === '') continue;
        if (typeof value === 'object' && !Array.isArray(value)) {
            const sub = cleanObject(value);
            if (Object.keys(sub).length > 0) cleaned[key] = sub;
        } else if (Array.isArray(value)) {
            const arr = cleanObject(value);
            if (arr.length > 0) cleaned[key] = arr;
        } else {
            cleaned[key] = value;
        }
    }
    return cleaned;
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { mapFormToPipeline, combinerDonneesDossier, validerAvantGeneration, calculerCompletude };
}
