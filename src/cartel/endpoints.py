"""Endpoint helpers with no harness imports (safe in the root env)."""

from pathlib import Path


def modal_endpoint(url: str, key_file: str = "~/.cartel_modal_key") -> dict:
    """Endpoint dict for a scripts/modal_serve.py deployment; the key is read from a file, never printed."""
    base = url.rstrip("/")
    return {"base_url": base if base.endswith("/v1") else base + "/v1",
            "api_key": Path(key_file).expanduser().read_text().strip()}
