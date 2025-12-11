# src/pdf_reader.py
import pdfplumber
from pathlib import Path


def read_pdf_text(path: str) -> str:
    pdf_path = Path(path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                texts.append(txt)

    # ✅ se não tiver texto, retorna string vazia (SEM OCR)
    return "\n".join(texts)
