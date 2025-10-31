import os
from pathlib import Path
from typing import Optional

from .models import Dataset, ExportFormat


class DatasetExporter:
    async def export(self, dataset: Dataset, output_path: str | Path, format: ExportFormat = ExportFormat.JSONL) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if format == ExportFormat.JSONL:
            lines = dataset.to_jsonl()
            output_path.write_text("\n".join(lines), encoding="utf-8")
        elif format == ExportFormat.JSON:
            # simple wrapper using JSONL content
            output_path.write_text("[\n" + ",\n".join(dataset.to_jsonl()) + "\n]", encoding="utf-8")
        else:
            raise ValueError(f"Unsupported export format: {format}")
        return output_path


class DatabaseManager:
    async def close(self) -> None:
        return None


def upload_to_supabase(file_path: Path) -> Optional[str]:
    """Upload a file to Supabase Storage if configured.

    Env vars required:
      - SUPABASE_URL
      - SUPABASE_SERVICE_ROLE_KEY
      - SUPABASE_STORAGE_BUCKET
    Returns a public URL (if bucket is public) or a signed URL, or None on failure.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET")
    if not url or not key or not bucket:
        return None
    try:
        from supabase import create_client  # type: ignore
        client = create_client(url, key)
        storage_path = file_path.name
        with open(file_path, "rb") as f:
            client.storage.from_(bucket).upload(storage_path, f.read())
        # Try to create public URL; if bucket is not public, create a signed URL
        try:
            public = client.storage.from_(bucket).get_public_url(storage_path)
            if public and isinstance(public, str):
                return public
            if isinstance(public, dict) and public.get("publicURL"):
                return public["publicURL"]
        except Exception:
            pass
        try:
            signed = client.storage.from_(bucket).create_signed_url(storage_path, 60 * 60 * 24)
            if isinstance(signed, str):
                return signed
            if isinstance(signed, dict) and signed.get("signedURL"):
                return signed["signedURL"]
        except Exception:
            pass
        return None
    except Exception:
        return None


