from dataclasses import dataclass
import io
import os
import shutil

import pymupdf
import pytesseract
from PIL import Image
from pypdf import PdfReader


@dataclass
class DocumentText:
    """
    Result of extracting text from a PDF document.
    """

    success: bool

    page_count: int = 0

    text: str = ""

    extraction_method: str | None = None

    error: str | None = None


class PDFTextExtractor:
    """
    Extract text from PDF documents.

    Strategy:

    1. Try embedded PDF text with pypdf.
    2. If no usable text exists, fall back to OCR.
    """

    def __init__(
        self,
        ocr_language: str = "eng",
        ocr_dpi: int = 200,
    ) -> None:

        self.ocr_language = ocr_language
        self.ocr_dpi = ocr_dpi

        self._configure_tesseract()

    @staticmethod
    def _configure_tesseract() -> None:
        """
        Automatically locate Tesseract OCR.

        Priority:

        1. Tesseract already available on PATH.
        2. Standard Windows installation locations.
        3. Common local installation locations.

        Raises RuntimeError if Tesseract cannot be found.
        """

        # ---------------------------------------------------------
        # 1. Check whether Tesseract is already available on PATH.
        # ---------------------------------------------------------

        tesseract_path = shutil.which(
            "tesseract"
        )

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = (
                tesseract_path
            )
            return

        # ---------------------------------------------------------
        # 2. Check standard Windows installation locations.
        # ---------------------------------------------------------

        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"
            ),
        ]

        for path in windows_paths:

            if os.path.isfile(path):

                pytesseract.pytesseract.tesseract_cmd = (
                    path
                )

                return

        # ---------------------------------------------------------
        # 3. Tesseract could not be located.
        # ---------------------------------------------------------

        raise RuntimeError(
            "Tesseract OCR was not found. "
            "Install Tesseract OCR or add tesseract.exe "
            "to the system PATH."
        )

    def extract(
        self,
        content: bytes,
    ) -> DocumentText:
        """
        Extract text from PDF bytes.
        """

        if not content:
            return DocumentText(
                success=False,
                error="PDF content is empty.",
            )

        embedded_result = (
            self._extract_with_pypdf(
                content
            )
        )

        if embedded_result.success:
            return embedded_result

        ocr_result = self._extract_with_ocr(
            content
        )

        if ocr_result.success:
            return ocr_result

        return DocumentText(
            success=False,
            page_count=max(
                embedded_result.page_count,
                ocr_result.page_count,
            ),
            text="",
            extraction_method=None,
            error=(
                "Embedded text extraction failed "
                "and OCR extraction also failed. "
                f"Embedded error: "
                f"{embedded_result.error}. "
                f"OCR error: "
                f"{ocr_result.error}"
            ),
        )

    def _extract_with_pypdf(
        self,
        content: bytes,
    ) -> DocumentText:
        """
        Try extracting an embedded text layer.
        """

        try:
            reader = PdfReader(
                io.BytesIO(content)
            )

            page_count = len(
                reader.pages
            )

            pages: list[str] = []

            for page in reader.pages:

                text = page.extract_text()

                if text and text.strip():
                    pages.append(
                        text.strip()
                    )

            full_text = "\n\n".join(
                pages
            ).strip()

            if not full_text:
                return DocumentText(
                    success=False,
                    page_count=page_count,
                    text="",
                    extraction_method=None,
                    error=(
                        "No embedded text was "
                        "found in the PDF."
                    ),
                )

            return DocumentText(
                success=True,
                page_count=page_count,
                text=full_text,
                extraction_method="pypdf",
                error=None,
            )

        except Exception as exc:

            return DocumentText(
                success=False,
                page_count=0,
                text="",
                extraction_method=None,
                error=str(exc),
            )

    def _extract_with_ocr(
        self,
        content: bytes,
    ) -> DocumentText:
        """
        Render PDF pages to images and extract
        text using Tesseract OCR.
        """

        document = None

        try:
            document = pymupdf.open(
                stream=content,
                filetype="pdf",
            )

            page_count = len(
                document
            )

            pages: list[str] = []

            zoom = (
                self.ocr_dpi / 72.0
            )

            matrix = pymupdf.Matrix(
                zoom,
                zoom,
            )

            for page_number, page in enumerate(
                document,
                start=1,
            ):

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                )

                image_bytes = (
                    pixmap.tobytes(
                        "png"
                    )
                )

                image = Image.open(
                    io.BytesIO(
                        image_bytes
                    )
                )

                text = pytesseract.image_to_string(
                    image,
                    lang=self.ocr_language,
                )

                text = text.strip()

                if text:
                    pages.append(
                        f"[Page {page_number}]\n"
                        f"{text}"
                    )

            full_text = "\n\n".join(
                pages
            ).strip()

            if not full_text:
                return DocumentText(
                    success=False,
                    page_count=page_count,
                    text="",
                    extraction_method=None,
                    error=(
                        "OCR completed but "
                        "no text was detected."
                    ),
                )

            return DocumentText(
                success=True,
                page_count=page_count,
                text=full_text,
                extraction_method="tesseract_ocr",
                error=None,
            )

        except Exception as exc:

            return DocumentText(
                success=False,
                page_count=(
                    len(document)
                    if document is not None
                    else 0
                ),
                text="",
                extraction_method=None,
                error=str(exc),
            )

        finally:

            if document is not None:
                document.close()