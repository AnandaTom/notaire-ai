#!/usr/bin/env python3
"""Verify the output markdown file."""

import os

base_path = r"c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
path = os.path.join(base_path, ".tmp", "original_vente_complet.md")

if os.path.exists(path):
    size = os.path.getsize(path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.splitlines()

    print(f'File exists: Yes')
    print(f'File path: {path}')
    print(f'File size: {size:,} bytes')
    print(f'Character count: {len(content):,}')
    print(f'Line count: {len(lines):,}')
    print(f'Word count (approx): {len(content.split()):,}')

    # Count headings
    h1_count = len([l for l in lines if l.startswith('# ') and not l.startswith('## ')])
    h2_count = len([l for l in lines if l.startswith('## ') and not l.startswith('### ')])
    h3_count = len([l for l in lines if l.startswith('### ')])

    print(f'\nMarkdown structure:')
    print(f'  - H1 headings (#): {h1_count}')
    print(f'  - H2 headings (##): {h2_count}')
    print(f'  - H3 headings (###): {h3_count}')
else:
    print('File does not exist')
