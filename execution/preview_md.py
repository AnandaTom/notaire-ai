#!/usr/bin/env python3
"""Preview the markdown file content."""

import os
import sys

base_path = r"c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
path = os.path.join(base_path, ".tmp", "original_vente_complet.md")
preview_path = os.path.join(base_path, ".tmp", "preview.txt")

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

preview = []
preview.append(f'Total length: {len(content)} characters')
preview.append(f'Total lines: {len(content.splitlines())}')
preview.append('\n--- FIRST 3000 CHARACTERS ---')
preview.append(content[:3000])
preview.append('\n--- CHARACTERS 50000-53000 (middle) ---')
preview.append(content[50000:53000])
preview.append('\n--- LAST 2000 CHARACTERS ---')
preview.append(content[-2000:])

with open(preview_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(preview))

print(f"Preview saved to: {preview_path}")
print(f"Total length: {len(content)} characters")
print(f"Total lines: {len(content.splitlines())}")
