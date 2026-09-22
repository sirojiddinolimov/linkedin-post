"""Poll the Telegram Bot API for new @channel posts and append them to
data/messages.jsonl. Run frequently (e.g. every 15 minutes) via GitHub
Actions - plain HTTPS calls to api.telegram.org work fine from cloud IPs,
unlike the MTProto user-session approach this replaced.

The bot must be an administrator of the channel to receive channel_post
updates at all - that's a Telegram Bot API requirement, not a script choice.
"""

import json
import os
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MESSAGES_PATH = DATA_DIR / "messages.jsonl"
OFFSET_PATH = DATA_DIR / "offset.json"


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _load_offset() -> int:
    if not OFFSET_PATH.exists():
        return 0
    return json.loads(OFFSET_PATH.read_text(encoding="utf-8")).get("offset", 0)


def _save_offset(offset: int) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OFFSET_PATH.write_text(json.dumps({"offset": offset}, indent=2) + "\n", encoding="utf-8")


def _load_seen_ids() -> set[int]:
    if not MESSAGES_PATH.exists():
        return set()
    seen = set()
    with open(MESSAGES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                seen.add(json.loads(line)["message_id"])
    return seen


def collect() -> int:
    bot_token = _required("TELEGRAM_BOT_TOKEN")
    channel = os.environ.get("TELEGRAM_CHANNEL", "mutolaaxona").strip().lstrip("@")

    api = f"https://api.telegram.org/bot{bot_token}"

    # Make sure we're in long-polling mode, not webhook mode.
    requests.post(f"{api}/deleteWebhook", timeout=15)

    offset = _load_offset()
    seen_ids = _load_seen_ids()
    new_entries = []
    max_update_id = offset - 1

    while True:
        resp = requests.get(
            f"{api}/getUpdates",
            params={
                "offset": offset,
                "timeout": 0,
                "allowed_updates": json.dumps(["channel_post", "edited_channel_post"]),
            },
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("ok"):
            raise RuntimeError(f"getUpdates failed: {payload}")

        updates = payload["result"]
        if not updates:
            break

        for update in updates:
            max_update_id = max(max_update_id, update["update_id"])
            post = update.get("channel_post") or update.get("edited_channel_post")
            if not post:
                continue
            chat_username = (post.get("chat") or {}).get("username", "")
            if chat_username.lower() != channel.lower():
                continue
            text = (post.get("text") or post.get("caption") or "").strip()
            if not text:
                continue
            message_id = post["message_id"]
            if message_id in seen_ids:
                continue
            seen_ids.add(message_id)
            new_entries.append(
                {
                    "message_id": message_id,
                    "date_utc": post["date"],  # unix timestamp, UTC
                    "text": text,
                    "link": f"https://t.me/{channel}/{message_id}",
                    "has_photo": "photo" in post,
                }
            )

        offset = max_update_id + 1
        if len(updates) < 100:
            break

    if new_entries:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(MESSAGES_PATH, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    _save_offset(offset)
    print(f"Collected {len(new_entries)} new post(s); offset now {offset}.")
    return len(new_entries)


if __name__ == "__main__":
    collect()
