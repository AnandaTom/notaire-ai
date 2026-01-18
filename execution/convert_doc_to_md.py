#!/usr/bin/env python3
"""
Convert .doc (Office 97-2003) file to Markdown.
Uses olefile to extract text from binary .doc format.
"""

import sys
import os
import struct
import re

def extract_text_from_doc(doc_path):
    """
    Extract text from a .doc file using olefile.
    The .doc format stores text in the WordDocument stream.
    """
    import olefile

    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"File not found: {doc_path}")

    ole = olefile.OleFileIO(doc_path)

    # List all streams for debugging
    print("Available streams in the .doc file:")
    for stream in ole.listdir():
        print(f"  - {'/'.join(stream)}")

    # Read the WordDocument stream
    if ole.exists('WordDocument'):
        word_stream = ole.openstream('WordDocument').read()
        print(f"\nWordDocument stream size: {len(word_stream)} bytes")
    else:
        raise ValueError("No WordDocument stream found")

    # Try to read the main text from the document
    # For complex .doc files, we need to parse the FIB (File Information Block)
    # and then extract text from the appropriate location

    # Try to get text from 1Table or 0Table stream (contains formatting info)
    table_stream = None
    if ole.exists('1Table'):
        table_stream = ole.openstream('1Table').read()
        print(f"1Table stream size: {len(table_stream)} bytes")
    elif ole.exists('0Table'):
        table_stream = ole.openstream('0Table').read()
        print(f"0Table stream size: {len(table_stream)} bytes")

    ole.close()

    # Extract text using a simpler approach - look for readable text
    # in the WordDocument stream
    text = extract_text_simple(word_stream)

    return text


def extract_text_simple(data):
    """
    Simple text extraction from Word document binary data.
    Tries to extract readable text by looking for text runs.
    """
    # Word .doc files can contain text in different encodings
    # Try UTF-16LE first (common for .doc files)
    text_parts = []

    # Look for text patterns - .doc files often have text in specific sections
    # Try to decode as UTF-16LE
    try:
        # Skip the first few bytes (header) and try to find text
        decoded = data.decode('utf-16le', errors='ignore')
        # Filter out non-printable characters but keep French accents
        cleaned = ''.join(c if c.isprintable() or c in '\n\r\t' else '' for c in decoded)
        if len(cleaned) > 100:
            text_parts.append(cleaned)
    except:
        pass

    # Also try CP1252 (Windows Western European)
    try:
        decoded = data.decode('cp1252', errors='ignore')
        cleaned = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in decoded)
        if len(cleaned) > len(''.join(text_parts)):
            text_parts = [cleaned]
    except:
        pass

    return '\n'.join(text_parts)


def extract_with_antiword_method(doc_path):
    """
    Alternative method: Use Windows COM automation if available.
    """
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False

        doc = word.Documents.Open(doc_path)
        text = doc.Range().Text
        doc.Close(False)
        word.Quit()

        return text
    except ImportError:
        print("win32com not available, trying alternative methods...")
        return None
    except Exception as e:
        print(f"COM automation failed: {e}")
        return None


def convert_to_markdown(text):
    """
    Convert extracted text to basic Markdown format.
    Preserves structure as much as possible.
    """
    lines = text.split('\n')
    md_lines = []

    for line in lines:
        line = line.strip()
        if line:
            md_lines.append(line)
        else:
            md_lines.append('')

    # Join and clean up multiple empty lines
    result = '\n'.join(md_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result


def main():
    base_path = r"c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
    doc_path = os.path.join(base_path, "docs_originels", "Trame vente lots de copropriété.doc")
    output_path = os.path.join(base_path, ".tmp", "original_vente_complet.md")

    print(f"Converting: {doc_path}")
    print(f"Output: {output_path}")
    print("-" * 50)

    # Try COM automation first (best quality on Windows)
    text = extract_with_antiword_method(doc_path)

    if not text or len(text) < 1000:
        print("\nTrying olefile extraction...")
        text = extract_text_from_doc(doc_path)

    if text:
        # Convert to Markdown
        md_content = convert_to_markdown(text)

        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"\nExtracted {len(md_content)} characters")
        print(f"Saved to: {output_path}")

        # Show first 2000 characters as preview
        print("\n" + "=" * 50)
        print("PREVIEW (first 2000 chars):")
        print("=" * 50)
        print(md_content[:2000])
    else:
        print("Failed to extract text from the document")
        sys.exit(1)


if __name__ == "__main__":
    main()
