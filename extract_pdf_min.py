#!/usr/bin/env python3

"""
import sys
import pdfplumber
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python extract_datasheet.py datasheet.pdf")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
output_path = pdf_path.with_suffix('.md')

with open(output_path, 'w') as f:
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"  ✓ Page {page_num}")
            f.write(f"## Page {page_num}\n\n")
            
            text = page.extract_text()
            if text:
                f.write(text)
                f.write("\n\n")
            
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        f.write("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |\n")
                    f.write("\n")


print(f"Saved to {output_path}")
"""


#!/usr/bin/env python3
import sys
import pdfplumber
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python extract_datasheet.py datasheet.pdf")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
output_path = pdf_path.with_suffix('.md')

def format_table(table):
    """Format table as proper markdown with headers."""
    if not table or len(table) < 2:
        return ""
    
    md = ""
    # Header row
    md += "| " + " | ".join(str(cell).strip() if cell else "" for cell in table[0]) + " |\n"
    # Separator
    md += "|" + "|".join(["---"] * len(table[0])) + "|\n"
    # Data rows
    for row in table[1:]:
        md += "| " + " | ".join(str(cell).strip() if cell else "" for cell in row) + " |\n"
    
    return md

with open(output_path, 'w') as f:
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            f.write(f"## Page {page_num}\n\n")
            
            # Extract text
            text = page.extract_text()
            if text:
                f.write(text)
                f.write("\n\n")
            
            # Extract tables
            tables = page.extract_tables()
            
            if tables:
                f.write("### Tables\n\n")
                for i, table in enumerate(tables, 1):
                    formatted = format_table(table)
                    if formatted:
                        f.write(formatted)
                        f.write("\n")

print(f"Saved to {output_path}")
 