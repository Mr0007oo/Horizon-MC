#!/usr/bin/env python3
"""Best-effort Telegram notification sender."""

from __future__ import annotations

import json
import os
import sys import urllib.parse
import urllib.request


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: notify.py MESSAGE", file=sys.stderr)
        return 2
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_ALERT_CHAT_ID", "")
    if not token or not chat_id:
        print("Telegram notifications skipped: token or alert chat ID not configured.")
        return 0

    payload = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": sys.argv[1], "disable_web_page_preview": "true"}
    ).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError("Telegram API returned ok=false")
    except Exception as exc:
        # Never print the URL or token.
        print(f"Telegram notification failed: {type(exc).__name__} (details redacted).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
