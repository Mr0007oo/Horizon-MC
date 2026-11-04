#!/usr/bin/env python3
"""Allowlisted Telegram control bot; Telegram text is never executed by an OS shell."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.parse
import urllib.request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = {
    item.strip() for item in os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if item.strip().isdigit()
}
ALLOWED_CHATS = {
    item.strip() for item in os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")
    if item.strip()
}
SERVER_DIR = os.environ.get("SERVER_DIR", "")
ROOT = pathlib.Path(os.environ.get("GITHUB_WORKSPACE", "."))
HORIZON = os.environ.get("HORIZON_BIN", "horizon-server")


def api(method: str, payload: dict | None = None, timeout: int = 35):
    url = "https://api.telegram.org/bot{}/{}".format(TOKEN, method)
    data = None if payload is None else urllib.parse.urlencode(payload).encode()
    request = urllib.request.Request(url, data=data, method="GET" if data is None else "POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError("Telegram API returned ok=false")
    return result["result"]


def send(chat_id: int, message: str) -> None:
    api("sendMessage", {
        "chat_id": str(chat_id),
        "text": message[:3900],
        "disable_web_page_preview": "true",
    }, timeout=15)


def horizon(*args: str) -> str:
    result = subprocess.run(
        [HORIZON, "--dir", SERVER_DIR, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=90,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout[-2000:] or "Horizon command failed")
    return result.stdout[-3000:]


def handle(chat_id: int, text: str) -> str:
    command, _, remainder = text.strip().partition(" ")
    command = command.split("@", 1)[0].lower()
    if command == "/help":
        return (
            "/status - server status\n"
            "/players - player list\n"
            "/logs - recent logs\n"
            "/say MESSAGE - broadcast\n"
            "/console COMMAND - one Minecraft console command\n"
            "/backup - make and verify a checkpoint\n"
            "/restart - restart Horizon game process\n"
            "/stop - save and stop this Actions session"
        )
    if command == "/status":
        return horizon("status", "--json")
    if command == "/players":
        return horizon("players", "--json")
    if command == "/logs":
        return horizon("logs", "-n", "60")
    if command == "/restart":
        return horizon("restart")
    if command == "/say":
        message = remainder.strip()
        if not message or any(ord(ch) < 32 for ch in message):
            return "Usage: /say message (single line)"
        return horizon("cmd", "say", message[:240])
    if command == "/console":
        words = remainder.strip().split()
        if not words or len(remainder) > 400 or any(ord(ch) < 32 for ch in remainder):
            return "Usage: /console <single Minecraft console command>"
        # Argument vector only: never invoke bash, sh, PowerShell, eval or shell=True.
        return horizon("cmd", *words)
    if command == "/backup":
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/checkpoint.sh")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=1800,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stdout[-2500:] or "Checkpoint failed")
        return result.stdout[-2500:] or "Checkpoint completed."
    if command == "/stop":
        marker = pathlib.Path(SERVER_DIR) / ".manual-stop"
        marker.write_text("Requested by Telegram chat {}\n".format(chat_id), encoding="utf-8")
        return "Stop requested. The session controller will save and stop the server; it will not auto-restart."
    return "Unknown command. Send /help."


def main() -> int:
    if not TOKEN or not ALLOWED_USERS:
        print("Telegram bot disabled: token or numeric user allowlist is missing.")
        return 0

    offset = 0
    while True:
        try:
            updates = api("getUpdates", {
                "timeout": "25",
                "offset": str(offset),
            }, timeout=35)
            for update in updates:
                offset = max(offset, int(update["update_id"]) + 1)
                message = update.get("message") or update.get("edited_message")
                if not message or not message.get("text"):
                    continue
                user_id = str(message.get("from", {}).get("id", ""))
                chat_id = int(message.get("chat", {}).get("id", 0))
                if user_id not in ALLOWED_USERS:
                    continue
                if ALLOWED_CHATS and str(chat_id) not in ALLOWED_CHATS:
                    continue
                try:
                    reply = handle(chat_id, message["text"])
                except Exception as exc:
                    reply = "Command failed: {}. Check server logs for details.".format(type(exc).__name__)
                send(chat_id, reply or "Done.")
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            # Never log the request URL; Telegram bot URLs contain the bot token.
            print("Telegram polling error: {} (details redacted).".format(type(exc).__name__),
                  file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
