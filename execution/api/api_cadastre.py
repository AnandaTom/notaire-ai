#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_cadastre.py
---------------
Endpoints API pour le service cadastre.
Permet au frontend de geocoder des adresses, chercher des parcelles,
et enrichir automatiquement les données cadastrales d'un dossier.

Endpoints:
    POST /cadastre/geocoder     - Adresse → code_insee + coordinates
    GET  /cadastre/parcelle     - code_insee + section + numero → parcelle
    GET  /cadastre/sections     - code_insee → liste sections
    POST /cadastre/enrichir     - Données dossier → données enrichies
    GET  /cadastre/surface      - Conversion surface texte → m²
"""

import sys
from typing import Optional

if sys.platform == "win32":
    for stream in [sys.stdout, sys.stderr]:
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

# =============================================================================
# FastAPI Router
# =============================================================================

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    router = APIRouter(prefix="/cadastre", tags=["Cadastre"])

    # ── Modèles Pydantic ──

    class AdresseRequest(BaseModel):
        adresse: str = Field(..., description="Adresse complète à geocoder")

    class GeocodageResponse(BaseModel):
        code_insee: str
        code_postal: str
        ville: str
        district: str = ""
        latitude: Optional[float] = None
        longitude: Optional[float] = None
        label: str = ""
        score: float = 0

    class ParcelleResponse(BaseModel):
        section: str
        numero: str
        feuille: str = ""
        code_dep: str = ""
        code_com: str = ""
        code_insee: str = ""
        surface_m2: Optional[int] = None

    class SectionResponse(BaseModel):
        section: str
        feuille: str = ""
        code_dep: str = ""
        code_com: str = ""

    class EnrichirRequest(BaseModel):
        donnees: dict = Field(..., description="Données du dossier à enrichir")

    class EnrichirResponse(BaseModel):
        donnees: dict
        rapport: dict

    class SurfaceResponse(BaseModel):
        texte: str
        m2: Optional[int] = None
        reconversion: str = ""

    # ── Endpoints ──

    @router.post("/geocoder", response_model=GeocodageResponse)
    async def geocoder_adresse(req: AdresseRequest):
        """Geocode une adresse française → code_insee, coordinates."""
        from execution.services.cadastre_service import CadastreService
        svc = CadastreService()
        result = svc.geocoder_adresse(req.adresse)
        if not result:
            raise HTTPException(404, f"Adresse non trouvee: {req.adresse}")
        return GeocodageResponse(**result)

    @router.get("/parcelle", response_model=ParcelleResponse)
    async def chercher_parcelle(
        code_insee: str = Query(..., description="Code INSEE commune (5 chiffres)"),
        section: str = Query(..., description="Section cadastrale (2 car.)"),
        numero: str = Query(..., description="Numero de parcelle"),
    ):
        """Recherche une parcelle cadastrale."""
        from execution.services.cadastre_service import CadastreService
        svc = CadastreService()
        result = svc.chercher_parcelle(code_insee, section, numero)
        if not result:
            raise HTTPException(
                404,
                f"Parcelle non trouvee: {code_insee}/{section}/{numero}"
            )
        # Exclure la géométrie GeoJSON (trop volumineux pour l'API)
        result.pop("geometry", None)
        return ParcelleResponse(**result)

    @router.get("/sections", response_model=list[SectionResponse])
    async def lister_sections(
        code_insee: str = Query(..., description="Code INSEE commune"),
    ):
        """Liste toutes les sections cadastrales d'une commune."""
        from execution.services.cadastre_service import CadastreService
        svc = CadastreService()
        sections = svc.lister_sections(code_insee)
        return [SectionResponse(**s) for s in sections]

    @router.post("/enrichir", response_model=EnrichirResponse)
    async def enrichir_cadastre(req: EnrichirRequest):
        """Enrichit les données d'un dossier avec le cadastre officiel."""
        from execution.services.cadastre_service import CadastreService
        svc = CadastreService()
        result = svc.enrichir_cadastre(req.donnees)
        return EnrichirResponse(**result)

    @router.get("/surface", response_model=SurfaceResponse)
    async def convertir_surface(
        texte: str = Query(..., description="Surface a convertir (ex: '00 ha 05 a 30 ca')"),
    ):
        """Convertit une surface textuelle en m²."""
        from execution.services.cadastre_service import CadastreService
        m2 = CadastreService.surface_texte_vers_m2(texte)
        reconversion = CadastreService.m2_vers_surface_texte(m2) if m2 else ""
        return SurfaceResponse(texte=texte, m2=m2, reconversion=reconversion)

except ImportError:
    router = None
    print("[WARN] FastAPI non installe. Endpoints cadastre non disponibles.")
