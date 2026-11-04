# Horizon MC — Runtime Architecture

## Components

1. **GitHub Actions workflow** — one manually dispatched, time-bounded server session on Ubuntu 24.04.
2. **Horizon** — Rust-based Minecraft Java Edition 26.3 dedicated server, installed at the pinned release.
3. **FRPC** — pinned FRP client running in the same job, exposing the loopback-bound Java listener through the owner's existing FRPS server.
4. **World snapshot store** — a separate Git worktree and remote branch, world-data/<world-id>, containing only verified current/previous world archives and manifests.
5. **Telegram controller** — long-polling bot with numeric sender/chat allowlists and argument-vector-only Horizon CLI calls.
6. **Prepared resources release** — private, checksum-verified GitHub release asset containing owner-prepared Minecraft 26.3 resources.

## Network

    Java clients
       |
       v
    Owner's public FRPS host
       | TCP 25565 (Minecraft)
       | TCP 7000  (FRP control connection)
       v
    FRPC inside GitHub Actions
       |
       v
    Horizon server bound to 127.0.0.1:25565

The current bootstrap implements Java TCP only. Bedrock UDP and Velocity/Geyser/Floodgate are deliberately not represented as complete.

## Runtime lifecycle

The timer is initialized in the workflow's first step. Horizon starts after setup and restore. The controller:
- sends warnings at 300 and 315 minutes;
- creates hourly consistent backups;
- begins graceful stop at 325 minutes;
- verifies a stopped phase;
- creates a final clean-shutdown snapshot;
- verifies the remote world-data ref;
- exits before the 350-minute job timeout.

A failure to verify the final snapshot fails the workflow and keeps the previous remote checkpoint.

## Data boundary

Source, scripts, tests and documentation belong on main. World data belongs on the dedicated world branch. Prepared game resources are kept in a private release and copied only to runner-local Horizon data. Secrets are passed through Actions Secrets and never committed.

The world snapshot helper enforces a conservative archive and Git history budget. Git history is not a rolling binary database; if the world grows beyond the limit, use object storage or a persistent disk rather than rewriting history or splitting archives to evade file limits.

## Trust boundaries

- Only manually dispatched workflow inputs may choose seed and operator username; both are validated.
- FRPC credentials are loaded from Actions Secrets.
- Telegram commands require numeric allowlists and never execute an OS shell.
- Horizon backend listens only on loopback in this design.
- EULA acceptance is explicit and is not prechecked.
- Offline/cracked identity is not included because offline mode alone does not authenticate player identities.