#!/usr/bin/env python3
"""
Convert .doc file to Markdown using Windows COM automation.
This gives the best quality extraction as it uses Microsoft Word directly.
"""

import os
import sys
import re

def extract_with_word_com(doc_path, output_path):
    """
    Use Windows COM automation to extract text from .doc file.
    Requires Microsoft Word to be installed.
    """
    try:
        import win32com.client
        from win32com.client import constants
    except ImportError:
        print("ERROR: pywin32 is required. Install with: pip install pywin32")
        return False

    print(f"Opening Word application...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    try:
        print(f"Opening document: {doc_path}")
        doc = word.Documents.Open(doc_path)

        # Get document statistics
        print(f"\nDocument statistics:")
        print(f"  - Pages: {doc.ComputeStatistics(2)}")  # wdStatisticPages = 2
        print(f"  - Words: {doc.ComputeStatistics(0)}")  # wdStatisticWords = 0
        print(f"  - Characters: {doc.ComputeStatistics(3)}")  # wdStatisticCharacters = 3
        print(f"  - Paragraphs: {doc.ComputeStatistics(4)}")  # wdStatisticParagraphs = 4

        # Extract all text
        print("\nExtracting text...")
        text = doc.Range().Text

        # Also try to preserve some structure by getting paragraph-by-paragraph
        paragraphs = []
        for i, para in enumerate(doc.Paragraphs):
            para_text = para.Range.Text.strip()
            if para_text:
                # Get paragraph style for potential markdown formatting
                style_name = para.Style.NameLocal if para.Style else ""
                paragraphs.append({
                    'text': para_text,
                    'style': style_name
                })

        doc.Close(False)

        # Convert to markdown
        md_content = convert_to_markdown(paragraphs, text)

        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\nExtracted {len(md_content)} characters")
        print(f"Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        word.Quit()


def convert_to_markdown(paragraphs, raw_text):
    """
    Convert extracted paragraphs to Markdown format.
    Uses style information when available to format headings.
    """
    md_lines = []

    for para in paragraphs:
        text = para['text'].strip()
        style = para['style'].lower() if para['style'] else ''

        if not text:
            md_lines.append('')
            continue

        # Clean up special characters from Word
        text = text.replace('\r', '')
        text = text.replace('\x07', '')  # Table cell marker
        text = text.replace('\x0b', '\n')  # Vertical tab to newline
        text = text.replace('\x0c', '\n\n')  # Page break

        # Detect headings based on style name
        if 'titre 1' in style or 'heading 1' in style:
            md_lines.append(f"# {text}")
        elif 'titre 2' in style or 'heading 2' in style:
            md_lines.append(f"## {text}")
        elif 'titre 3' in style or 'heading 3' in style:
            md_lines.append(f"### {text}")
        elif 'titre' in style or 'title' in style:
            md_lines.append(f"# {text}")
        else:
            md_lines.append(text)

        md_lines.append('')  # Add blank line after each paragraph

    # Join and clean up
    result = '\n'.join(md_lines)

    # Clean up multiple blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result


def main():
    base_path = r"c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
    doc_path = os.path.join(base_path, "docs_originels", "Trame vente lots de copropriété.doc")
    output_path = os.path.join(base_path, ".tmp", "original_vente_complet.md")

    print("=" * 60)
    print("DOC to Markdown Converter (using Word COM)")
    print("=" * 60)
    print(f"\nSource: {doc_path}")
    print(f"Output: {output_path}")
    print("-" * 60)

    if not os.path.exists(doc_path):
        print(f"ERROR: File not found: {doc_path}")
        sys.exit(1)

    success = extract_with_word_com(doc_path, output_path)

    if success:
        print("\n" + "=" * 60)
        print("Conversion completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Conversion FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
