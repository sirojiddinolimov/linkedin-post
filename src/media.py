import os
from pathlib import Path

import requests

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"


def download_post_photo(file_id: str, message_id: int) -> str | None:
    """Download a Telegram photo by file_id into docs/images/<message_id>.jpg.
    Returns the published path (e.g. "images/123.jpg") or None on failure/if
    TELEGRAM_BOT_TOKEN isn't set."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not bot_token:
        print("No TELEGRAM_BOT_TOKEN; skipping image download.")
        return None

    api = f"https://api.telegram.org/bot{bot_token}"
    try:
        resp = requests.get(f"{api}/getFile", params={"file_id": file_id}, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("ok"):
            raise RuntimeError(payload)
        file_path = payload["result"]["file_path"]

        file_resp = requests.get(
            f"https://api.telegram.org/file/bot{bot_token}/{file_path}", timeout=30
        )
        file_resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to download post photo ({exc}); continuing without an image.")
        return None

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    published_name = f"{message_id}.jpg"
    (IMAGES_DIR / published_name).write_bytes(file_resp.content)
    return f"images/{published_name}"
