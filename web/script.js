// Gestion de l'affichage du formulaire conjoint
document.getElementById('regime_matrimonial').addEventListener('change', function(e) {
    const conjointSection = document.getElementById('conjoint_section');
    const value = e.target.value;

    if (value === 'marie' || value === 'pacs') {
        conjointSection.classList.remove('hidden');
        // Rendre les champs obligatoires
        document.getElementById('conjoint_nom').required = true;
        document.getElementById('conjoint_prenoms').required = true;
        document.getElementById('date_mariage').required = true;
        document.getElementById('lieu_mariage').required = true;
        document.getElementById('type_regime').required = true;
    } else {
        conjointSection.classList.add('hidden');
        // Rendre les champs optionnels
        document.getElementById('conjoint_nom').required = false;
        document.getElementById('conjoint_prenoms').required = false;
        document.getElementById('date_mariage').required = false;
        document.getElementById('lieu_mariage').required = false;
        document.getElementById('type_regime').required = false;
    }
});

// Soumission du formulaire
document.getElementById('vendeurForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {
        vendeur: {
            personne_physique: {
                civilite: formData.get('civilite'),
                nom: formData.get('nom'),
                nom_usage: formData.get('nom_usage') || null,
                prenoms: formData.get('prenoms').split(',').map(p => p.trim()),
                date_naissance: formData.get('date_naissance'),
                lieu_naissance: formData.get('lieu_naissance'),
                nationalite: formData.get('nationalite'),
                profession: formData.get('profession') || null
            },
            adresse: {
                adresse: formData.get('adresse'),
                code_postal: formData.get('code_postal'),
                ville: formData.get('ville')
            },
            situation_matrimoniale: {
                regime: formData.get('regime_matrimonial')
            },
            pieces_identite: {
                cni: {
                    numero: formData.get('cni_numero'),
                    date_emission: formData.get('cni_date_emission'),
                    date_expiration: formData.get('cni_date_expiration'),
                    autorite_emission: formData.get('cni_autorite')
                }
            },
            coordonnees_bancaires: {
                iban: formData.get('iban'),
                bic: formData.get('bic'),
                nom_banque: formData.get('banque')
            },
            contact: {
                telephone: formData.get('telephone'),
                email: formData.get('email')
            }
        }
    };

    // Ajouter les informations du conjoint si applicable
    const regime = formData.get('regime_matrimonial');
    if (regime === 'marie' || regime === 'pacs') {
        const conjointKey = regime === 'marie' ? 'conjoint' : 'partenaire';
        data.vendeur.situation_matrimoniale[conjointKey] = {
            nom: formData.get('conjoint_nom'),
            prenoms: formData.get('conjoint_prenoms').split(',').map(p => p.trim()),
            intervient_acte: formData.get('conjoint_intervient') === 'on'
        };
        data.vendeur.situation_matrimoniale.date_union = formData.get('date_mariage');
        data.vendeur.situation_matrimoniale.lieu_union = formData.get('lieu_mariage');
        data.vendeur.situation_matrimoniale.type_regime = formData.get('type_regime');
    }

    // Afficher le résultat
    document.getElementById('resultJson').textContent = JSON.stringify(data, null, 2);
    document.getElementById('result').classList.remove('hidden');

    // Scroll vers le résultat
    document.getElementById('result').scrollIntoView({ behavior: 'smooth' });

    // Afficher un toast
    showToast('Données collectées avec succès!');
});

// Réinitialiser le formulaire
function resetForm() {
    document.getElementById('vendeurForm').reset();
    document.getElementById('conjoint_section').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
}

// Remplir avec un exemple
function fillExample() {
    document.getElementById('civilite').value = 'M';
    document.getElementById('nom').value = 'DUPONT';
    document.getElementById('prenoms').value = 'Jean, Pierre, Marie';
    document.getElementById('date_naissance').value = '1975-06-15';
    document.getElementById('lieu_naissance').value = 'Paris (75)';
    document.getElementById('nationalite').value = 'Française';
    document.getElementById('profession').value = 'Ingénieur';

    document.getElementById('adresse').value = '12 rue de la République';
    document.getElementById('code_postal').value = '75001';
    document.getElementById('ville').value = 'Paris';

    document.getElementById('regime_matrimonial').value = 'marie';
    // Déclencher l'événement change pour afficher la section conjoint
    document.getElementById('regime_matrimonial').dispatchEvent(new Event('change'));

    document.getElementById('conjoint_nom').value = 'MARTIN';
    document.getElementById('conjoint_prenoms').value = 'Sophie, Marie';
    document.getElementById('date_mariage').value = '2005-08-20';
    document.getElementById('lieu_mariage').value = 'Lyon (69)';
    document.getElementById('type_regime').value = 'communaute_legale';
    document.getElementById('conjoint_intervient').checked = true;

    document.getElementById('cni_numero').value = '123456789012';
    document.getElementById('cni_date_emission').value = '2020-01-15';
    document.getElementById('cni_date_expiration').value = '2030-01-15';
    document.getElementById('cni_autorite').value = 'Préfecture de Paris';

    document.getElementById('iban').value = 'FR76 1234 5678 9012 3456 7890 123';
    document.getElementById('bic').value = 'BNPAFRPPXXX';
    document.getElementById('banque').value = 'BNP Paribas';

    document.getElementById('telephone').value = '06 12 34 56 78';
    document.getElementById('email').value = 'jean.dupont@email.com';

    showToast('Formulaire rempli avec des données d\'exemple');
}

// Télécharger le JSON
function downloadJson() {
    const jsonText = document.getElementById('resultJson').textContent;
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vendeur_' + new Date().toISOString().split('T')[0] + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Fichier JSON téléchargé');
}

// Copier le JSON
function copyJson() {
    const jsonText = document.getElementById('resultJson').textContent;
    navigator.clipboard.writeText(jsonText).then(() => {
        showToast('JSON copié dans le presse-papier');
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        showToast('Erreur lors de la copie', 'error');
    });
}

// Afficher un toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;

    if (type === 'error') {
        toast.style.background = '#f44336';
    }

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Formatage automatique de l'IBAN
document.getElementById('iban').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\s/g, '').toUpperCase();
    let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = formatted;
});

// Formatage automatique du téléphone
document.getElementById('telephone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\s/g, '');
    let formatted = value.match(/.{1,2}/g)?.join(' ') || value;
    e.target.value = formatted;
});
