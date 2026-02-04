/**
 * Script spécifique pour le questionnaire état civil
 * Gère les champs conditionnels et la collecte de fichiers
 */

document.addEventListener('DOMContentLoaded', () => {
    // Situation matrimoniale -> afficher conjoint
    const situationSelect = document.getElementById('situation_matrimoniale');
    if (situationSelect) {
        situationSelect.addEventListener('change', (e) => {
            const showConjoint = ['marie', 'pacse'].includes(e.target.value);
            document.getElementById('conjoint_details')?.classList.toggle('visible', showConjoint);
        });
    }

    // File upload handlers
    setupFileUpload('file_recto', 'uploadRecto', 'rectoFileName');
    setupFileUpload('file_verso', 'uploadVerso', 'versoFileName');
});

function setupFileUpload(inputId, zoneId, nameId) {
    const input = document.getElementById(inputId);
    const zone = document.getElementById(zoneId);
    const nameDisplay = document.getElementById(nameId);

    if (!input || !zone) return;

    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate size (10 Mo max)
            if (file.size > 10 * 1024 * 1024) {
                alert('Le fichier est trop volumineux. Taille maximale : 10 Mo.');
                input.value = '';
                return;
            }

            // Validate type
            const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
            if (!allowedTypes.includes(file.type)) {
                alert('Format de fichier non accepté. Utilisez JPG, PNG ou PDF.');
                input.value = '';
                return;
            }

            zone.classList.add('has-file');
            nameDisplay.textContent = file.name;
        } else {
            zone.classList.remove('has-file');
            nameDisplay.textContent = '';
        }
    });
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// Override collectFormData for état civil
function collectFormDataEtatCivil() {
    const formEl = document.getElementById('questionnaireForm');
    const formDataObj = new FormData(formEl);

    const data = {
        type_questionnaire: CONFIG.type,
        date_soumission: new Date().toISOString(),
        personne: {
            civilite: formDataObj.get('civilite'),
            nom: formDataObj.get('nom'),
            nom_usage: formDataObj.get('nom_usage'),
            prenoms: formDataObj.get('prenoms'),
            date_naissance: formDataObj.get('date_naissance'),
            lieu_naissance: formDataObj.get('lieu_naissance'),
            departement_naissance: formDataObj.get('departement_naissance'),
            nationalite: formDataObj.get('nationalite'),
            profession: formDataObj.get('profession'),
            situation_matrimoniale: formDataObj.get('situation_matrimoniale')
        },
        coordonnees: {
            adresse: formDataObj.get('adresse'),
            complement_adresse: formDataObj.get('complement_adresse'),
            code_postal: formDataObj.get('code_postal'),
            ville: formDataObj.get('ville'),
            pays: formDataObj.get('pays'),
            tel_portable: formDataObj.get('tel_portable'),
            tel_fixe: formDataObj.get('tel_fixe'),
            email: formDataObj.get('email')
        },
        piece_identite: {
            type_piece: formDataObj.get('type_piece'),
            numero_piece: formDataObj.get('numero_piece'),
            date_expiration: formDataObj.get('date_expiration'),
            autorite_delivrance: formDataObj.get('autorite_delivrance')
        },
        observations: formDataObj.get('observations'),
        metadata: {
            user_agent: navigator.userAgent,
            rgpd_consent: formDataObj.get('rgpd_consent') === 'on',
            rgpd_consent_date: new Date().toISOString()
        }
    };

    // Conjoint info if married/PACS
    if (['marie', 'pacse'].includes(data.personne.situation_matrimoniale)) {
        data.personne.conjoint = {
            civilite: formDataObj.get('conjoint_civilite'),
            nom: formDataObj.get('conjoint_nom'),
            prenoms: formDataObj.get('conjoint_prenoms'),
            date_naissance: formDataObj.get('conjoint_date_naissance'),
            lieu_naissance: formDataObj.get('conjoint_lieu_naissance'),
            regime_matrimonial: formDataObj.get('regime_matrimonial'),
            date_mariage: formDataObj.get('date_mariage'),
            lieu_mariage: formDataObj.get('lieu_mariage')
        };
    }

    return data;
}

// Override collectFormData to include file data
const originalCollectFormData = typeof collectFormData === 'function' ? collectFormData : null;

async function collectFormDataWithFiles() {
    const data = collectFormDataEtatCivil();

    // Add files as base64
    const rectoInput = document.getElementById('file_recto');
    const versoInput = document.getElementById('file_verso');

    if (rectoInput && rectoInput.files[0]) {
        try {
            data.piece_identite.fichier_recto = {
                name: rectoInput.files[0].name,
                type: rectoInput.files[0].type,
                size: rectoInput.files[0].size,
                data: await fileToBase64(rectoInput.files[0])
            };
        } catch (e) {
            console.warn('Could not read recto file:', e);
        }
    }

    if (versoInput && versoInput.files[0]) {
        try {
            data.piece_identite.fichier_verso = {
                name: versoInput.files[0].name,
                type: versoInput.files[0].type,
                size: versoInput.files[0].size,
                data: await fileToBase64(versoInput.files[0])
            };
        } catch (e) {
            console.warn('Could not read verso file:', e);
        }
    }

    return data;
}

// Replace the global collectFormData
if (typeof window !== 'undefined') {
    window.collectFormData = collectFormDataWithFiles;
}
