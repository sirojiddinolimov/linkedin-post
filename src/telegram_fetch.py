from dataclasses import dataclass
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

from config import Config


@dataclass
class ChannelPost:
    message_id: int
    text: str
    date_utc: datetime
    views: int
    forwards: int
    reactions: int
    link: str
    has_photo: bool


def _yesterday_window(tz_name: str):
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    return yesterday_start, today_start


def fetch_yesterdays_posts(config: Config) -> list[ChannelPost]:
    """Return every text-bearing post from the channel for the previous local day."""
    start_local, end_local = _yesterday_window(config.post_timezone)
    start_utc = start_local.astimezone(ZoneInfo("UTC"))
    end_utc = end_local.astimezone(ZoneInfo("UTC"))

    client = TelegramClient(
        StringSession(config.telegram_session_string),
        config.telegram_api_id,
        config.telegram_api_hash,
        proxy=config.telegram_proxy(),
        connection_retries=3,
        timeout=15,
    )

    posts: list[ChannelPost] = []
    with client:
        print(f"Connected to Telegram; resolving @{config.telegram_channel}...", flush=True)
        entity = client.get_entity(config.telegram_channel)
        print("Resolved channel; fetching messages...", flush=True)
        for message in client.iter_messages(entity, offset_date=end_utc, reverse=False):
            if message.date is None:
                continue
            if message.date >= end_utc:
                continue
            if message.date < start_utc:
                break
            text = (message.message or "").strip()
            if not text:
                continue

            reactions = 0
            if message.reactions and message.reactions.results:
                reactions = sum(r.count for r in message.reactions.results)

            posts.append(
                ChannelPost(
                    message_id=message.id,
                    text=text,
                    date_utc=message.date,
                    views=message.views or 0,
                    forwards=message.forwards or 0,
                    reactions=reactions,
                    link=f"https://t.me/{config.telegram_channel}/{message.id}",
                    has_photo=isinstance(message.media, MessageMediaPhoto),
                )
            )

    return posts
