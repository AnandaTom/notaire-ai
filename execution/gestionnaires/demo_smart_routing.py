# -*- coding: utf-8 -*-
"""
Démonstration du Smart Routing de Modèles LLM (v2.1.0)

Ce script illustre l'utilisation du smart routing dans différents scénarios
pour optimiser les coûts API de 60%.

Usage:
    python execution/gestionnaires/demo_smart_routing.py
"""

import sys
from pathlib import Path

# Ajuster le chemin si nécessaire
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from execution.gestionnaires.orchestrateur import OrchestratorNotaire, TypeActe


def demo_validation():
    """Démo 1: Validation (→ Haiku, 80% économie)."""
    print("\n" + "=" * 60)
    print("DÉMO 1: VALIDATION (→ HAIKU)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    donnees = {
        "acte": {"type": "vente"},
        "vendeurs": [{"nom": "Dupont"}],
        "acquereurs": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 350000}
    }

    # Appeler la validation (utilise automatiquement Haiku)
    resultat = orch._valider_donnees(donnees, TypeActe.VENTE)

    print(f"\n✅ Résultat: {resultat}")
    print(f"📊 Stats modèles: {orch.stats_modeles}")


def demo_detection_haute_confiance():
    """Démo 2: Détection haute confiance (→ Sonnet, 60% économie)."""
    print("\n" + "=" * 60)
    print("DÉMO 2: DÉTECTION HAUTE CONFIANCE (→ SONNET)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    # Simuler une détection avec haute confiance
    modele = orch._choisir_modele(type_operation="detection", confiance=0.92)

    print(f"\n✅ Modèle sélectionné: {modele}")
    print(f"📊 Stats modèles: {orch.stats_modeles}")


def demo_generation_standard():
    """Démo 3: Génération standard (→ Sonnet, 60% économie)."""
    print("\n" + "=" * 60)
    print("DÉMO 3: GÉNÉRATION STANDARD (→ SONNET)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    donnees_std = {
        "acte": {"type": "vente"},
        "vendeurs": [{"nom": "Dupont"}],
        "acquereurs": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 350000}
    }

    modele = orch._choisir_modele(type_operation="generation", donnees=donnees_std)

    print(f"\n✅ Modèle sélectionné: {modele}")
    print(f"📊 Stats modèles: {orch.stats_modeles}")


def demo_generation_complexe():
    """Démo 4: Génération complexe (→ Opus, qualité max)."""
    print("\n" + "=" * 60)
    print("DÉMO 4: GÉNÉRATION COMPLEXE (→ OPUS)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    # Cas 1: Type complexe (viager)
    print("\n--- Cas 1: Type viager ---")
    donnees_viager = {
        "acte": {"type": "viager"},
        "promettants": [{"nom": "Dupont"}],
        "beneficiaires": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 250000}
    }
    modele1 = orch._choisir_modele(type_operation="generation", donnees=donnees_viager)
    print(f"✅ Modèle: {modele1}")

    # Cas 2: Multi-parties
    print("\n--- Cas 2: Multi-parties (>2 vendeurs) ---")
    donnees_multi = {
        "acte": {"type": "vente"},
        "vendeurs": [
            {"nom": "Dupont"},
            {"nom": "Martin"},
            {"nom": "Bernard"}
        ],
        "acquereurs": [{"nom": "Thomas"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 300000}
    }
    modele2 = orch._choisir_modele(type_operation="generation", donnees=donnees_multi)
    print(f"✅ Modèle: {modele2}")

    # Cas 3: Prix élevé
    print("\n--- Cas 3: Prix >1M€ ---")
    donnees_prix_eleve = {
        "acte": {"type": "vente"},
        "vendeurs": [{"nom": "Dupont"}],
        "acquereurs": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Château"},
        "prix": {"montant": 1_500_000}
    }
    modele3 = orch._choisir_modele(type_operation="generation", donnees=donnees_prix_eleve)
    print(f"✅ Modèle: {modele3}")

    print(f"\n📊 Stats modèles: {orch.stats_modeles}")


def demo_suggestion_clauses():
    """Démo 5: Suggestion de clauses (→ Opus, créativité)."""
    print("\n" + "=" * 60)
    print("DÉMO 5: SUGGESTION CLAUSES (→ OPUS)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    modele = orch._choisir_modele(type_operation="suggestion_clauses")

    print(f"\n✅ Modèle sélectionné: {modele}")
    print(f"📊 Stats modèles: {orch.stats_modeles}")


def demo_workflow_complet():
    """Démo 6: Workflow complet avec statistiques."""
    print("\n" + "=" * 60)
    print("DÉMO 6: WORKFLOW COMPLET")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=True)

    # Simuler un workflow typique:
    # 1. Validation initiale (Haiku)
    donnees = {
        "acte": {"type": "vente"},
        "vendeurs": [{"nom": "Dupont"}],
        "acquereurs": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 350000}
    }
    orch._valider_donnees(donnees, TypeActe.VENTE)

    # 2. Détection type acte (Sonnet, haute confiance)
    orch._choisir_modele(type_operation="detection", confiance=0.88)

    # 3. Génération acte standard (Sonnet)
    orch._choisir_modele(type_operation="generation", donnees=donnees)

    # 4. Suggestion clauses optionnelles (Opus)
    orch._choisir_modele(type_operation="suggestion_clauses")

    # Afficher les statistiques finales
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES FINALES")
    print("=" * 60)
    orch.afficher_stats_modeles()


