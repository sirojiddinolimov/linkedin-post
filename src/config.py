import os


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class Config:
    def __init__(self) -> None:
        self.telegram_api_id = int(_required("TELEGRAM_API_ID"))
        self.telegram_api_hash = _required("TELEGRAM_API_HASH")
        self.telegram_session_string = _required("TELEGRAM_SESSION_STRING")
        self.telegram_channel = os.environ.get("TELEGRAM_CHANNEL", "mutolaaxona").strip()

        self.linkedin_access_token = _required("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_org_urn = _required("LINKEDIN_ORG_URN")

        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.post_timezone = os.environ.get("POST_TIMEZONE", "Asia/Tashkent").strip()
        self.dry_run = os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes")
