import sys
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

from config import Config
from media import download_post_photo
from messages_store import load_yesterdays_posts
from rss_feed import add_daily_entry
from select_post import select_daily_post
from state import load_last_posted_date, save_last_posted


def main() -> int:
    config = Config()

    tz = ZoneInfo(config.post_timezone)
    yesterday = (datetime.now(tz) - timedelta(days=1)).date().isoformat()

    last_posted = load_last_posted_date()
    if last_posted == yesterday:
        print(f"Already posted for {yesterday}; nothing to do.")
        return 0

    posts = load_yesterdays_posts(config.post_timezone)
    if not posts:
        print(f"No collected posts for {yesterday}; skipping.")
        return 0

    chosen, final_text = select_daily_post(posts, config)
    print(f"Selected message {chosen.message_id} ({chosen.link})")
    print("---- RSS item text ----")
    print(final_text)
    print("------------------------")

    if config.dry_run:
        print("DRY_RUN set; not updating the RSS feed.")
        return 0

    image_path = None
    if chosen.has_photo and chosen.photo_file_id:
        image_path = download_post_photo(chosen.photo_file_id, chosen.message_id)

    add_daily_entry(chosen, final_text, yesterday, config, image_path=image_path)
    print(f"Added {yesterday} entry to docs/feed.xml" + (f" with image {image_path}" if image_path else ""))

    save_last_posted(yesterday, chosen.message_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
