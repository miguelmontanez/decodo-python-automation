import os
from typing import Dict, Any

try:
    from supabase import create_client, Client  # type: ignore
except Exception:  # pragma: no cover
    create_client = None
    Client = None  # type: ignore


def load_remote_config() -> Dict[str, Any]:
    """Load key->json config from Supabase table `app_config`.

    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars.
    Returns empty dict if not configured or client unavailable.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key or create_client is None:
        return {}
    try:
        supabase: Client = create_client(url, key)
        res = supabase.table("app_config").select("key,value").execute()
        rows = res.data or []
        return {row.get("key"): row.get("value") for row in rows if isinstance(row, dict)}
    except Exception:
        return {}


