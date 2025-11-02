import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from core.config import settings
from core.logging import get_logger
from models import Document, DocumentType


class BaseLoader(ABC):
    def __init__(self) -> None:
        self.logger = get_logger(f"loader.{self.__class__.__name__}")
        self.supported_formats: List[DocumentType] = []

    @abstractmethod
    async def load_single(self, source, **kwargs) -> Document:
        ...

    async def load_multiple(self, sources, max_workers: int | None = None):
        semaphore = asyncio.Semaphore(max_workers or settings.max_parallel_loaders)

        async def run(s):
            async with semaphore:
                return await self.load_single(s)

        tasks = [run(s) for s in sources]
        return await asyncio.gather(*tasks)

    def get_document_type(self, source) -> DocumentType:
        if isinstance(source, str) and source.startswith("http"):
            return DocumentType.URL
        p = Path(source)
        suffix = p.suffix.lower().lstrip(".")
        return DocumentType(suffix)

    def create_document(self, title, content, source, doc_type: DocumentType, **kwargs) -> Document:
        return Document(
            title=title,
            content=content,
            source=str(source),
            doc_type=doc_type,
            word_count=len(content.split()) if content else 0,
            char_count=len(content) if content else 0,
            metadata={**kwargs} if kwargs else {},
        )


