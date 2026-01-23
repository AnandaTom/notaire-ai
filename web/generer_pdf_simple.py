"""
Génère un PDF du formulaire web NotaireAI.
Utilise le navigateur Chrome/Edge en mode headless via Playwright.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

async def generer_pdf_formulaire(output_path=None, avec_exemple=False):
    """
    Génère un PDF du formulaire web en utilisant Playwright.

    Args:
        output_path: Chemin de sortie du PDF (optionnel)
        avec_exemple: Si True, remplit le formulaire avec l'exemple
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Erreur: playwright n'est pas installé", file=sys.stderr)
        print("\n📦 Installation requise:", file=sys.stderr)
        print("   pip install playwright", file=sys.stderr)
        print("   playwright install chromium", file=sys.stderr)
        sys.exit(1)

    # Chemins
    web_dir = Path(__file__).parent
    html_path = web_dir / "index.html"

    # Sortie par défaut
    if output_path is None:
        suffix = "_exemple" if avec_exemple else ""
        output_path = web_dir.parent / "outputs" / f"formulaire_vendeur{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Génération du PDF du formulaire...")
    print(f"   Source: {html_path}")
    print(f"   Sortie: {output_path}")

    async with async_playwright() as p:
        # Lancer le navigateur
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Charger le fichier HTML
        await page.goto(f"file:///{html_path.resolve().as_posix()}")

        # Attendre que la page soit chargée
        await page.wait_for_load_state("networkidle")

        if avec_exemple:
            print("   Mode: Avec exemple pré-rempli")
            # Remplir le formulaire avec l'exemple
            await page.evaluate("fillExample()")
            # Attendre un peu pour que les champs soient remplis
            await page.wait_for_timeout(500)

        # Masquer les boutons d'action avant l'impression
        await page.add_style_tag(content="""
            .form-actions { display: none !important; }
            .result { display: none !important; }
            @page { margin: 2cm; }
        """)

        # Générer le PDF
        await page.pdf(
            path=str(output_path),
            format="A4",
            print_background=True,
            margin={
                "top": "2cm",
                "right": "2cm",
                "bottom": "2cm",
                "left": "2cm"
            }
        )

        await browser.close()

    print(f"✅ PDF généré avec succès!")
    print(f"   Taille: {output_path.stat().st_size / 1024:.1f} Ko")

    return str(output_path)

def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Génère un PDF du formulaire web")
    parser.add_argument('--output', '-o', help='Chemin de sortie du PDF')
    parser.add_argument('--exemple', '-e', action='store_true', help='Générer avec exemple pré-rempli')

    args = parser.parse_args()

    try:
        pdf_path = asyncio.run(generer_pdf_formulaire(args.output, args.exemple))
        print(f"\n📍 Fichier PDF: {pdf_path}")

    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
