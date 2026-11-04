# Codespaces Setup — First Horizon Server Run

This repository now contains an initial GitHub Actions runtime bootstrap. The workflow is manual and the server has not yet been started against your FRP host.

## 1. Merge the bootstrap PR first

The workflow uses workflow_dispatch. GitHub exposes manual dispatch for workflows on the repository's default branch, so review and merge the bootstrap pull request into main before trying to run it.

After merge, open:

**GitHub repository → Actions → Horizon Minecraft Server → Run workflow**

## 2. Prepare your own Minecraft 26.3 resources

Horizon does not distribute Mojang game assets. Prepare the required resource folder from your own Minecraft Java Edition 26.3 installation, following the official Horizon v0.2.97 hosting guide:

https://github.com/horizon-rust/horizon/blob/v0.2.97/docs/hosting.md

The private resource archive expected by this project must have this shape:

    horizon-resources-26.3.tar.gz
      26.3/
        horizon-resources.json
        registries.json
        commands.json
        ...other prepared Horizon game data...

Create the archive from the parent directory of the prepared 26.3 folder:

    tar -czf horizon-resources-26.3.tar.gz -C /path/to/prepared/resources 26.3
    sha256sum horizon-resources-26.3.tar.gz > horizon-resources-26.3.tar.gz.sha256

Create a **private GitHub release** in this repository with tag:

    resources-26.3

Attach both files:
- horizon-resources-26.3.tar.gz
- horizon-resources-26.3.tar.gz.sha256

The workflow downloads this release using its temporary GITHUB_TOKEN, validates the checksum, and extracts the resource files into runner-local Horizon data. The archive is not committed to main, the world-data branch or build artifacts.

Do not upload Mojang assets to a public release or commit them to source control.

## 3. Configure repository variables

Open **Settings → Secrets and variables → Actions → Variables**.

| Variable | Required | Value |
|---|---:|---|
| FRP_SERVER_ADDR | Yes | Your existing FRPS public hostname or IP only; do not include the port |
| TELEGRAM_ALLOWED_USER_IDS | Recommended | Comma-separated numeric Telegram user IDs allowed to control the server |
| TELEGRAM_ALLOWED_CHAT_IDS | Optional | Comma-separated numeric chat IDs; restricts allowed admin chats |
| TELEGRAM_ALERT_CHAT_ID | Recommended | Numeric Telegram chat ID for admin notifications |

## 4. Configure repository secrets

Open **Settings → Secrets and variables → Actions → Secrets**.

| Secret | Value |
|---|---|
| FRP_AUTH_TOKEN | The token already configured in your FRPS server |
| TELEGRAM_BOT_TOKEN | Use the existing bot token you already configured |

Do not paste secrets into source files, issue comments, workflow inputs or Codespaces terminal commands. The FRP client writes its token to a temporary mode-0600 file and references that file from the generated TOML.

## 5. Existing FRP port mapping

The initial implementation uses the existing FRP server and only enables the Java path:

- FRP control/server port: TCP 7000
- Minecraft Java: TCP remote 25565 → local 127.0.0.1:25565

Bedrock UDP 19132 is not enabled in this first pass. Do not assume Bedrock is available until a tested Geyser/Floodgate/Velocity setup is implemented.

The current workflow sends the FRP Java TCP tunnel directly to Horizon. Horizon is configured to listen on loopback in the Actions runner. The public client endpoint is your FRP hostname on port 25565.

## 6. Start the first server session

In **Actions → Horizon Minecraft Server → Run workflow**:

- Accept the EULA only after you have read and agreed to the Minecraft EULA.
- Enter the Java account username that should receive operator privileges on first initialization.
- Leave the seed as 9064150133272194, unless you deliberately intend to start a different world.

The world identity is initially:

- World name: survival
- Seed: 9064150133272194
- Game version: 26.3
- World data branch: world-data/survival-9064150133272194-26.3

The workflow initializes the world only when there is no existing server.toml; subsequent sessions restore the latest verified snapshot from the world-data branch.

Join using:

    <your-FRP-hostname>:25565

The first run will fail clearly if the resource release, FRP address/token, EULA input or operator username is missing.

## 7. Session timing

The controller measures time from the first workflow step (before checkout and installation):

- 5h00m: first in-game/Telegram warning
- 5h15m: second warning
- 5h25m: graceful shutdown begins (controller polls every 5 seconds)
- 5h50m: workflow hard timeout

This deliberately leaves a shutdown buffer and does not use the full six-hour window. The actual final save and Git push must finish before the workflow timeout. Automatic continuation is not enabled; manually start another session after checking that the previous run completed successfully.

## 8. Telegram commands

Only numeric user IDs listed in TELEGRAM_ALLOWED_USER_IDS are authorized.

Supported initial commands:
- /status
- /players
- /logs
- /say message
- /console command
- /backup
- /restart
- /stop
- /help

/stop requests a manual shutdown; the session controller then creates its final snapshot and exits. It does not auto-restart.

To whitelist a friend during the running session, an authorized administrator can use:

    /console whitelist add PlayerName

Horizon validates player identities according to its current online/offline mode and the exact version's whitelist rules.

## 9. Current implementation scope and limitations

Implemented as an initial bootstrap:
- Pinned Horizon dedicated server installer.
- Pinned FRP client and Java TCP configuration.
- Private resource release downloader and checksum verification.
- Manual GitHub Actions server session.
- 5h00 / 5h15 warnings and 5h25 graceful shutdown target.
- Hourly world snapshot helper, dedicated world-data branch, checksums and current/previous rotation.
- Allowlisted Telegram command bot.
- Offline test suite and CI workflow.

Not yet implemented or end-to-end verified:
- Bedrock UDP/Geyser/Floodgate.
- Java 26.2 protocol translation.
- Public offline/cracked authentication.
- The requested homes/waypoints/Vein Miner/Ender Chest/duel/claim/schematic native mods.
- Actual connectivity through your FRP server.
- Live restore/final-backup test on an Actions runner.

The first Codespaces task after merging is to inspect the CI run, validate the prepared-resource release and run a controlled first server session with no important player data yet.