/**
 * Hook React pour la détection automatique du viager
 * Gère la détection, les questions conditionnelles et la validation
 */

import { useState, useEffect, useCallback } from 'react';
import { detecterType, getQuestions, validerPromesse, DetectionResult, Section } from '@/lib/api/promesse';

interface UseViagerDetectionOptions {
  autoDetect?: boolean; // Détection automatique après 3 champs remplis
  validateOnChange?: boolean; // Validation temps réel
}

export function useViagerDetection(
  donnees: Record<string, any>,
  options: UseViagerDetectionOptions = {}
) {
  const { autoDetect = true, validateOnChange = true } = options;

  const [detection, setDetection] = useState<DetectionResult | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionError, setDetectionError] = useState<string | null>(null);

  const [questionsViager, setQuestionsViager] = useState<Section[]>([]);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);

  const [validation, setValidation] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);

  /**
   * Déclenche la détection manuelle ou automatique
   */
  const detectType = useCallback(async () => {
    // Vérifier qu'on a au moins 3 champs remplis
    const champsRemplis = Object.keys(donnees).filter((key) => {
      const value = donnees[key];
      return value !== null && value !== undefined && value !== '';
    });

    if (champsRemplis.length < 3) {
      return; // Pas assez de données
    }

    setIsDetecting(true);
    setDetectionError(null);

    try {
      const result = await detecterType(donnees);
      setDetection(result);

      // Si viager détecté, charger les questions spécifiques
      if (result.sous_type === 'viager') {
        loadViagerQuestions(result.categorie_bien);
      }
    } catch (error: any) {
      console.error('Erreur détection:', error);
      setDetectionError(error.message);
    } finally {
      setIsDetecting(false);
    }
  }, [donnees]);

  /**
   * Charge les questions viager (section 15_viager)
   */
  const loadViagerQuestions = async (categorie: string) => {
    setIsLoadingQuestions(true);
    try {
      const response = await getQuestions(categorie, 'viager', '15_viager');
      setQuestionsViager(response.sections);
    } catch (error) {
      console.error('Erreur chargement questions viager:', error);
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  /**
   * Valide les données avec règles métier viager
   */
  const validateData = useCallback(async () => {
    if (!detection?.sous_type) return;

    setIsValidating(true);
    try {
      const result = await validerPromesse(donnees);
      setValidation(result);
    } catch (error) {
      console.error('Erreur validation:', error);
    } finally {
      setIsValidating(false);
    }
  }, [donnees, detection]);

  /**
   * Auto-détection au changement des données
   */
  useEffect(() => {
    if (autoDetect && Object.keys(donnees).length >= 3) {
      const timer = setTimeout(() => {
        detectType();
      }, 1000); // Debounce 1s

      return () => clearTimeout(timer);
    }
  }, [donnees, autoDetect, detectType]);

  /**
   * Auto-validation au changement
   */
  useEffect(() => {
    if (validateOnChange && detection?.sous_type === 'viager') {
      const timer = setTimeout(() => {
        validateData();
      }, 500); // Debounce 500ms

      return () => clearTimeout(timer);
    }
  }, [donnees, validateOnChange, detection, validateData]);

  /**
   * Vérifie si les champs obligatoires viager sont remplis
   */
  const checkViagerRequired = useCallback(() => {
    if (detection?.sous_type !== 'viager') return { valid: true, missing: [] };

    const missing: string[] = [];

    // Bouquet obligatoire
    if (!donnees.prix?.bouquet?.montant) {
      missing.push('Bouquet (capital initial)');
    }

    // Rente viagère obligatoire
    if (!donnees.prix?.rente_viagere?.montant) {
      missing.push('Rente viagère mensuelle');
    }

    // Âge du crédirentier recommandé
    if (!donnees.promettants?.[0]?.age) {
      missing.push('Âge du vendeur (recommandé)');
    }

    return {
      valid: missing.length === 0,
      missing,
    };
  }, [donnees, detection]);

  /**
   * Génère les warnings viager
   */
  const getViagerWarnings = useCallback(() => {
    if (detection?.sous_type !== 'viager') return [];

    const warnings: string[] = [];

    // Certificat médical recommandé
    if (!donnees.promettants?.[0]?.sante?.certificat_medical?.fourni) {
      warnings.push('Certificat médical recommandé (art. 1975 C. civ.)');
    }

    // Indexation recommandée
    if (
      donnees.prix?.rente_viagere &&
      !donnees.prix?.rente_viagere?.indexation?.indice
    ) {
      warnings.push('Indexation de la rente recommandée (IRL, IPC)');
    }

    // DUH recommandé pour viager occupé
    if (
      donnees.prix?.type_vente === 'Viager occupé' &&
      !donnees.bien?.droit_usage_habitation?.reserve
    ) {
      warnings.push('DUH (Droit d\'Usage et d\'Habitation) recommandé');
    }

    return warnings;
  }, [donnees, detection]);

  return {
    // État détection
    detection,
    isDetecting,
    detectionError,
    detectType, // Fonction manuelle

    // Questions viager
    questionsViager,
    isLoadingQuestions,

    // Validation
    validation,
    isValidating,
    validateData,

    // Helpers
    checkViagerRequired,
    getViagerWarnings,

    // Computed
    isViager: detection?.sous_type === 'viager',
    isCreation: detection?.sous_type === 'creation',
    sousType: detection?.sous_type,
    confiance: detection?.confiance || 0,
  };
}
