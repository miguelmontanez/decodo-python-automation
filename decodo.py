from typing import Any, Dict, List


class DecodoClient:
    """Stub client for web/data discovery.

    Replace with actual crawling/sourcing logic when available.
    """

    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        return [{"title": query, "url": "https://example.com", "snippet": "..."}]

    async def close(self) -> None:
        return None


