# 05 — Telegram Bot and Remote Administration

## Objective

Run an outbound Telegram Bot API controller alongside Horizon for status, notifications and allowlisted administration. Telegram is not required for world saving and must not be a single point of failure for persistence.

The owner has already configured TELEGRAM_BOT_TOKEN. Read it only from GitHub Actions Secrets. Never ask the owner to paste it again, commit it, echo it or include it in logs.

## Additional configuration

- TELEGRAM_ALLOWED_USER_IDS: comma-separated numeric Telegram user IDs.
- TELEGRAM_ALLOWED_CHAT_IDS: optional allowed chat IDs.
- TELEGRAM_ALERT_CHAT_ID: target for server notifications.

Do not authorize by display name or username. Reject all admin commands from unapproved numeric user IDs.

## Implementation

Use a small Rust or Python controller with Telegram long polling and outbound HTTPS. Avoid a public webhook endpoint unless a future reviewed design requires one. Use bounded retry, rate limiting, update offset tracking and graceful termination.

Start the bot only after the Horizon supervisor/control interface is ready. Stop it during workflow shutdown.

## Commands

/status
- Online/offline state.
- Minecraft version.
- Horizon revision/release.
- Uptime and job elapsed time remaining.
- TPS/MSPT.
- RAM/CPU.
- Player count.
- FRP status.
- Latest verified backup time and commit.

Use actual output from the pinned Horizon CLI. Do not invent JSON fields.

 /players
- Use the supported `horizon-server cmd list` console command in the pinned v0.2.97 release.
- Return the Minecraft online-player list only; do not expose unnecessary IP addresses.

/console <Minecraft console command>
- Only allowlisted users.
- Pass one validated Minecraft console command to the documented horizon-server cmd interface.
- Never execute Telegram input through bash, sh, PowerShell, eval, a subprocess shell or an OS command interpreter.
- Reject multiline input and control characters that alter command boundaries.
- Log administrator ID, timestamp, requested command and sanitized outcome.

/say <message>
- Send a server broadcast through Horizon's documented CLI.

/backup
- Request a serialized Horizon backup and remote snapshot.
- Refuse to start a manual backup when less than 30 minutes remain before scheduled shutdown; cap the attempt to 15 minutes.
- Report both local backup result and remote world-data branch result.

/logs
- Return a limited, redacted tail of the relevant Horizon logs.
- Never dump environment variables or secrets.

/restart
- Restart the Horizon game process through the pinned supervisor CLI. This does not restart the GitHub Actions job or reset its 5h25 session deadline.

/stop
- Write a per-session manual-stop marker. The session controller then performs the same graceful stop and final snapshot path; no successor workflow is dispatched.

/help
- List authorized administration commands.

## Notifications

Send concise notifications for:
- Server startup and world restore.
- Java endpoint health.
- Bedrock endpoint health if enabled.
- Player join/leave if event stream support is verified.
- 5h00 warning.
- 5h15 warning.
- Shutdown start and completion.
- Backup start/success/failure.
- Snapshot push and remote verification.
- Critical errors.
- Continuation skipped or dispatched.

Rate-limit repeated errors; do not flood the admin chat.

## Failure behavior

If Telegram is unavailable:
- Keep the Minecraft server running.
- Continue hourly persistence independently.
- Retry with bounded backoff.
- Record the notification failure in workflow logs without exposing token.
- Do not shut down the server solely because Telegram is unavailable.

The bot advances the Telegram update offset for every received update and ignores messages whose timestamp predates the current bot process start. This prevents queued commands from an earlier Actions session from being replayed. Never replay a potentially destructive administrative command as a result of a duplicate update.

## Acceptance tests

- Authorized status and player commands work.
- Unauthorized IDs cannot control or inspect the server.
- Console command reaches Minecraft but cannot execute OS shell commands.
- Backup reports local and remote results truthfully.
- Stop disables continuation.
- Restart follows graceful lifecycle.
- Telegram outage does not corrupt persistence.
- No token appears in source, logs or test artifacts.