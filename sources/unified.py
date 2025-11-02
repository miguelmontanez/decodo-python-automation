import asyncio
from pathlib import Path
from typing import List

from base_loader import BaseLoader
from document_loader import DocumentLoader
from pdf_loader import PDFLoader
from web_loader import WebLoader
from core.config import settings
from core.exceptions import DocumentLoadError
from core.logging import LogContext, get_logger
from models import Document, DocumentType


class UnifiedLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger("loader.unified")
        self.document_loader = DocumentLoader()
        self.pdf_loader = PDFLoader()
        self.web_loader = WebLoader()
        self.supported_formats = list(DocumentType)

    def _select_loader(self, source) -> BaseLoader | None:
        if isinstance(source, str) and source.startswith(("http://", "https://")):
            return self.web_loader
        p = Path(source)
        if not p.exists():
            return None
        suffix = p.suffix.lower().lstrip(".")
        doc_type = DocumentType(suffix)
        if doc_type == DocumentType.PDF:
            return self.pdf_loader
        if doc_type in [DocumentType.TXT, DocumentType.MD, DocumentType.HTML, DocumentType.JSON, DocumentType.CSV, DocumentType.DOCX]:
            return self.document_loader
        return None

    async def load_single(self, source, **kwargs) -> Document:
        loader = self._select_loader(source)
        if not loader:
            raise DocumentLoadError(f"Unsupported or missing source: {source}")
        with LogContext("unified_load_single", source=str(source)):
            return await loader.load_single(source, **kwargs)

    async def load_directory(self, directory: str | Path, recursive: bool = True) -> List[Document]:
        directory = Path(directory)
        if not directory.exists():
            raise DocumentLoadError(f"Directory not found: {directory}")
        sources: list[Path] = self._find_supported_files(directory, recursive=recursive)
        semaphore = asyncio.Semaphore(settings.max_parallel_loaders)

        async def run(src: Path):
            async with semaphore:
                try:
                    return await self.load_single(src)
                except Exception as e:
                    self.logger.error(f"Failed to load: {src} | {e}")
                    return e

        tasks = [run(s) for s in sources]
        results = await asyncio.gather(*tasks)
        documents: List[Document] = [r for r in results if isinstance(r, Document)]
        return documents

    def _find_supported_files(self, directory: Path, recursive: bool = True) -> list[Path]:
        patterns = ["*.pdf", "*.txt", "*.md", "*.html", "*.docx", "*.json", "*.csv"]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(directory.rglob(pattern) if recursive else directory.glob(pattern))
        return sorted(files)


