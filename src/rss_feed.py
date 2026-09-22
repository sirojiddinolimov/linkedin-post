import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from typing import TYPE_CHECKING
from xml.sax.saxutils import escape

from config import Config

if TYPE_CHECKING:
    from telegram_fetch import ChannelPost

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
HISTORY_PATH = os.path.join(DOCS_DIR, "history.json")
FEED_PATH = os.path.join(DOCS_DIR, "feed.xml")


def _load_history() -> list[dict]:
    if not os.path.exists(HISTORY_PATH):
        return []
    with open(HISTORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_history(entries: list[dict]) -> None:
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _render_feed(entries: list[dict], config: Config) -> str:
    channel_link = config.feed_base_url
    items_xml = []
    for entry in entries:
        pub_date = format_datetime(datetime.fromisoformat(entry["published_at"]))
        title = escape(entry["title"])
        description = escape(entry["text"])
        link = escape(entry["source_link"])
        guid = escape(entry["guid"])
        items_xml.append(
            "    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <guid isPermaLink=\"false\">{guid}</guid>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"      <description>{description}</description>\n"
            "    </item>"
        )

    now = format_datetime(datetime.now(timezone.utc))
    body = "\n".join(items_xml)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{escape(config.feed_title)}</title>\n"
        f"    <link>{escape(channel_link)}</link>\n"
        "    <description>@" + escape(config.telegram_channel)
        + " kanalidagi har kunning eng muhim posti</description>\n"
        "    <language>uz</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        f"{body}\n"
        "  </channel>\n"
        "</rss>\n"
    )


def add_daily_entry(post: "ChannelPost", final_text: str, entry_date: str, config: Config) -> None:
    """Append today's chosen post to docs/history.json and regenerate docs/feed.xml
    (the RSS feed LinkedIn's Page "Add source" feature reads from)."""
    entries = _load_history()

    title_line = final_text.strip().splitlines()[0][:120]
    entry = {
        "date": entry_date,
        "telegram_message_id": post.message_id,
        "source_link": post.link,
        "title": title_line,
        "text": final_text.strip(),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "guid": f"mutolaa-linkedin-{entry_date}-{post.message_id}",
    }

    entries = [e for e in entries if e["date"] != entry_date]
    entries.append(entry)
    entries.sort(key=lambda e: e["date"], reverse=True)
    entries = entries[: config.feed_max_items]

    _save_history(entries)

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(_render_feed(entries, config))
