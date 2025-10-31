import asyncio

import httpx

from .base_loader import BaseLoader
from ..core.config import settings
from ..core.exceptions import DocumentLoadError
from ..models import DocumentType


class WebLoader(BaseLoader):
    def __init__(self) -> None:
        super().__init__()
        self.supported_formats = [DocumentType.URL]

    async def load_single(self, source) -> "Document":
        if not isinstance(source, str) or not source.startswith(("http://", "https://")):
            raise DocumentLoadError(f"Invalid URL: {source}")
        content = await self._fetch_url_content(source)
        title = self._extract_title(source, content)
        return self.create_document(
            title=title,
            content=content,
            source=source,
            doc_type=DocumentType.URL,
            extraction_method="WebLoader.httpx",
        )

    async def _fetch_url_content(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "").lower()
            if "text/html" in content_type:
                return self._extract_html_text(resp.text)
            return resp.text

    def _extract_html_text(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return html
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
        return " ".join(chunk for chunk in chunks if chunk)

    def _extract_title(self, url: str, content: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            t = soup.find("title")
            if t and t.text.strip():
                return t.text.strip()
        except Exception:
            pass
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base = parsed.netloc + parsed.path
            return base or url
        except Exception:
            return url


