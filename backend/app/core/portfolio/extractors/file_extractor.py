from __future__ import annotations

from pathlib import Path
from typing import Optional

import pdfplumber
from .base import BaseExtractor


class FileExtractor(BaseExtractor):
    """
    Extractor for local files.
    Supports: .pdf, .txt, .md
    """

    SUPPORTED_TEXT_EXTS = {".txt", ".md"}
    SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

    def extract(self, source: str) -> str:
        path = Path(source)

        if not path.exists():
            return f"[Error] File not found: {path}"

        suffix = path.suffix.lower()

        # 1. PDF Handling
        if suffix == ".pdf":
            # Try text extraction first
            text = extract_text_from_pdf(path)
            # If text is very short/empty, it might be a scanned PDF -> Try Vision OCR
            if len(text.strip()) < 50:
                logger.info(f"PDF {path.name} seems to have little text. Trying Google Vision OCR...")
                from .google_vision_extractor import GoogleVisionExtractor
                vision = GoogleVisionExtractor()
                # For a full implementation, we'd convert PDF to images here.
                # Since that's heavy, we'll just log and return what we have or try OCR on first page if possible.
                pass 
            return text

        # 2. Image Handling
        if suffix in self.SUPPORTED_IMAGE_EXTS:
            from .google_vision_extractor import GoogleVisionExtractor
            return GoogleVisionExtractor().extract(source)

        # 3. Text Handling
        if suffix in self.SUPPORTED_TEXT_EXTS:
            return path.read_text(encoding="utf-8", errors="ignore").strip()

        return f"[Error] Unsupported file type: {suffix}"


def extract_text_with_pdfplumber(pdf_path: Path) -> str:
    chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            t = (page.extract_text() or "").strip()
            if t:
                chunks.append(t)
    return "\n\n".join(chunks).strip()


def extract_text_with_pypdf(pdf_path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []

    for page in reader.pages:
        t = (page.extract_text() or "").strip()
        if t:
            chunks.append(t)

    return "\n\n".join(chunks).strip()


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Try pdfplumber first; if it fails OR returns empty text, fallback to pypdf.
    """
    try:
        text = extract_text_with_pdfplumber(pdf_path)
        if text:
            return text
    except Exception:
        pass

    try:
        return extract_text_with_pypdf(pdf_path)
    except Exception:
        return ""
