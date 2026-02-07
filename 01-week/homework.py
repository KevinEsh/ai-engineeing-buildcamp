# Convert all the downloaded PDFs to markdown files and save them to a books_text/ directory using markitdown
import subprocess
from pathlib import Path

pdf_dir = Path("01-week/data/books/pdfs")
md_dir = Path("01-week/data/books/markdown")
md_dir.mkdir(parents=True, exist_ok=True)
print("hello")
for pdf_file in pdf_dir.glob("*.pdf"):
    output_file = md_dir / f"{pdf_file.stem}.md"
    cmd = f'uv run markitdown "{pdf_file}" > "{output_file}"'
    subprocess.run(cmd, shell=True)
    print(f"✓ {pdf_file.name} → {output_file.name}")
