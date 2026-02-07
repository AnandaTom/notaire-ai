#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cadastre_service.py
-------------------
Service d'accès aux données cadastrales via les APIs gouvernementales françaises.

APIs utilisées:
- API Adresse (BAN): geocoding adresse → code_insee, coordinates
  https://api-adresse.data.gouv.fr/search/
- API Carto Cadastre (IGN): code_insee + section + numero → parcelle GeoJSON
  https://apicarto.ign.fr/api/cadastre/

Usage:
    from execution.services.cadastre_service import CadastreService

    service = CadastreService()

    # Geocoder une adresse
    geo = service.geocoder_adresse("12 rue de la Paix, 75002 Paris")
    # → {"code_insee": "75102", "latitude": 48.869, "longitude": 2.331, ...}

    # Chercher une parcelle
    parcelle = service.chercher_parcelle("75102", "AB", "0145")
    # → {"section": "AB", "numero": "0145", "geometry": {...}, ...}

    # Enrichir automatiquement les données d'un dossier
    donnees = service.enrichir_cadastre(donnees_dossier)
"""

import json
import re
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlencode

from execution.security.secure_delete import secure_delete_file

try:
    import requests
except ImportError:
    requests = None

# Encodage UTF-8 Windows
if sys.platform == "win32":
    for stream in [sys.stdout, sys.stderr]:
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# CACHE LOCAL
# =============================================================================

class CacheLocal:
    """Cache fichier JSON pour éviter les appels API redondants."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl_heures: int = 24):
        self.cache_dir = cache_dir or Path(".tmp/cache_cadastre")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_secondes = ttl_heures * 3600

    def _cle_fichier(self, cle: str) -> Path:
        h = hashlib.md5(cle.encode()).hexdigest()
        return self.cache_dir / f"{h}.json"

    def get(self, cle: str) -> Optional[dict]:
        fichier = self._cle_fichier(cle)
        if not fichier.exists():
            return None
        try:
            data = json.loads(fichier.read_text(encoding="utf-8"))
            age = time.time() - data.get("_timestamp", 0)
            if age > self.ttl_secondes:
                secure_delete_file(fichier)
                return None
            return data.get("valeur")
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, cle: str, valeur: dict):
        fichier = self._cle_fichier(cle)
        try:
            fichier.write_text(
                json.dumps({"_timestamp": time.time(), "valeur": valeur},
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass


# =============================================================================
# SERVICE CADASTRE
# =============================================================================

class CadastreService:
    """Service d'accès aux données cadastrales via APIs gouvernementales."""

    API_ADRESSE = "https://api-adresse.data.gouv.fr/search/"
    API_CADASTRE = "https://apicarto.ign.fr/api/cadastre"

    def __init__(self, cache_ttl_heures: int = 24, timeout: int = 10):
        if requests is None:
            raise ImportError(
                "Le module 'requests' est requis. Installer: pip install requests"
            )
        self.timeout = timeout
        self.cache = CacheLocal(ttl_heures=cache_ttl_heures)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Notomai/1.7.0 (notaire-ai)",
            "Accept": "application/json",
        })

    # =========================================================================
    # API ADRESSE (BAN) — Geocoding
    # =========================================================================

    def geocoder_adresse(self, adresse: str, limit: int = 1) -> Optional[Dict]:
        """Geocode une adresse française → code_insee, coordinates, etc.

        Args:
            adresse: Adresse complète ("12 rue de la Paix, 75002 Paris")
            limit: Nombre max de résultats

        Returns:
            {
                "code_insee": "75102",
                "code_postal": "75002",
                "ville": "Paris",
                "latitude": 48.869141,
                "longitude": 2.331303,
                "label": "12 Rue de la Paix 75002 Paris",
                "score": 0.964
            }
            ou None si non trouvé
        """
        cle_cache = f"geocode:{adresse}"
        cached = self.cache.get(cle_cache)
        if cached:
            return cached

        params = {"q": adresse, "limit": limit}
        try:
            resp = self.session.get(
                self.API_ADRESSE, params=params, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Geocodage echoue pour '{adresse}': {e}")
            return None

        features = data.get("features", [])
        if not features:
            return None

        f = features[0]
        props = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [None, None])

        resultat = {
            "code_insee": props.get("citycode", ""),
            "code_postal": props.get("postcode", ""),
            "ville": props.get("city", ""),
            "district": props.get("district", ""),
            "latitude": coords[1],
            "longitude": coords[0],
            "label": props.get("label", ""),
            "score": props.get("score", 0),
        }
        self.cache.set(cle_cache, resultat)
        return resultat

    # =========================================================================
    # API CARTO CADASTRE (IGN) — Parcelles
    # =========================================================================

    def chercher_parcelle(
        self,
        code_insee: str,
        section: str,
        numero: str,
    ) -> Optional[Dict]:
        """Recherche une parcelle cadastrale par code_insee + section + numéro.

        Args:
            code_insee: Code INSEE commune (5 chiffres, ex: "75102")
            section: Section cadastrale (2 caractères, ex: "AB")
            numero: Numéro parcelle (4 chiffres, ex: "0145")

        Returns:
            {
                "section": "AB",
                "numero": "0145",
                "feuille": "1",
                "code_dep": "75",
                "code_com": "102",
                "code_insee": "75102",
                "geometry": { GeoJSON },
                "surface_m2": 530  (calculée depuis géométrie si disponible)
            }
            ou None si non trouvé
        """
        # Normaliser le numéro (padding 4 chiffres)
        numero_norm = numero.lstrip("0").zfill(4)
        section_norm = section.upper().strip()

        cle_cache = f"parcelle:{code_insee}:{section_norm}:{numero_norm}"
        cached = self.cache.get(cle_cache)
        if cached:
            return cached

        params = {
            "code_insee": code_insee,
            "section": section_norm,
            "numero": numero_norm,
        }
        try:
            resp = self.session.get(
                f"{self.API_CADASTRE}/parcelle",
                params=params,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Recherche parcelle echouee ({code_insee}/{section_norm}/{numero_norm}): {e}")
            return None

        features = data.get("features", [])
        if not features:
            return None

        f = features[0]
        props = f.get("properties", {})
        geometry = f.get("geometry")

        resultat = {
            "section": props.get("section", section_norm),
            "numero": props.get("numero", numero_norm),
            "feuille": props.get("feuille", ""),
            "code_dep": props.get("code_dep", ""),
            "code_com": props.get("code_com", ""),
            "code_insee": code_insee,
            "geometry": geometry,
            "surface_m2": self._calculer_surface_geojson(geometry),
        }
        self.cache.set(cle_cache, resultat)
        return resultat

    def lister_sections(self, code_insee: str) -> List[Dict]:
        """Liste toutes les sections cadastrales d'une commune.

        Returns:
            [{"section": "AB", "feuille": "1", "code_dep": "75", ...}, ...]
        """
        cle_cache = f"sections:{code_insee}"
        cached = self.cache.get(cle_cache)
        if cached:
            return cached

        try:
            resp = self.session.get(
                f"{self.API_CADASTRE}/division",
                params={"code_insee": code_insee, "_limit": 500},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Liste sections echouee ({code_insee}): {e}")
            return []

        sections = []
        for f in data.get("features", []):
            props = f.get("properties", {})
            sections.append({
                "section": props.get("section", ""),
                "feuille": props.get("feuille", ""),
                "code_dep": props.get("code_dep", ""),
                "code_com": props.get("code_com", ""),
            })
        self.cache.set(cle_cache, sections)
        return sections

    def chercher_parcelles_section(
        self, code_insee: str, section: str
    ) -> List[Dict]:
        """Liste toutes les parcelles d'une section.

        Returns:
            [{"numero": "0145", "section": "AB", ...}, ...]
        """
        cle_cache = f"parcelles_section:{code_insee}:{section.upper()}"
        cached = self.cache.get(cle_cache)
        if cached:
            return cached

        try:
            resp = self.session.get(
                f"{self.API_CADASTRE}/parcelle",
                params={
                    "code_insee": code_insee,
                    "section": section.upper(),
                    "_limit": 1000,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Parcelles section echouees ({code_insee}/{section}): {e}")
            return []

        parcelles = []
        for f in data.get("features", []):
            props = f.get("properties", {})
            parcelles.append({
                "numero": props.get("numero", ""),
                "section": props.get("section", ""),
                "feuille": props.get("feuille", ""),
            })
        self.cache.set(cle_cache, parcelles)
        return parcelles

    # =========================================================================
    # ENRICHISSEMENT AUTOMATIQUE
    # =========================================================================

    def enrichir_cadastre(self, donnees: Dict) -> Dict[str, Any]:
        """Enrichit les données d'un dossier avec le cadastre officiel.

        Chaîne de résolution:
        1. Si bien.cadastre existe → valider/enrichir via API
        2. Si bien.adresse existe mais pas cadastre → geocoder + proposer
        3. Retourner données enrichies + rapport

        Args:
            donnees: Données du dossier (structure standard Notomai)

        Returns:
            {
                "donnees": { données enrichies },
                "rapport": {
                    "cadastre_enrichi": bool,
                    "parcelles_trouvees": int,
                    "parcelles_validees": int,
                    "code_insee": str,
                    "geocodage": { résultat geocoding },
                    "warnings": [],
                    "erreurs": [],
                }
            }
        """
        rapport = {
            "cadastre_enrichi": False,
            "parcelles_trouvees": 0,
            "parcelles_validees": 0,
            "code_insee": None,
            "geocodage": None,
            "warnings": [],
            "erreurs": [],
        }

        bien = donnees.get("bien", {})
        if not bien:
            rapport["erreurs"].append("Pas de section 'bien' dans les donnees")
            return {"donnees": donnees, "rapport": rapport}

        # ── Étape 1: Geocoder l'adresse pour obtenir code_insee ──
        adresse = bien.get("adresse", {})
        code_insee = None

        if adresse:
            adresse_str = self._formater_adresse(adresse)
            if adresse_str:
                geo = self.geocoder_adresse(adresse_str)
                if geo:
                    code_insee = geo["code_insee"]
                    rapport["geocodage"] = geo
                    rapport["code_insee"] = code_insee

                    # Enrichir l'adresse si données manquantes
                    if not adresse.get("code_postal") and geo.get("code_postal"):
                        adresse["code_postal"] = geo["code_postal"]
                    if not adresse.get("ville") and geo.get("ville"):
                        adresse["ville"] = geo["ville"]
                else:
                    rapport["warnings"].append(
                        f"Geocodage echoue pour: {adresse_str}"
                    )

        # ── Étape 2: Enrichir les parcelles existantes ──
        cadastre = bien.get("cadastre", [])
        if cadastre and code_insee:
            for i, parcelle in enumerate(cadastre):
                section = parcelle.get("section", "")
                numero = parcelle.get("numero", "")
                if not section or not numero:
                    continue

                resultat_api = self.chercher_parcelle(code_insee, section, numero)
                if resultat_api:
                    rapport["parcelles_trouvees"] += 1
                    rapport["parcelles_validees"] += 1

                    # Enrichir avec données API
                    parcelle["code_insee"] = code_insee
                    parcelle["verifie"] = True
                    parcelle["source"] = "api_cadastre"
                    if resultat_api.get("surface_m2"):
                        parcelle["surface_m2"] = resultat_api["surface_m2"]
                    if resultat_api.get("feuille"):
                        parcelle["feuille"] = resultat_api["feuille"]

                    # Coordonnées du centroïde
                    geo_parcelle = rapport.get("geocodage")
                    if geo_parcelle:
                        parcelle["coordinates"] = {
                            "latitude": geo_parcelle["latitude"],
                            "longitude": geo_parcelle["longitude"],
                        }

                    rapport["cadastre_enrichi"] = True
                else:
                    parcelle["verifie"] = False
                    rapport["warnings"].append(
                        f"Parcelle {section}/{numero} non trouvee dans le cadastre officiel"
                    )

        # ── Étape 3: Si pas de cadastre mais adresse → proposer lookup ──
        elif not cadastre and code_insee:
            rapport["warnings"].append(
                f"Aucune reference cadastrale. Code INSEE: {code_insee}. "
                f"Utilisez lister_sections('{code_insee}') pour trouver les sections."
            )

        # Remettre dans les données
        bien["cadastre"] = cadastre
        donnees["bien"] = bien

        return {"donnees": donnees, "rapport": rapport}

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _formater_adresse(self, adresse: Dict) -> Optional[str]:
        """Formate un dict adresse en chaîne pour geocoding."""
        parties = []
        if adresse.get("numero"):
            parties.append(str(adresse["numero"]))
        if adresse.get("voie"):
            parties.append(adresse["voie"])
        if adresse.get("code_postal"):
            parties.append(str(adresse["code_postal"]))
        if adresse.get("ville"):
            parties.append(adresse["ville"])
        return " ".join(parties) if parties else None

    def _calculer_surface_geojson(self, geometry: Optional[Dict]) -> Optional[int]:
        """Calcule surface approximative depuis géométrie GeoJSON (m²).

        Utilise la formule de Shoelace pour polygones en coordonnées WGS84.
        Approximation suffisante pour des parcelles cadastrales.
        """
        if not geometry:
            return None

        geo_type = geometry.get("type", "")
        coords = geometry.get("coordinates")
        if not coords:
            return None

        try:
            import math

            def _surface_polygon(ring):
                """Surface approx d'un anneau en m² (Shoelace + projection)."""
                n = len(ring)
                if n < 3:
                    return 0
                # Point central pour la projection
                lat_c = sum(p[1] for p in ring) / n
                # Facteur de conversion degrés → mètres à cette latitude
                m_per_deg_lat = 111_320
                m_per_deg_lon = 111_320 * math.cos(math.radians(lat_c))

                surface = 0
                for i in range(n):
                    j = (i + 1) % n
                    xi = ring[i][0] * m_per_deg_lon
                    yi = ring[i][1] * m_per_deg_lat
                    xj = ring[j][0] * m_per_deg_lon
                    yj = ring[j][1] * m_per_deg_lat
                    surface += xi * yj - xj * yi
                return abs(surface) / 2

            if geo_type == "Polygon":
                return round(_surface_polygon(coords[0]))
            elif geo_type == "MultiPolygon":
                total = sum(_surface_polygon(poly[0]) for poly in coords)
                return round(total)
        except Exception:
            return None

        return None

    @staticmethod
    def surface_texte_vers_m2(surface_texte: str) -> Optional[int]:
        """Convertit "00 ha 05 a 30 ca" → 530 m².

        Formats acceptés:
        - "00 ha 05 a 30 ca"
        - "5a 30ca"
        - "530 m²"
        - "0,0530 ha"
        """
        if not surface_texte:
            return None

        texte = surface_texte.strip().lower()

        # Format direct m²
        m = re.match(r"(\d+(?:[,\.]\d+)?)\s*m[²2]", texte)
        if m:
            return round(float(m.group(1).replace(",", ".")))

        # Format hectares décimal
        m = re.match(r"(\d+(?:[,\.]\d+)?)\s*ha$", texte)
        if m:
            return round(float(m.group(1).replace(",", ".")) * 10000)

        # Format ha/a/ca
        ha = a = ca = 0
        m_ha = re.search(r"(\d+)\s*ha", texte)
        m_a = re.search(r"(\d+)\s*a(?:\s|$|[^-z])", texte)
        m_ca = re.search(r"(\d+)\s*ca", texte)

        if m_ha:
            ha = int(m_ha.group(1))
        if m_a:
            a = int(m_a.group(1))
        if m_ca:
            ca = int(m_ca.group(1))

        if ha or a or ca:
            return ha * 10000 + a * 100 + ca

        return None

    @staticmethod
    def m2_vers_surface_texte(m2: int) -> str:
        """Convertit 530 m² → "00 ha 05 a 30 ca"."""
        ha = m2 // 10000
        reste = m2 % 10000
        a = reste // 100
        ca = reste % 100
        return f"{ha:02d} ha {a:02d} a {ca:02d} ca"


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI pour tester le service cadastre."""
    import argparse

    parser = argparse.ArgumentParser(description="Service Cadastre")
    sub = parser.add_subparsers(dest="commande")

    # Geocoder
    p_geo = sub.add_parser("geocoder", help="Geocoder une adresse")
    p_geo.add_argument("adresse", help="Adresse a geocoder")

    # Parcelle
    p_parc = sub.add_parser("parcelle", help="Chercher une parcelle")
    p_parc.add_argument("code_insee", help="Code INSEE commune")
    p_parc.add_argument("section", help="Section cadastrale")
    p_parc.add_argument("numero", help="Numero de parcelle")

    # Sections
    p_sec = sub.add_parser("sections", help="Lister les sections")
    p_sec.add_argument("code_insee", help="Code INSEE commune")

    # Enrichir
    p_enr = sub.add_parser("enrichir", help="Enrichir un fichier de donnees")
    p_enr.add_argument("fichier", help="Fichier JSON a enrichir")
    p_enr.add_argument("--output", "-o", help="Fichier de sortie")

    # Surface
    p_surf = sub.add_parser("surface", help="Convertir surface")
    p_surf.add_argument("texte", help="Surface a convertir (ex: '00 ha 05 a 30 ca')")

    args = parser.parse_args()
    if not args.commande:
        parser.print_help()
        return

    service = CadastreService()

    if args.commande == "geocoder":
        result = service.geocoder_adresse(args.adresse)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Adresse non trouvee")
            sys.exit(1)

    elif args.commande == "parcelle":
        result = service.chercher_parcelle(
            args.code_insee, args.section, args.numero
        )
        if result:
            # Ne pas afficher la géométrie complète en CLI
            affichage = {k: v for k, v in result.items() if k != "geometry"}
            affichage["geometry"] = (
                result["geometry"]["type"] if result.get("geometry") else None
            )
            print(json.dumps(affichage, indent=2, ensure_ascii=False))
        else:
            print("Parcelle non trouvee")
            sys.exit(1)

    elif args.commande == "sections":
        sections = service.lister_sections(args.code_insee)
        if sections:
            print(f"{len(sections)} sections trouvees:")
            for s in sections[:20]:
                print(f"  Section {s['section']} (feuille {s['feuille']})")
            if len(sections) > 20:
                print(f"  ... et {len(sections) - 20} autres")
        else:
            print("Aucune section trouvee")

    elif args.commande == "enrichir":
        donnees = json.loads(Path(args.fichier).read_text(encoding="utf-8"))
        resultat = service.enrichir_cadastre(donnees)

        rapport = resultat["rapport"]
        print(f"Code INSEE: {rapport['code_insee']}")
        print(f"Parcelles trouvees: {rapport['parcelles_trouvees']}")
        print(f"Parcelles validees: {rapport['parcelles_validees']}")
        print(f"Enrichi: {rapport['cadastre_enrichi']}")
        if rapport["warnings"]:
            for w in rapport["warnings"]:
                print(f"  [WARN] {w}")

        if args.output:
            Path(args.output).write_text(
                json.dumps(resultat["donnees"], indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"Donnees enrichies sauvegardees: {args.output}")

    elif args.commande == "surface":
        m2 = CadastreService.surface_texte_vers_m2(args.texte)
        if m2 is not None:
            print(f"{args.texte} = {m2} m2")
            print(f"Reconversion: {CadastreService.m2_vers_surface_texte(m2)}")
        else:
            print("Format non reconnu")


if __name__ == "__main__":
    main()
