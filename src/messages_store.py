import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

MESSAGES_PATH = Path(__file__).resolve().parent.parent / "data" / "messages.jsonl"


@dataclass
class ChannelPost:
    message_id: int
    text: str
    date_utc: datetime
    link: str
    has_photo: bool
    photo_file_id: str | None = None


def _yesterday_window_utc(tz_name: str):
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    return yesterday_start.astimezone(timezone.utc), today_start.astimezone(timezone.utc)


def load_yesterdays_posts(post_timezone: str) -> list[ChannelPost]:
    """Return posts collected by bot_collect.py that fall in the previous local day."""
    if not MESSAGES_PATH.exists():
        return []

    start_utc, end_utc = _yesterday_window_utc(post_timezone)

    posts = []
    with open(MESSAGES_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            date_utc = datetime.fromtimestamp(entry["date_utc"], tz=timezone.utc)
            if not (start_utc <= date_utc < end_utc):
                continue
            posts.append(
                ChannelPost(
                    message_id=entry["message_id"],
                    text=entry["text"],
                    date_utc=date_utc,
                    link=entry["link"],
                    has_photo=entry.get("has_photo", False),
                    photo_file_id=entry.get("photo_file_id"),
                )
            )

    return posts
