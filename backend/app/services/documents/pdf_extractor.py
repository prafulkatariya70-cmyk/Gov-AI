from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import os

import fitz


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    page_count: int
    method: str


class PDFTextExtractor:
    """Extract native PDF text and fall back to OCR for image-only pages."""

    def __init__(self, *, tesseract_cmd: str | None = None) -> None:
        self.tesseract_cmd = tesseract_cmd or os.getenv("TESSERACT_CMD")

    def extract(self, content: bytes) -> ExtractedDocument:
        document = fitz.open(stream=content, filetype="pdf")
        try:
            native_pages = [page.get_text("text") for page in document]
            native_text = "\n".join(native_pages).strip()
            if native_text:
                return ExtractedDocument(native_text, len(document), "native_pdf_text")

            return self._ocr(document)
        finally:
            document.close()

    def _ocr(self, document) -> ExtractedDocument:
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("OCR dependencies are not installed.") from exc

        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        pages: list[str] = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png")))
            pages.append(pytesseract.image_to_string(image))

        return ExtractedDocument("\n".join(pages).strip(), len(document), "tesseract_ocr")
