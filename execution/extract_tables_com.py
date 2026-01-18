"""
Extract all tables from the original Word document using COM automation.
This script opens the .doc file with Word COM and extracts table metadata and content.
"""

import win32com.client
import json
import os
import sys

def extract_tables_from_doc(doc_path, output_path):
    """
    Extract all tables from a Word document using COM automation.

    Args:
        doc_path: Path to the Word document
        output_path: Path to save the JSON output
    """
    # Initialize Word application
    word = None
    doc = None

    try:
        print(f"Opening Word application...")
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False  # Run in background

        # Convert path to absolute path
        doc_path = os.path.abspath(doc_path)
        print(f"Opening document: {doc_path}")

        # Open the document
        doc = word.Documents.Open(doc_path, ReadOnly=True)

        # Get number of tables
        num_tables = doc.Tables.Count
        print(f"Found {num_tables} tables in the document")

        tables_data = []

        # Iterate through all tables (1-indexed in COM)
        for i in range(1, num_tables + 1):
            print(f"Processing table {i}/{num_tables}...")
            table = doc.Tables(i)

            # Get table dimensions
            num_rows = table.Rows.Count
            num_cols = table.Columns.Count

            table_info = {
                "table_index": i,
                "num_rows": num_rows,
                "num_cols": num_cols,
                "header_row": [],
                "first_data_row": [],
                "all_content": []
            }

            # Extract all cell content
            try:
                for row_idx in range(1, min(num_rows + 1, 6)):  # Limit to first 5 rows for sample
                    row_content = []
                    for col_idx in range(1, num_cols + 1):
                        try:
                            cell = table.Cell(row_idx, col_idx)
                            # Get cell text, remove end-of-cell marker (ASCII 7 and 13)
                            cell_text = cell.Range.Text.strip()
                            cell_text = cell_text.replace('\r\x07', '').replace('\x07', '').replace('\r', ' ').strip()
                            row_content.append(cell_text)
                        except Exception as cell_error:
                            # Handle merged cells or other issues
                            row_content.append(f"[Error: {str(cell_error)[:50]}]")

                    if row_idx == 1:
                        table_info["header_row"] = row_content
                    elif row_idx == 2:
                        table_info["first_data_row"] = row_content

                    table_info["all_content"].append(row_content)

            except Exception as row_error:
                print(f"  Warning: Error reading table {i} rows: {row_error}")

            # Try to get table position context
            try:
                # Get text before the table (context)
                table_range = table.Range
                start_pos = max(0, table_range.Start - 200)
                context_range = doc.Range(start_pos, table_range.Start)
                context_text = context_range.Text.strip()[-100:] if context_range.Text else ""
                table_info["context_before"] = context_text.replace('\r', ' ').replace('\x07', '')
            except:
                table_info["context_before"] = ""

            tables_data.append(table_info)
            print(f"  Table {i}: {num_rows} rows x {num_cols} cols")

        # Save to JSON
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "document_path": doc_path,
                "total_tables": num_tables,
                "tables": tables_data
            }, f, ensure_ascii=False, indent=2)

        print(f"\nExtracted {num_tables} tables to: {output_path}")
        return tables_data

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        # Clean up
        if doc:
            try:
                doc.Close(False)
            except:
                pass
        if word:
            try:
                word.Quit()
            except:
                pass


if __name__ == "__main__":
    # Default paths
    base_dir = r"c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
    doc_path = os.path.join(base_dir, "docs_originels", "Trame vente lots de copropriété.doc")
    output_path = os.path.join(base_dir, ".tmp", "tables_original.json")

    # Allow command line override
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    extract_tables_from_doc(doc_path, output_path)
