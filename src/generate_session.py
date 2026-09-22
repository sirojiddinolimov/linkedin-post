"""One-time helper to generate a Telethon session string.

Run locally (never in CI):
    python src/generate_session.py

You will be asked for your API ID/hash and to log in with your phone number
and a one-time code sent by Telegram. The resulting string is your
TELEGRAM_SESSION_STRING secret - keep it private, it grants full account access.
"""

from telethon import TelegramClient
from telethon.sessions import StringSession


def main() -> None:
    api_id = int(input("TELEGRAM_API_ID: ").strip())
    api_hash = input("TELEGRAM_API_HASH: ").strip()

    with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()
        print("\nTELEGRAM_SESSION_STRING=" + session_string)
        print("\nSave this value as a GitHub Actions secret named TELEGRAM_SESSION_STRING.")


if __name__ == "__main__":
    main()
