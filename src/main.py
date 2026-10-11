import sys
import os
from datetime import date, datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

from config import Config
from media import download_post_photo
from messages_store import load_posts_for_day
from rss_feed import add_daily_entry
from select_post import select_daily_post
from state import load_last_posted_date, save_last_posted


def main() -> int:
    config = Config()

    tz = ZoneInfo(config.post_timezone)
    requested_date = os.environ.get("TARGET_DATE", "").strip()
    if requested_date:
        try:
            target_day = date.fromisoformat(requested_date)
        except ValueError as exc:
            raise RuntimeError("TARGET_DATE must be a valid YYYY-MM-DD date.") from exc
        if target_day.isoformat() != requested_date:
            raise RuntimeError("TARGET_DATE must use YYYY-MM-DD format.")
    else:
        target_day = (datetime.now(tz) - timedelta(days=1)).date()
    target_date = target_day.isoformat()

    last_posted = load_last_posted_date()
    if last_posted == target_date:
        print(f"Already posted for {target_date}; nothing to do.")
        return 0

    posts = load_posts_for_day(config.post_timezone, target_day)
    if not posts:
        print(f"No collected posts for {target_date}; skipping.")
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

    add_daily_entry(chosen, final_text, target_date, config, image_path=image_path)
    print(f"Added {target_date} entry to docs/feed.xml" + (f" with image {image_path}" if image_path else ""))

    save_last_posted(target_date, chosen.message_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
