from pathlib import Path
from io import BytesIO

from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".txt", ".pdf"}


def extract_text(file_bytes: bytes, filename: str) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Use .txt or .pdf")

    if extension == ".txt":
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        if not text:
            raise ValueError("Text file is empty")
        return text

    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No extractable text found in PDF")
    return text
