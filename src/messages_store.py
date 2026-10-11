from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
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


def _day_window_utc(tz_name: str, target_day: date):
    tz = ZoneInfo(tz_name)
    start_local = datetime.combine(target_day, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def load_posts_for_day(post_timezone: str, target_day: date) -> list[ChannelPost]:
    """Return collected channel posts that fall within one local calendar day."""
    if not MESSAGES_PATH.exists():
        return []

    start_utc, end_utc = _day_window_utc(post_timezone, target_day)

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


def load_yesterdays_posts(post_timezone: str) -> list[ChannelPost]:
    """Compatibility wrapper for callers that need the previous local day."""
    tz = ZoneInfo(post_timezone)
    yesterday = (datetime.now(tz) - timedelta(days=1)).date()
    return load_posts_for_day(post_timezone, yesterday)
