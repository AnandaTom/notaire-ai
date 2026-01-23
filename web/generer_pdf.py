"""
Génère un PDF du formulaire web NotaireAI.
Utilise weasyprint pour convertir HTML → PDF.
"""

import sys
from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

def generer_pdf_formulaire(output_path=None):
    """
    Génère un PDF du formulaire web.

    Args:
        output_path: Chemin de sortie du PDF (optionnel)
    """
    # Chemins
    web_dir = Path(__file__).parent
    html_path = web_dir / "index.html"
    css_path = web_dir / "styles.css"

    # Sortie par défaut
    if output_path is None:
        output_path = web_dir.parent / "outputs" / f"formulaire_vendeur_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Génération du PDF du formulaire...")
    print(f"   Source: {html_path}")
    print(f"   Sortie: {output_path}")

    # Lire le HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Lire le CSS
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # CSS spécifique pour le PDF (ajustements d'impression)
    css_print = """
        @page {
            size: A4;
            margin: 2cm;
        }

        body {
            background: white !important;
        }

        .container {
            box-shadow: none !important;
            max-width: 100% !important;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        .form-actions {
            display: none !important;
        }

        .result {
            display: none !important;
        }

        .form-section {
            page-break-inside: avoid;
        }

        input, select {
            border: 2px solid #333 !important;
            background: white !important;
        }
    """

    # Générer le PDF
    try:
        html = HTML(string=html_content, base_url=str(web_dir))
        css_main = CSS(string=css_content)
        css_extra = CSS(string=css_print)

        html.write_pdf(
            output_path,
            stylesheets=[css_main, css_extra]
        )

        print(f"✅ PDF généré avec succès!")
        print(f"   Taille: {output_path.stat().st_size / 1024:.1f} Ko")

        return str(output_path)

    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF: {e}", file=sys.stderr)
        raise

def generer_pdf_exemple():
    """
    Génère un PDF du formulaire pré-rempli avec l'exemple.
    """
    # Créer une version HTML avec les données d'exemple
    web_dir = Path(__file__).parent
    html_path = web_dir / "index.html"

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Injecter un script pour remplir automatiquement le formulaire
    script_autofill = """
    <script>
    window.onload = function() {
        // Simuler le clic sur "Remplir avec exemple"
        fillExample();
    };
    </script>
    """

    html_content = html_content.replace('</body>', script_autofill + '</body>')

    # Générer le PDF
    output_path = web_dir.parent / "outputs" / f"formulaire_vendeur_exemple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Génération du PDF avec exemple pré-rempli...")

    try:
        from weasyprint import HTML, CSS

        html = HTML(string=html_content, base_url=str(web_dir))

        # CSS pour le PDF
        css_print = """
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                background: white !important;
            }
            .container {
                box-shadow: none !important;
            }
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                -webkit-print-color-adjust: exact;
            }
            .form-actions, .result {
                display: none !important;
            }
        """

        css_extra = CSS(string=css_print)

        html.write_pdf(output_path, stylesheets=[css_extra])

        print(f"✅ PDF généré avec succès!")
        print(f"   Fichier: {output_path}")

        return str(output_path)

    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Génère un PDF du formulaire web")
    parser.add_argument('--output', '-o', help='Chemin de sortie du PDF')
    parser.add_argument('--exemple', '-e', action='store_true', help='Générer avec exemple pré-rempli')

    args = parser.parse_args()

    try:
        if args.exemple:
            pdf_path = generer_pdf_exemple()
        else:
            pdf_path = generer_pdf_formulaire(args.output)

        print(f"\n📍 Fichier PDF: {pdf_path}")

    except ImportError:
        print("❌ Erreur: weasyprint n'est pas installé", file=sys.stderr)
        print("\n📦 Installation requise:", file=sys.stderr)
        print("   pip install weasyprint", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        sys.exit(1)
