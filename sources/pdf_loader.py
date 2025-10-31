import asyncio
from pathlib import Path

from .base_loader import BaseLoader
from ..core.exceptions import DocumentLoadError
from ..models import DocumentType


class PDFLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        self.supported_formats = [DocumentType.PDF]

    async def load_single(self, source) -> "Document":
        p = Path(source)
        if not p.exists():
            raise DocumentLoadError(f"File not found: {source}")
        content = await self._extract_pdf_text(p)
        return self.create_document(
            title=p.stem,
            content=content,
            source=str(p),
            doc_type=DocumentType.PDF,
            extraction_method="PDFLoader.pymupdf",
        )

    async def _extract_pdf_text(self, path: Path) -> str:
        def _extract() -> str:
            try:
                import fitz  # PyMuPDF
            except ImportError as e:
                raise DocumentLoadError(
                    "PyMuPDF package required for PDF files. Install: pip install PyMuPDF"
                ) from e
            doc = fitz.open(path)
            parts: list[str] = []
            try:
                for i in range(doc.page_count):
                    page = doc[i]
                    text = page.get_text()
                    if text.strip():
                        parts.append(f"Page {i+1}:\n{text}")
            finally:
                doc.close()
            return "\n\n".join(parts)

        return await asyncio.to_thread(_extract)


