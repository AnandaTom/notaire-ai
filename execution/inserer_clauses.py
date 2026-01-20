#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour insérer automatiquement des clauses modulaires dans un template
Supporte l'insertion à une position spécifique ou avant/après un marqueur
"""
import sys
import argparse
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def charger_clause(clause_path):
    """Charge le contenu d'une clause"""
    with open(clause_path, 'r', encoding='utf-8') as f:
        return f.read()

def inserer_dans_template(template_path, clause_content, position='fin', marqueur=None, offset_lignes=0):
    """
    Insère une clause dans un template

    Args:
        template_path: Chemin du template
        clause_content: Contenu de la clause à insérer
        position: 'debut', 'fin', 'avant', 'apres', 'ligne'
        marqueur: Texte à rechercher (pour avant/apres)
        offset_lignes: Numéro de ligne (pour position='ligne')
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    if position == 'debut':
        # Insérer au début (après l'en-tête Jinja2 s'il existe)
        index = 0
        # Chercher fin de l'en-tête de commentaire
        for i, ligne in enumerate(lignes):
            if ligne.strip().startswith('{#') or ligne.strip().startswith('#}'):
                continue
            if not ligne.strip().startswith('#'):
                index = i
                break

        lignes.insert(index, '\n' + clause_content + '\n\n')

    elif position == 'fin':
        # Insérer avant les dernières lignes (signature, etc.)
        index = len(lignes) - 10  # 10 lignes avant la fin par défaut
        lignes.insert(index, '\n' + clause_content + '\n\n')

    elif position == 'avant' and marqueur:
        # Chercher le marqueur et insérer avant
        for i, ligne in enumerate(lignes):
            if marqueur in ligne:
                lignes.insert(i, '\n' + clause_content + '\n\n')
                break
        else:
            print(f"[ATTENTION] Marqueur '{marqueur}' non trouvé. Insertion en fin.")
            lignes.insert(len(lignes) - 10, '\n' + clause_content + '\n\n')

    elif position == 'apres' and marqueur:
        # Chercher le marqueur et insérer après
        for i, ligne in enumerate(lignes):
            if marqueur in ligne:
                lignes.insert(i + 1, '\n' + clause_content + '\n\n')
                break
        else:
            print(f"[ATTENTION] Marqueur '{marqueur}' non trouvé. Insertion en fin.")
            lignes.insert(len(lignes) - 10, '\n' + clause_content + '\n\n')

    elif position == 'ligne':
        # Insérer à une ligne spécifique
        lignes.insert(offset_lignes, '\n' + clause_content + '\n\n')

    # Écrire le template modifié
    with open(template_path, 'w', encoding='utf-8') as f:
        f.writelines(lignes)

    return template_path

def main():
    parser = argparse.ArgumentParser(
        description="Insérer une clause modulaire dans un template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Insérer clause prêt dans template promesse avant la section "PRIX"
  python inserer_clauses.py -t promesse_vente_lots_copropriete.md \\
      -c conditions_suspensives/cs_pret_standard.md \\
      --position avant --marqueur "# PRIX"

  # Insérer clause DPE passoire dans template vente après diagnostics
  python inserer_clauses.py -t vente_lots_copropriete.md \\
      -c diagnostics/dpe_passoire.md \\
      --position apres --marqueur "Diagnostic de performance"

  # Insérer à la ligne 450
  python inserer_clauses.py -t vente_lots_copropriete.md \\
      -c garanties/garantie_eviction.md \\
      --position ligne --ligne 450
        """
    )

    parser.add_argument(
        "-t", "--template",
        required=True,
        help="Nom du fichier template (dans templates/)"
    )

    parser.add_argument(
        "-c", "--clause",
        required=True,
        help="Chemin de la clause (dans clauses/), ex: diagnostics/dpe_passoire.md"
    )

    parser.add_argument(
        "--position",
        choices=['debut', 'fin', 'avant', 'apres', 'ligne'],
        default='fin',
        help="Position d'insertion (défaut: fin)"
    )

    parser.add_argument(
        "--marqueur",
        help="Texte à rechercher (requis pour avant/apres)"
    )

    parser.add_argument(
        "--ligne",
        type=int,
        help="Numéro de ligne (requis pour position=ligne)"
    )

    parser.add_argument(
        "--dry-run",
        action='store_true',
        help="Afficher le résultat sans modifier le fichier"
    )

    args = parser.parse_args()

    # Validation
    if args.position in ['avant', 'apres'] and not args.marqueur:
        parser.error(f"--marqueur requis pour position={args.position}")

    if args.position == 'ligne' and args.ligne is None:
        parser.error("--ligne requis pour position=ligne")

    # Chemins
    template_path = Path('templates') / args.template
    clause_path = Path('clauses') / args.clause

    if not template_path.exists():
        print(f"[ERREUR] Template non trouvé: {template_path}")
        sys.exit(1)

    if not clause_path.exists():
        print(f"[ERREUR] Clause non trouvée: {clause_path}")
        sys.exit(1)

    # Charger clause
    print(f"Chargement de la clause: {clause_path}")
    clause_content = charger_clause(clause_path)
    print(f"  → {len(clause_content)} caractères")

    # Insérer
    if args.dry_run:
        print(f"\n[DRY RUN] Aperçu de l'insertion dans {template_path}:")
        print(f"  Position: {args.position}")
        if args.marqueur:
            print(f"  Marqueur: {args.marqueur}")
        if args.ligne:
            print(f"  Ligne: {args.ligne}")
        print(f"\nContenu à insérer:\n{'-'*80}\n{clause_content}\n{'-'*80}")
    else:
        print(f"\nInsertion dans {template_path}...")
        inserer_dans_template(
            template_path,
            clause_content,
            position=args.position,
            marqueur=args.marqueur,
            offset_lignes=args.ligne or 0
        )
        print(f"[OK] Clause insérée")
        print(f"  Template: {template_path}")

if __name__ == "__main__":
    main()
