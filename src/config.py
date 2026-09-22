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

        proxy_host = os.environ.get("TELEGRAM_PROXY_HOST", "").strip()
        proxy_port = os.environ.get("TELEGRAM_PROXY_PORT", "").strip()
        proxy_username = os.environ.get("TELEGRAM_PROXY_USERNAME", "").strip()
        proxy_password = os.environ.get("TELEGRAM_PROXY_PASSWORD", "").strip()
        if bool(proxy_host) != bool(proxy_port):
            raise RuntimeError(
                "TELEGRAM_PROXY_HOST and TELEGRAM_PROXY_PORT must be set together"
            )
        if bool(proxy_username) != bool(proxy_password):
            raise RuntimeError(
                "TELEGRAM_PROXY_USERNAME and TELEGRAM_PROXY_PASSWORD must be set together"
            )
        self.telegram_proxy = (
            (
                "socks5",
                proxy_host,
                int(proxy_port),
                True,
                proxy_username or None,
                proxy_password or None,
            )
            if proxy_host
            else None
        )

        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.post_timezone = os.environ.get("POST_TIMEZONE", "Asia/Tashkent").strip()
        self.dry_run = os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes")

        # Public GitHub Pages base URL serving docs/, e.g.
        # https://<user>.github.io/<repo>/  (used as the RSS feed's <link>)
        self.feed_base_url = _required("FEED_BASE_URL").rstrip("/") + "/"
        self.feed_title = os.environ.get("FEED_TITLE", "Mutolaa | Kunlik tanlov").strip()
        self.feed_max_items = int(os.environ.get("FEED_MAX_ITEMS", "60"))
