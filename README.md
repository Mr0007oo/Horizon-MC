# Horizon MC

A community server hosting and management project built around the Rust-based Horizon Minecraft dedicated server.

**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC

## Current state

The initial runtime bootstrap is implemented on the feature branch. It is **not yet live-verified** against the owner's FRP server or prepared Minecraft resources. Review and merge the bootstrap PR, complete the one-time setup, then dispatch the Actions workflow manually.

## Read first

1. [Master PRD](PRD.md)
2. [Codespaces and first-run setup](docs/SETUP-CODESPACES.md)
3. [Runtime architecture](docs/ARCHITECTURE.md)
4. [.github/copilot-instructions.md](.github/copilot-instructions.md)
5. [Implementation status](IMPLEMENTATION_STATUS.md)
6. [Architecture decisions](DECISIONS.md)
7. [Current handoff](HANDOFF.md)

Detailed requirements live in docs/requirements/.

## Initial runtime bootstrap

- Pinned Horizon dedicated server v0.2.97.
- Pinned FRP client v0.71.1.
- Manual GitHub Actions session workflow with a 350-minute hard timeout.
- First warning at 5h00m, second warning at 5h15m, graceful shutdown begins at 5h25m.
- Hourly snapshots and final world snapshot on a dedicated world-data branch.
- Java TCP 25565 through the existing FRP server (control port 7000).
- Allowlisted Telegram bot for initial operations.
- Default world seed: 9064150133272194.

## Required one-time setup

Prepare your own Minecraft 26.3 resources and upload them to the private GitHub release described in [SETUP-CODESPACES.md](docs/SETUP-CODESPACES.md). Configure FRP and Telegram Actions secrets/variables. The workflow intentionally stops with a clear validation error until these are present.

## Upstream projects

- [Horizon](https://github.com/horizon-rust/horizon)
- [Horizon dedicated server distribution](https://github.com/horizon-rust/horizon-server)
- [Official Horizon native mods](https://github.com/horizon-rust/horizon-mods)

## Important limitations

The initial bootstrap supports Java 26.3 only. Bedrock, Java 26.2 translation, public offline/cracked authentication, and the requested gameplay native mods are not included in this first implementation. Live runner, public network and restore validation are still required.

GitHub Actions is not guaranteed permanent hosting. Automatic continuation is disabled; each new session is started manually after reviewing the previous run.