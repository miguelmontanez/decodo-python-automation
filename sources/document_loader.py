import asyncio
import csv
import json
from pathlib import Path

from .base_loader import BaseLoader
from ..core.config import settings
from ..core.exceptions import DocumentLoadError
from ..models import Document, DocumentType


class DocumentLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        self.supported_formats = [
            DocumentType.TXT,
            DocumentType.MD,
            DocumentType.HTML,
            DocumentType.JSON,
            DocumentType.CSV,
            DocumentType.DOCX,
        ]

    async def load_single(self, source, encoding: str | None = None) -> Document:
        encoding = encoding or settings.default_encoding
        doc_type = self.get_document_type(source)
        p = Path(source)
        if not p.exists():
            raise DocumentLoadError(f"File not found: {source}")

        if doc_type == DocumentType.TXT:
            content = await asyncio.to_thread(p.read_text, encoding=encoding)
        elif doc_type == DocumentType.MD:
            content = await asyncio.to_thread(p.read_text, encoding=encoding)
        elif doc_type == DocumentType.HTML:
            content = await self._load_html(p, encoding)
        elif doc_type == DocumentType.JSON:
            content = await self._load_json(p, encoding)
        elif doc_type == DocumentType.CSV:
            content = await self._load_csv(p, encoding)
        elif doc_type == DocumentType.DOCX:
            content = await self._load_docx(p)
        else:
            raise DocumentLoadError(f"Unsupported document type: {doc_type}")

        return self.create_document(
            title=p.stem,
            content=content,
            source=str(p),
            doc_type=doc_type,
        )

    async def _load_html(self, path: Path, encoding: str) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return await asyncio.to_thread(path.read_text, encoding=encoding)

        with open(path, "r", encoding=encoding) as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
        return " ".join(chunk for chunk in chunks if chunk)

    async def _load_json(self, path: Path, encoding: str) -> str:
        with open(path, "r", encoding=encoding) as f:
            data = json.load(f)
        if isinstance(data, dict):
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        if isinstance(data, list):
            return "\n".join(f"Item {i+1}: {item}" for i, item in enumerate(data))
        return str(data)

    async def _load_csv(self, path: Path, encoding: str) -> str:
        lines: list[str] = []
        with open(path, "r", encoding=encoding, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers:
                lines.append("Headers: " + ", ".join(headers))
                lines.append("")
            for row_num, row in enumerate(reader, 1):
                if headers and len(row) == len(headers):
                    row_data = [f"{h}: {v}" for h, v in zip(headers, row)]
                    lines.append(f"Row {row_num}: {' | '.join(row_data)}")
                else:
                    lines.append(", ".join(row))
        return "\n".join(lines)

    async def _load_docx(self, path: Path) -> str:
        try:
            from docx import Document as Docx
        except ImportError as e:
            raise DocumentLoadError("python-docx package required for DOCX files") from e
        doc = Docx(path)
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(parts)


