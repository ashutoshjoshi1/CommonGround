from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from docx import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".png", ".jpg", ".jpeg"}


def _extract_pdf_text(file_path: Path) -> tuple[str, dict[str, Any]]:
    reader = PdfReader(str(file_path))
    pages = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(f"\n[Page {idx + 1}]\n{text}")
    return "\n".join(pages).strip(), {"page_count": len(reader.pages)}


def _extract_docx_text(file_path: Path) -> tuple[str, dict[str, Any]]:
    doc = Document(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs), {"paragraph_count": len(paragraphs)}


def _extract_csv_text(file_path: Path) -> tuple[str, dict[str, Any]]:
    rows: list[list[str]] = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.reader(handle)
        for row in reader:
            rows.append(row)
    text = "\n".join(", ".join(cell.strip() for cell in row if cell is not None) for row in rows)
    return text, {"row_count": len(rows)}


def _extract_text_file(file_path: Path) -> tuple[str, dict[str, Any]]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return text, {"character_count": len(text)}


def _extract_image_text(file_path: Path) -> tuple[str, dict[str, Any]]:
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text, {"ocr": True, "engine": "tesseract", "ocr_text": text}
    except Exception as exc:  # pragma: no cover
        return "", {"ocr": False, "error": str(exc)}


def parse_content(file_name: str, payload: bytes) -> tuple[str, dict[str, Any]]:
    suffix = Path(file_name).suffix.lower()
    with io.BytesIO(payload) as stream:
        temp = Path("/tmp") / f"commonground-{file_name.replace('/', '_')}"
        temp.write_bytes(stream.read())

    metadata: dict[str, Any] = {"file_name": file_name, "file_extension": suffix}

    if suffix == ".pdf":
        text, extra = _extract_pdf_text(temp)
    elif suffix == ".docx":
        text, extra = _extract_docx_text(temp)
    elif suffix == ".csv":
        text, extra = _extract_csv_text(temp)
    elif suffix in {".txt"}:
        text, extra = _extract_text_file(temp)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        text, extra = _extract_image_text(temp)
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")

    metadata.update(extra)
    metadata["text_length"] = len(text)
    return text, metadata
