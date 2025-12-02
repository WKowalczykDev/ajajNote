import subprocess
from pathlib import Path


def convert_markdown_file_to_pdf(input_md_path: str, output_pdf_path: str,
                                 pdf_engine: str = "wkhtmltopdf"):

    input_md_path = Path(input_md_path)
    output_pdf_path = Path(output_pdf_path)

    if not input_md_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku {input_md_path}")

    cmd = [
        "pandoc",
        str(input_md_path),
        "-o", str(output_pdf_path),
        "--pdf-engine", pdf_engine,
        "-V", "margin-top=2cm",
        "-V", "margin-bottom=2cm",
        "-V", "margin-left=2cm",
        "-V", "margin-right=2cm",
        "--highlight-style", "tango"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"PDF zapisany jako {output_pdf_path}")
    except subprocess.CalledProcessError as e:
        print("Błąd podczas konwersji Markdown → PDF")
        raise e

convert_markdown_file_to_pdf("./OUTPUT/md/spotkanie_wrss_01_12.md","./OUTPUT/pdf/spotkanie_wrss_01_12.pdf")