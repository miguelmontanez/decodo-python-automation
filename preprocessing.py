from typing import List

from .models import TextChunk


class TextPreprocessor:
    """Simple chunker that splits text into fixed-size windows."""

    def __init__(self, max_chars: int = 1000, overlap: int = 100) -> None:
        self.max_chars = max_chars
        self.overlap = overlap

    def chunk_text(self, document_id, text: str) -> List[TextChunk]:
        if not text:
            return []
        chunks: List[TextChunk] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + self.max_chars, len(text))
            content = text[start:end]
            chunks.append(
                TextChunk(
                    document_id=document_id,
                    content=content,
                    start_index=start,
                    end_index=end,
                    chunk_index=index,
                    token_count=len(content.split()),
                )
            )
            start = end - self.overlap
            start = max(start, end) if self.overlap >= self.max_chars else start
            index += 1
        return chunks