def demo_comparaison_baseline():
    """Démo 7: Comparaison économie vs baseline Opus."""
    print("\n" + "=" * 60)
    print("DÉMO 7: COMPARAISON ÉCONOMIE (100 OPÉRATIONS)")
    print("=" * 60)

    orch = OrchestratorNotaire(verbose=False)

    # Simuler 100 opérations typiques:
    # - 40 validations
    # - 30 détections (haute confiance)
    # - 25 générations standard
    # - 5 générations complexes

    print("\n📊 Simulation 100 opérations...")

    for _ in range(40):
        orch._choisir_modele(type_operation="validation")

    for _ in range(30):
        orch._choisir_modele(type_operation="detection", confiance=0.85)

    donnees_std = {
        "acte": {"type": "vente"},
        "vendeurs": [{"nom": "Dupont"}],
        "acquereurs": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 350000}
    }
    for _ in range(25):
        orch._choisir_modele(type_operation="generation", donnees=donnees_std)

    donnees_viager = {
        "acte": {"type": "viager"},
        "promettants": [{"nom": "Dupont"}],
        "beneficiaires": [{"nom": "Martin"}],
        "bien": {"adresse": "12 rue Test"},
        "prix": {"montant": 250000}
    }
    for _ in range(5):
        orch._choisir_modele(type_operation="generation", donnees=donnees_viager)

    # Afficher les stats
    orch.afficher_stats_modeles()


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 60)
    print("🚀 DÉMONSTRATION SMART ROUTING LLM (v2.1.0)")
    print("=" * 60)
    print("\nObjectif: Réduire les coûts API de 60% en sélectionnant")
    print("intelligemment le modèle Claude selon le type d'opération.")

    demos = [
        ("1. Validation", demo_validation),
        ("2. Détection haute confiance", demo_detection_haute_confiance),
        ("3. Génération standard", demo_generation_standard),
        ("4. Génération complexe", demo_generation_complexe),
        ("5. Suggestion de clauses", demo_suggestion_clauses),
        ("6. Workflow complet", demo_workflow_complet),
        ("7. Comparaison économie", demo_comparaison_baseline),
    ]

    print("\n📋 Démonstrations disponibles:")
    for titre, _ in demos:
        print(f"   {titre}")

    print("\n" + "=" * 60)

    # Exécuter toutes les démos
    for titre, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Erreur dans {titre}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()
