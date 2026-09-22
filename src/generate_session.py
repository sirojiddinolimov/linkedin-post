"""Generate a Telethon session string locally using Telegram QR login.

Run locally (never in CI):
    python src/generate_session.py

The script prints a QR code in the terminal. On the phone where the Telegram
account is already signed in, use Settings -> Devices -> Link Desktop Device
and scan it. The resulting session string grants full account access; keep it
private and save it only as the TELEGRAM_SESSION_STRING GitHub secret.
"""

from __future__ import annotations

import asyncio
import getpass
import os
from pathlib import Path

import qrcode
from telethon import TelegramClient, errors
from telethon.sessions import StringSession


def print_qr(url: str, image_path: Path | None = None) -> None:
    """Render a scannable QR code using plain terminal characters."""
    code = qrcode.QRCode(border=2)
    code.add_data(url)
    code.make(fit=True)
    matrix = code.get_matrix()

    if image_path is not None:
        image_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        code.make_image().save(str(image_path))
        os.chmod(image_path, 0o600)

    print("\nScan this QR code from Telegram on your phone:\n")
    for row in matrix:
        print("".join("██" if cell else "  " for cell in row))
    print()


async def generate_session() -> None:
    api_id = int(input("TELEGRAM_API_ID: ").strip())
    api_hash = getpass.getpass("TELEGRAM_API_HASH: ").strip()

    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()

    try:
        image_path = os.environ.get("SESSION_QR_IMAGE_PATH")
        url_path = os.environ.get("SESSION_QR_URL_PATH")
        while True:
            qr_login = await client.qr_login()
            if url_path:
                url_file = Path(url_path).expanduser()
                url_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                url_file.write_text(qr_login.url + "\n", encoding="utf-8")
                os.chmod(url_file, 0o600)
            print_qr(qr_login.url, Path(image_path) if image_path else None)
            print("On Telegram: Settings -> Devices -> Link Desktop Device -> scan the QR above.")
            print("Waiting for Telegram approval...\n")

            try:
                await qr_login.wait()
                break
            except asyncio.TimeoutError:
                print("That QR expired; generating a fresh QR code.\n")
            except errors.SessionPasswordNeededError:
                password = getpass.getpass("Telegram 2FA password: ")
                await client.sign_in(password=password)
                break

        session_string = client.session.save()
        output_path = Path(
            os.environ.get(
                "SESSION_OUTPUT_PATH",
                str(Path(__file__).resolve().parents[2] / "telegram_session_string"),
            )
        ).expanduser()
        output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        output_path.write_text(session_string + "\n", encoding="utf-8")
        os.chmod(output_path, 0o600)
        print("Telegram login approved.")
        print(f"Session saved securely to {output_path}")
        if image_path:
            Path(image_path).unlink(missing_ok=True)
        if url_path:
            Path(url_path).unlink(missing_ok=True)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(generate_session())
