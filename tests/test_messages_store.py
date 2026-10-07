import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch

from src import messages_store


class LoadPostsForDayTests(unittest.TestCase):
    def test_uses_the_requested_local_calendar_day(self) -> None:
        entries = [
            (1, datetime(2026, 9, 24, 18, 59, tzinfo=timezone.utc)),
            (2, datetime(2026, 9, 24, 19, 0, tzinfo=timezone.utc)),
            (3, datetime(2026, 9, 25, 4, 33, tzinfo=timezone.utc)),
            (4, datetime(2026, 9, 25, 19, 0, tzinfo=timezone.utc)),
        ]
        rows = [
            {
                "message_id": message_id,
                "date_utc": int(timestamp.timestamp()),
                "text": f"post {message_id}",
                "link": f"https://t.me/mutolaaxona/{message_id}",
            }
            for message_id, timestamp in entries
        ]

        with tempfile.TemporaryDirectory() as directory:
            messages_path = Path(directory) / "messages.jsonl"
            messages_path.write_text(
                "\n".join(json.dumps(row) for row in rows), encoding="utf-8"
            )
            with patch.object(messages_store, "MESSAGES_PATH", messages_path):
                posts = messages_store.load_posts_for_day(
                    "Asia/Tashkent", date(2026, 9, 25)
                )

        self.assertEqual([2, 3], [post.message_id for post in posts])


if __name__ == "__main__":
    unittest.main()
