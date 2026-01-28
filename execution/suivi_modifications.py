# -*- coding: utf-8 -*-
"""
suivi_modifications.py
======================

Module de suivi des modifications entre promesse et acte de vente.

Fonctionnalités:
- Comparaison détaillée entre documents
- Génération d'avenants si nécessaire
- Historique des modifications
- Validation de la cohérence

Usage:
    from execution.suivi_modifications import SuiviModifications

    suivi = SuiviModifications()
    diff = suivi.comparer(promesse_data, vente_data)
    if diff.avenant_necessaire:
        avenant = suivi.generer_avenant(diff)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import copy

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class TypeModification(Enum):
    """Types de modifications possibles."""
    PRIX = "prix"
    PARTIES = "parties"
    BIEN = "bien"
    FINANCEMENT = "financement"
    CONDITIONS = "conditions"
    DELAIS = "delais"
    AUTRE = "autre"


class NiveauGravite(Enum):
    """Niveau de gravité d'une modification."""
    MINEURE = "mineure"          # Pas d'avenant requis
    SIGNIFICATIVE = "significative"  # Avenant recommandé
    MAJEURE = "majeure"          # Avenant obligatoire


@dataclass
class Modification:
    """Représente une modification détectée."""
    type_modification: TypeModification
    chemin: str
    valeur_originale: Any
    valeur_nouvelle: Any
    gravite: NiveauGravite
    description: str
    date_detection: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RapportComparaison:
    """Rapport de comparaison entre deux documents."""
    modifications: List[Modification] = field(default_factory=list)
    avenant_necessaire: bool = False
    avenant_recommande: bool = False
    resume: str = ""
    date_comparaison: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire."""
        return {
            "modifications": [
                {
                    "type": m.type_modification.value,
                    "chemin": m.chemin,
                    "valeur_originale": m.valeur_originale,
                    "valeur_nouvelle": m.valeur_nouvelle,
                    "gravite": m.gravite.value,
                    "description": m.description
                }
                for m in self.modifications
            ],
            "avenant_necessaire": self.avenant_necessaire,
            "avenant_recommande": self.avenant_recommande,
            "resume": self.resume,
            "date_comparaison": self.date_comparaison
        }


class SuiviModifications:
    """
    Classe de suivi des modifications entre promesse et vente.
    """

    # Seuils pour déterminer la gravité
    SEUIL_PRIX_MINEURE = 0.01  # 1% de variation
    SEUIL_PRIX_SIGNIFICATIVE = 0.05  # 5% de variation
    SEUIL_PRIX_MAJEURE = 0.10  # 10% de variation

    def __init__(self):
        """Initialise le suivi."""
        self.historique: List[RapportComparaison] = []

    def comparer(
        self,
        promesse: Dict,
        vente: Dict,
        stricte: bool = False
    ) -> RapportComparaison:
        """
        Compare une promesse et un acte de vente.

        Args:
            promesse: Données de la promesse
            vente: Données de l'acte de vente
            stricte: Mode strict (toute différence = modification)

        Returns:
            RapportComparaison détaillé
        """
        rapport = RapportComparaison()

        # 1. Comparer le prix
        mods_prix = self._comparer_prix(promesse, vente)
        rapport.modifications.extend(mods_prix)

        # 2. Comparer les parties
        mods_parties = self._comparer_parties(promesse, vente)
        rapport.modifications.extend(mods_parties)

        # 3. Comparer le bien
        mods_bien = self._comparer_bien(promesse, vente, stricte)
        rapport.modifications.extend(mods_bien)

        # 4. Comparer le financement
        mods_fin = self._comparer_financement(promesse, vente)
        rapport.modifications.extend(mods_fin)

        # 5. Comparer les conditions
        mods_cond = self._comparer_conditions(promesse, vente)
        rapport.modifications.extend(mods_cond)

        # 6. Comparer les délais
        mods_delais = self._comparer_delais(promesse, vente)
        rapport.modifications.extend(mods_delais)

        # Déterminer si avenant nécessaire/recommandé
        rapport.avenant_necessaire = any(
            m.gravite == NiveauGravite.MAJEURE
            for m in rapport.modifications
        )
        rapport.avenant_recommande = any(
            m.gravite == NiveauGravite.SIGNIFICATIVE
            for m in rapport.modifications
        )

        # Générer le résumé
        rapport.resume = self._generer_resume(rapport)

        # Ajouter à l'historique
        self.historique.append(rapport)

        return rapport

    def _comparer_prix(self, promesse: Dict, vente: Dict) -> List[Modification]:
        """Compare les prix."""
        modifications = []

        prix_promesse = promesse.get("prix", {}).get("montant", 0)
        prix_vente = vente.get("prix", {}).get("montant", 0)

        if prix_promesse and prix_vente and abs(prix_promesse - prix_vente) > 0.01:
            variation = abs(prix_vente - prix_promesse) / prix_promesse

            if variation > self.SEUIL_PRIX_MAJEURE:
                gravite = NiveauGravite.MAJEURE
            elif variation > self.SEUIL_PRIX_SIGNIFICATIVE:
                gravite = NiveauGravite.SIGNIFICATIVE
            else:
                gravite = NiveauGravite.MINEURE

            modifications.append(Modification(
                type_modification=TypeModification.PRIX,
                chemin="prix.montant",
                valeur_originale=prix_promesse,
                valeur_nouvelle=prix_vente,
                gravite=gravite,
                description=f"Prix modifié de {prix_promesse}€ à {prix_vente}€ ({variation*100:.1f}%)"
            ))

        # Vérifier la ventilation du prix
        vent_promesse = promesse.get("prix", {}).get("ventilation", {})
        vent_vente = vente.get("prix", {}).get("ventilation", {})

        if vent_promesse != vent_vente and vent_promesse and vent_vente:
            modifications.append(Modification(
                type_modification=TypeModification.PRIX,
                chemin="prix.ventilation",
                valeur_originale=vent_promesse,
                valeur_nouvelle=vent_vente,
                gravite=NiveauGravite.SIGNIFICATIVE,
                description="Ventilation du prix modifiée"
            ))

        return modifications

    def _comparer_parties(self, promesse: Dict, vente: Dict) -> List[Modification]:
        """Compare les parties."""
        modifications = []

        # Vendeurs/Promettants
        promettants = promesse.get("promettants", promesse.get("vendeurs", []))
        vendeurs = vente.get("vendeurs", [])

        if len(promettants) != len(vendeurs):
            modifications.append(Modification(
                type_modification=TypeModification.PARTIES,
                chemin="vendeurs",
                valeur_originale=len(promettants),
                valeur_nouvelle=len(vendeurs),
                gravite=NiveauGravite.MAJEURE,
                description=f"Nombre de vendeurs modifié ({len(promettants)} → {len(vendeurs)})"
            ))
        else:
            # Vérifier si les personnes sont les mêmes
            noms_promettants = {p.get("nom", "").upper() for p in promettants}
            noms_vendeurs = {v.get("nom", "").upper() for v in vendeurs}

            if noms_promettants != noms_vendeurs:
                modifications.append(Modification(
                    type_modification=TypeModification.PARTIES,
                    chemin="vendeurs",
                    valeur_originale=list(noms_promettants),
                    valeur_nouvelle=list(noms_vendeurs),
                    gravite=NiveauGravite.MAJEURE,
                    description="Liste des vendeurs modifiée"
                ))

        # Bénéficiaires/Acquéreurs
        beneficiaires = promesse.get("beneficiaires", promesse.get("acquereurs", []))
        acquereurs = vente.get("acquereurs", [])

        if len(beneficiaires) != len(acquereurs):
            modifications.append(Modification(
                type_modification=TypeModification.PARTIES,
                chemin="acquereurs",
                valeur_originale=len(beneficiaires),
                valeur_nouvelle=len(acquereurs),
                gravite=NiveauGravite.MAJEURE,
                description=f"Nombre d'acquéreurs modifié ({len(beneficiaires)} → {len(acquereurs)})"
            ))
        else:
            noms_benef = {b.get("nom", "").upper() for b in beneficiaires}
            noms_acq = {a.get("nom", "").upper() for a in acquereurs}

            if noms_benef != noms_acq:
                modifications.append(Modification(
                    type_modification=TypeModification.PARTIES,
                    chemin="acquereurs",
                    valeur_originale=list(noms_benef),
                    valeur_nouvelle=list(noms_acq),
                    gravite=NiveauGravite.MAJEURE,
                    description="Liste des acquéreurs modifiée"
                ))

        return modifications

    def _comparer_bien(self, promesse: Dict, vente: Dict, stricte: bool) -> List[Modification]:
        """Compare les biens."""
        modifications = []

        bien_promesse = promesse.get("bien", {})
        bien_vente = vente.get("bien", {})

        # Adresse
        adresse_p = bien_promesse.get("adresse", {})
        adresse_v = bien_vente.get("adresse", {})

        if isinstance(adresse_p, dict) and isinstance(adresse_v, dict):
            rue_p = adresse_p.get("rue", "")
            rue_v = adresse_v.get("rue", "")

            if rue_p and rue_v and rue_p.lower() != rue_v.lower():
                modifications.append(Modification(
                    type_modification=TypeModification.BIEN,
                    chemin="bien.adresse.rue",
                    valeur_originale=rue_p,
                    valeur_nouvelle=rue_v,
                    gravite=NiveauGravite.MAJEURE,
                    description="Adresse du bien modifiée"
                ))

        # Lots (copropriété)
        lots_p = bien_promesse.get("lots", [])
        lots_v = bien_vente.get("lots", [])

        if len(lots_p) != len(lots_v):
            modifications.append(Modification(
                type_modification=TypeModification.BIEN,
                chemin="bien.lots",
                valeur_originale=len(lots_p),
                valeur_nouvelle=len(lots_v),
                gravite=NiveauGravite.MAJEURE,
                description=f"Nombre de lots modifié ({len(lots_p)} → {len(lots_v)})"
            ))

        # Surface Carrez
        surface_p = bien_promesse.get("superficie_carrez", {}).get("superficie_m2", 0)
        surface_v = bien_vente.get("superficie_carrez", {}).get("superficie_m2", 0)

        if surface_p and surface_v and abs(surface_p - surface_v) > 0.5:
            gravite = NiveauGravite.SIGNIFICATIVE
            if abs(surface_p - surface_v) / surface_p > 0.05:  # >5% de variation
                gravite = NiveauGravite.MAJEURE

            modifications.append(Modification(
                type_modification=TypeModification.BIEN,
                chemin="bien.superficie_carrez",
                valeur_originale=surface_p,
                valeur_nouvelle=surface_v,
                gravite=gravite,
                description=f"Surface Carrez modifiée ({surface_p}m² → {surface_v}m²)"
            ))

        return modifications

    def _comparer_financement(self, promesse: Dict, vente: Dict) -> List[Modification]:
        """Compare le financement."""
        modifications = []

        fin_promesse = promesse.get("financement", promesse.get("paiement", {}))
        fin_vente = vente.get("paiement", vente.get("financement", {}))

        prets_p = fin_promesse.get("prets", [])
        prets_v = fin_vente.get("prets", [])

        total_p = sum(p.get("montant", 0) for p in prets_p)
        total_v = sum(p.get("montant", 0) for p in prets_v)

        if abs(total_p - total_v) > 100:  # Plus de 100€ de différence
            modifications.append(Modification(
                type_modification=TypeModification.FINANCEMENT,
                chemin="paiement.prets",
                valeur_originale=total_p,
                valeur_nouvelle=total_v,
                gravite=NiveauGravite.SIGNIFICATIVE,
                description=f"Montant des prêts modifié ({total_p}€ → {total_v}€)"
            ))

        # Vérifier si prêt ajouté ou supprimé
        if len(prets_p) != len(prets_v):
            modifications.append(Modification(
                type_modification=TypeModification.FINANCEMENT,
                chemin="paiement.prets.count",
                valeur_originale=len(prets_p),
                valeur_nouvelle=len(prets_v),
                gravite=NiveauGravite.SIGNIFICATIVE,
                description=f"Nombre de prêts modifié ({len(prets_p)} → {len(prets_v)})"
            ))

        return modifications

    def _comparer_conditions(self, promesse: Dict, vente: Dict) -> List[Modification]:
        """Compare les conditions suspensives."""
        modifications = []

        cond_p = promesse.get("conditions_suspensives", {})
        cond_v = vente.get("conventions_anterieures", {}).get("compromis", {}).get("conditions_suspensives", {})

        # Conditions non réalisées
        if cond_v.get("conditions_realisees") is False:
            modifications.append(Modification(
                type_modification=TypeModification.CONDITIONS,
                chemin="conditions_suspensives.realisees",
                valeur_originale=True,
                valeur_nouvelle=False,
                gravite=NiveauGravite.MAJEURE,
                description="Conditions suspensives non réalisées"
            ))

        return modifications

    def _comparer_delais(self, promesse: Dict, vente: Dict) -> List[Modification]:
        """Compare les délais."""
        modifications = []

        delai_p = promesse.get("delai_realisation", "")
        date_vente = vente.get("acte", {}).get("date", {})

        # Si le délai de réalisation est dépassé
        if delai_p and date_vente:
            # Note: comparaison simplifiée - à améliorer avec parsing de dates
            pass

        return modifications

    def _generer_resume(self, rapport: RapportComparaison) -> str:
        """Génère un résumé textuel du rapport."""
        if not rapport.modifications:
            return "Aucune modification détectée entre la promesse et l'acte de vente."

        parties = []

        nb_mineures = sum(1 for m in rapport.modifications if m.gravite == NiveauGravite.MINEURE)
        nb_significatives = sum(1 for m in rapport.modifications if m.gravite == NiveauGravite.SIGNIFICATIVE)
        nb_majeures = sum(1 for m in rapport.modifications if m.gravite == NiveauGravite.MAJEURE)

        parties.append(f"{len(rapport.modifications)} modification(s) détectée(s)")

        if nb_majeures:
            parties.append(f"{nb_majeures} majeure(s)")
        if nb_significatives:
            parties.append(f"{nb_significatives} significative(s)")
        if nb_mineures:
            parties.append(f"{nb_mineures} mineure(s)")

        if rapport.avenant_necessaire:
            parties.append("AVENANT OBLIGATOIRE")
        elif rapport.avenant_recommande:
            parties.append("Avenant recommandé")

        return " - ".join(parties)

    def generer_avenant(
        self,
        rapport: RapportComparaison,
        promesse: Optional[Dict] = None,
        vente: Optional[Dict] = None
    ) -> str:
        """
        Génère le texte d'un avenant si des modifications le justifient.

        Args:
            rapport: Rapport de comparaison
            promesse: Données de la promesse (optionnel pour contexte)
            vente: Données de la vente (optionnel pour contexte)

        Returns:
            Texte de l'avenant en Markdown
        """
        if not rapport.modifications:
            return ""

        lignes = [
            "# AVENANT À LA PROMESSE DE VENTE",
            "",
            f"**Date**: {datetime.now().strftime('%d/%m/%Y')}",
            "",
            "---",
            "",
            "## OBJET DE L'AVENANT",
            "",
            "Le présent avenant a pour objet de modifier les conditions de la promesse "
            "de vente conclue entre les parties selon les termes ci-après.",
            "",
            "## MODIFICATIONS APPORTÉES",
            ""
        ]

        # Grouper par type de modification
        par_type: Dict[TypeModification, List[Modification]] = {}
        for mod in rapport.modifications:
            if mod.type_modification not in par_type:
                par_type[mod.type_modification] = []
            par_type[mod.type_modification].append(mod)

        # Prix
        if TypeModification.PRIX in par_type:
            lignes.append("### 1. MODIFICATION DU PRIX")
            lignes.append("")
            for mod in par_type[TypeModification.PRIX]:
                if "montant" in mod.chemin:
                    lignes.append(f"Le prix de vente initialement fixé à **{mod.valeur_originale:,.0f} euros** "
                                  f"est porté à **{mod.valeur_nouvelle:,.0f} euros**.")
                else:
                    lignes.append(f"- {mod.description}")
            lignes.append("")

        # Parties
        if TypeModification.PARTIES in par_type:
            lignes.append("### 2. MODIFICATION DES PARTIES")
            lignes.append("")
            for mod in par_type[TypeModification.PARTIES]:
                lignes.append(f"- {mod.description}")
            lignes.append("")

        # Bien
        if TypeModification.BIEN in par_type:
            lignes.append("### 3. MODIFICATION DU BIEN")
            lignes.append("")
            for mod in par_type[TypeModification.BIEN]:
                lignes.append(f"- {mod.description}")
            lignes.append("")

        # Financement
        if TypeModification.FINANCEMENT in par_type:
            lignes.append("### 4. MODIFICATION DU FINANCEMENT")
            lignes.append("")
            for mod in par_type[TypeModification.FINANCEMENT]:
                lignes.append(f"- {mod.description}")
            lignes.append("")

        # Autres modifications
        for type_mod, mods in par_type.items():
            if type_mod not in [TypeModification.PRIX, TypeModification.PARTIES,
                                TypeModification.BIEN, TypeModification.FINANCEMENT]:
                lignes.append(f"### MODIFICATION: {type_mod.value.upper()}")
                lignes.append("")
                for mod in mods:
                    lignes.append(f"- {mod.description}")
                lignes.append("")

        # Clause de maintien
        lignes.extend([
            "## MAINTIEN DES AUTRES STIPULATIONS",
            "",
            "Toutes les autres clauses et conditions de la promesse de vente initiale "
            "demeurent inchangées et restent en vigueur.",
            "",
            "## SIGNATURES",
            "",
            "Fait à _____________, le _____________",
            "",
            "**Le(s) Promettant(s):**",
            "",
            "",
            "**Le(s) Bénéficiaire(s):**",
            ""
        ])

        return "\n".join(lignes)

    def sauvegarder_historique(self, chemin: Path) -> None:
        """Sauvegarde l'historique dans un fichier JSON."""
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(
                [r.to_dict() for r in self.historique],
                f,
                ensure_ascii=False,
                indent=2
            )

    def charger_historique(self, chemin: Path) -> None:
        """Charge l'historique depuis un fichier JSON."""
        if chemin.exists():
            with open(chemin, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Reconstruction simplifiée - l'historique complet nécessiterait plus de parsing
                self.historique = []


# ============================================================================
# CLI
# ============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Suivi des modifications promesse/vente")

    parser.add_argument("--promesse", "-p", required=True, help="Fichier JSON de la promesse")
    parser.add_argument("--vente", "-v", required=True, help="Fichier JSON de l'acte de vente")
    parser.add_argument("--avenant", "-a", help="Fichier de sortie pour l'avenant (si nécessaire)")
    parser.add_argument("--json", "-j", action="store_true", help="Sortie JSON")

    args = parser.parse_args()

    # Charger les fichiers
    with open(args.promesse, 'r', encoding='utf-8') as f:
        promesse = json.load(f)

    with open(args.vente, 'r', encoding='utf-8') as f:
        vente = json.load(f)

    # Comparer
    suivi = SuiviModifications()
    rapport = suivi.comparer(promesse, vente)

    # Afficher
    if args.json:
        print(json.dumps(rapport.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print("RAPPORT DE COMPARAISON PROMESSE / VENTE")
        print("=" * 60)

        print(f"\nRésumé: {rapport.resume}")

        if rapport.modifications:
            print(f"\nModifications détectées: {len(rapport.modifications)}")
            for i, mod in enumerate(rapport.modifications, 1):
                print(f"\n  {i}. [{mod.gravite.value.upper()}] {mod.type_modification.value}")
                print(f"     {mod.description}")
                print(f"     Chemin: {mod.chemin}")

        if rapport.avenant_necessaire:
            print("\n[!] AVENANT OBLIGATOIRE")
        elif rapport.avenant_recommande:
            print("\n[i] Avenant recommandé")
        else:
            print("\n[OK] Pas d'avenant nécessaire")

    # Générer avenant si demandé
    if args.avenant and (rapport.avenant_necessaire or rapport.avenant_recommande):
        avenant = suivi.generer_avenant(rapport, promesse, vente)
        with open(args.avenant, 'w', encoding='utf-8') as f:
            f.write(avenant)
        print(f"\nAvenant généré: {args.avenant}")


if __name__ == "__main__":
    main()
