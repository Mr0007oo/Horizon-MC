# Horizon MC

A community server hosting and management project built around the Rust-based Horizon Minecraft dedicated server.

**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC

## Status

This repository currently contains requirements and planning documents. It does not yet contain a verified production server workflow or completed gameplay mods.

## Read first

1. [Master PRD](PRD.md)
2. [.github/copilot-instructions.md](.github/copilot-instructions.md)
3. [Implementation status](IMPLEMENTATION_STATUS.md)
4. [Architecture decisions](DECISIONS.md)
5. [Current handoff](HANDOFF.md)

Detailed requirements live in docs/requirements/.

## Upstream projects

- [Horizon](https://github.com/horizon-rust/horizon)
- [Horizon dedicated server distribution](https://github.com/horizon-rust/horizon-server)
- [Official Horizon native mods](https://github.com/horizon-rust/horizon-mods)

## Important prerequisites

Horizon requires game resources prepared from the owner's own Minecraft Java Edition 26.3 installation. Do not commit Mojang assets or obtain them through an unauthorized redistribution path.

The owner already has an FRP server and Telegram bot token configured. Put credentials into GitHub Actions Secrets; never store values in this repository.

## Intended design

- Bounded GitHub Actions server sessions.
- Existing FRP infrastructure for stable public TCP/UDP endpoints.
- Hourly consistent snapshots and a final graceful-shutdown checkpoint.
- Dedicated world-data branch separate from source.
- Telegram allowlisted operations.
- Native Rust gameplay modules.

GitHub Actions is not guaranteed permanent hosting. Automatic session continuation is optional, budget-controlled and subject to current GitHub limits.

## Development

Complete Phase 0 research and pin exact upstream revisions before implementation. See PRD.md.