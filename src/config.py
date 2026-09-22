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

        # Optional proxy for the Telegram connection - needed on hosts (e.g.
        # GitHub Actions runners) whose IP ranges Telegram blocks/throttles.
        self.telegram_proxy_type = os.environ.get("TELEGRAM_PROXY_TYPE", "").strip().lower()
        self.telegram_proxy_host = os.environ.get("TELEGRAM_PROXY_HOST", "").strip()
        self.telegram_proxy_port = os.environ.get("TELEGRAM_PROXY_PORT", "").strip()
        self.telegram_proxy_username = os.environ.get("TELEGRAM_PROXY_USERNAME", "").strip()
        self.telegram_proxy_password = os.environ.get("TELEGRAM_PROXY_PASSWORD", "").strip()

        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.post_timezone = os.environ.get("POST_TIMEZONE", "Asia/Tashkent").strip()
        self.dry_run = os.environ.get("DRY_RUN", "").strip().lower() in ("1", "true", "yes")

        # Public GitHub Pages base URL serving docs/, e.g.
        # https://<user>.github.io/<repo>/  (used as the RSS feed's <link>)
        self.feed_base_url = _required("FEED_BASE_URL").rstrip("/") + "/"
        self.feed_title = os.environ.get("FEED_TITLE", "Mutolaa | Kunlik tanlov").strip()
        self.feed_max_items = int(os.environ.get("FEED_MAX_ITEMS", "60"))

    def telegram_proxy(self):
        """Return a PySocks-style proxy tuple for Telethon, or None if unset."""
        if not self.telegram_proxy_host or not self.telegram_proxy_port:
            return None

        import socks

        proxy_types = {
            "socks5": socks.SOCKS5,
            "socks4": socks.SOCKS4,
            "http": socks.HTTP,
        }
        proxy_type = proxy_types.get(self.telegram_proxy_type, socks.SOCKS5)
        return (
            proxy_type,
            self.telegram_proxy_host,
            int(self.telegram_proxy_port),
            True,
            self.telegram_proxy_username or None,
            self.telegram_proxy_password or None,
        )
