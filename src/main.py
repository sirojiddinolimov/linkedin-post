import sys
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

from config import Config
from linkedin_publish import publish_post
from select_post import select_daily_post
from state import load_last_posted_date, save_last_posted
from telegram_fetch import fetch_yesterdays_posts


def main() -> int:
    config = Config()

    tz = ZoneInfo(config.post_timezone)
    yesterday = (datetime.now(tz) - timedelta(days=1)).date().isoformat()

    last_posted = load_last_posted_date()
    if last_posted == yesterday:
        print(f"Already posted for {yesterday}; nothing to do.")
        return 0

    posts = fetch_yesterdays_posts(config)
    if not posts:
        print(f"No posts found in @{config.telegram_channel} for {yesterday}; skipping.")
        return 0

    chosen, final_text = select_daily_post(posts, config)
    print(f"Selected message {chosen.message_id} ({chosen.link})")
    print("---- LinkedIn post text ----")
    print(final_text)
    print("-----------------------------")

    if config.dry_run:
        print("DRY_RUN set; not publishing to LinkedIn.")
        return 0

    post_urn = publish_post(final_text, config)
    print(f"Published to LinkedIn: {post_urn}")

    save_last_posted(yesterday, chosen.message_id, post_urn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
