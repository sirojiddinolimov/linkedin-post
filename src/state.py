import json
import os

STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state", "last_post.json")


def load_last_posted_date() -> str | None:
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f).get("date")


def save_last_posted(date_str: str, telegram_message_id: int, linkedin_post_urn: str) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "date": date_str,
                "telegram_message_id": telegram_message_id,
                "linkedin_post_urn": linkedin_post_urn,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")
