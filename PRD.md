# Horizon MC — Master Product Requirements Document

**Version:** 2.3  
**Repository:** https://github.com/Mr0007oo/Horizon-MC  
**Primary branch:** main  
**Runtime:** Horizon Minecraft Rust dedicated server  
**Orchestration:** GitHub Actions  
**Networking:** Owner-provided FRP server  
**Administration:** Telegram Bot  
**Persistence:** Dedicated world-data branch  
**Status:** Specification; implementation not yet verified

---

## 1. Vision

Build a maintainable Minecraft community server using the actual Horizon Rust-based dedicated server. GitHub Actions will host bounded sessions, the owner's existing FRP server will provide a stable public endpoint, a dedicated repository branch will hold verified world snapshots, and Telegram will provide authorized administration.

Prioritize data integrity, verifiable compatibility and safe recovery over feature count.

## 2. Non-negotiable engineering rules

1. Use the actual upstream project: https://github.com/horizon-rust/horizon
2. Use the standalone server documentation: https://github.com/horizon-rust/horizon/blob/main/docs/hosting.md
3. Use the native mod API: https://github.com/horizon-rust/horizon/blob/main/docs/native-mods.md
4. Inspect the exact pinned upstream revision before using commands, flags, settings, hooks or mod interfaces.
5. Do not treat Horizon as Paper, Spigot, Bukkit, Fabric or Forge. Java plugin JARs do not run as Horizon native mods.
6. Do not invent APIs, commands, protocol identifiers, config keys, release assets, checksums or compatibility claims.
7. Do not replace Horizon with another Minecraft implementation without recording the architectural decision and receiving owner approval.
8. Mark unsupported or unverified features as BLOCKED or PENDING; never represent placeholders as working features.
9. Never commit credentials, Mojang game assets, runner caches, world files or backup archives to main.
10. Never claim GitHub Actions provides guaranteed or unrestricted 24/7 hosting.

## 3. Upstream facts to re-verify at implementation time

The inspected upstream source describes horizon-server as a standalone Minecraft Java Edition 26.3 server. It uses Horizon's Rust game engine. It requires game resources prepared from the owner's own copy of Minecraft 26.3; those resources are not redistributed by the project.

Horizon supports native Rust mods built through Horizon Mixins. Java mod/plugin JARs do not run.

The official Horizon mods repository contains a native SMP mod:
https://github.com/horizon-rust/horizon-mods/tree/main/native/smp

That mod is separate from the standard server build. Its current code and compatibility metadata must be checked against the selected Horizon revision before reuse.

Horizon hosting documentation describes Velocity modern forwarding and a Geyser/Floodgate Bedrock path. Re-verify the exact Geyser, Floodgate, Velocity and Horizon versions together.

Horizon documents offline mode using online_mode = false, but offline mode does not authenticate player identities. Public offline-mode access requires a deliberate authentication and proxy architecture; it must not be described as secure merely because a player name is supplied.

These are research baselines, not permission to skip version-pinned verification.

## 4. Product objectives

- Start Horizon through a bounded GitHub Actions workflow.
- Reuse the owner's existing FRP server; do not rebuild it unnecessarily.
- Publish a stable player-facing address independent of the ephemeral runner IP.
- Map Java traffic over TCP and Bedrock traffic over UDP when Bedrock is enabled.
- Support Java Edition 26.3 natively.
- Investigate Java Edition 26.2 client compatibility independently; world-save migration is not client protocol compatibility.
- Investigate Bedrock cross-play through Velocity + Geyser + Floodgate.
- Support offline-mode clients only with clearly documented identity and impersonation risks.
- Send a first maintenance warning at 5h00m of job elapsed time.
- Send a second warning at 5h15m.
- Begin graceful shutdown at exactly 5h25m (325 minutes) of job elapsed time, leaving a 25-minute save/push window before the 5h50m job timeout.
- Create an hourly checkpoint while the server is running.
- Create and verify a final checkpoint after graceful shutdown.
- Persist world and player data on a dedicated world-data/<world-id> branch, not main.
- Control and monitor the server using an allowlisted Telegram bot.
- Reuse compatible official SMP functionality and implement missing requested functionality as native Rust mods.
- Verify modules together for conflicts and regressions.

## 5. Supporting requirements

The detailed requirements are normative and must be read alongside this master PRD:

| File | Scope |
|---|---|
| [01-hosting-lifecycle.md](docs/requirements/01-hosting-lifecycle.md) | Actions session lifecycle, 5h00 and 5h15 warnings, graceful shutdown at 5h25, hourly snapshots |
| [02-persistence.md](docs/requirements/02-persistence.md) | world-data branch, snapshot format, integrity, recovery, seed isolation |
| [03-networking-crossplay.md](docs/requirements/03-networking-crossplay.md) | FRP variables and transport, Velocity, Geyser, Floodgate, version and offline-mode verification |
| [04-gameplay-mods.md](docs/requirements/04-gameplay-mods.md) | official SMP reuse, homes, waypoints, TPA, Vein Miner, Ender Chest, duels, claims, schematic import |
| [05-telegram-control.md](docs/requirements/05-telegram-control.md) | Telegram commands, notifications, authorization and safe console forwarding |
| [06-testing-handoff.md](docs/requirements/06-testing-handoff.md) | test gates, combined integration, handoff, git and PR workflow |

Copilot behavior is governed by [.github/copilot-instructions.md](.github/copilot-instructions.md). The hand-off prompt is [.github/prompts/hand-off.prompt.md](.github/prompts/hand-off.prompt.md).

## 6. Hosting architecture

Logical architecture:

    Players
      |
      v
    Public FRP host (existing frps)
      | TCP Java port / UDP Bedrock port
      v
    FRPC in GitHub Actions runner
      |
      v
    Velocity proxy (if required)
      |------------------------------|
      v                              v
    Java backend path             Geyser UDP listener
      |                              |
      +----------> Horizon <---------+
                   dedicated server
                        |
               verified world snapshot
                        |
           world-data/<world-id> branch

The exact listener ports, topology and supported proxy integration must be derived from the real configuration and tested. Do not expose the Horizon backend directly when proxy forwarding is configured.

## 7. Existing FRP configuration supplied by owner

The owner reports an existing FRP server and these intended port values:

- FRP control/listener port: 7000
- Java public port: 25565
- Java local target port: 25565
- Bedrock public port: 19132
- Bedrock local target port: 19132

Normalize the ambiguous original variables. Use separate names:

- FRP_SERVER_ADDR
- FRP_SERVER_PORT = 7000
- FRP_AUTH_TOKEN
- FRP_JAVA_REMOTE_PORT = 25565
- FRP_JAVA_LOCAL_PORT = 25565
- FRP_BEDROCK_REMOTE_PORT = 19132
- FRP_BEDROCK_LOCAL_PORT = 19132
- FRP_LOCAL_HOST = 127.0.0.1

Java Minecraft traffic is TCP. Bedrock traffic is UDP. The FRP control port is not a Minecraft client port. Verify the actual FRP configuration syntax and whether the existing server allows both transports against the installed FRP version.

The owner has already configured TELEGRAM_BOT_TOKEN. Never request that token in chat or commit it. Store it as an Actions Secret.

## 8. GitHub Actions session lifecycle

The default project timing starts at the first job step, before checkout, and is measured from the allocated Actions job start:

| Elapsed job time | Operation |
|---|---|
| 0m | Validate inputs, secrets, concurrency and runner |
| 0–10m | Restore world and initialize runtime/network |
| 60m intervals | Consistent backup and remote checkpoint |
| 300m (5h00m) | First player and Telegram warning |
| 315m (5h15m) | Second warning |
| 325m (5h25m) | Begin graceful shutdown immediately |
| 325–345m | Final backup, validation, push and verification |
| 350m (5h50m) | Hard workflow timeout; 10-minute safety margin remains before six hours |

These timings are project defaults, not GitHub platform guarantees. At implementation time verify the applicable runner/job timeout and retain a safety margin. If bootstrap time or platform limits make the schedule unsafe, adjust it and document the decision.

The shutdown sequence must use the documented Horizon supervisor/CLI for the pinned release. Do not invent a console API or assume Ctrl-C semantics without testing.

## 9. Automatic continuation and the 24/7 objective

Automatic continuation is optional and defaults to disabled.

A successor run may be dispatched only after:
- Horizon stops successfully.
- The final backup is valid.
- The snapshot manifest and checksum validate.
- The expected commit is confirmed on the remote world-data branch.
- No manual stop, cancellation or critical error is active.
- Explicit daily and monthly usage budgets allow another session.
- Current GitHub usage limits and platform restrictions permit the run.

Dispatch exactly one successor; prevent overlapping server instances with a shared concurrency group and a durable continuation/run identifier. The next run must independently fetch and verify the latest snapshot before launching.

This mechanism does not guarantee 24/7 operation. A 30-day month of uninterrupted execution requires 43,200 runner-minutes before overhead. Queues, quotas, billing, platform limits and outages remain applicable. Do not evade limits or describe repeated workflow dispatch as unlimited hosting.

## 10. Persistence architecture

The initial world seed supplied by the owner is **9064150133272194**. The initial world name is `survival`, game version is `26.3`, and world ID is `survival-9064150133272194-26.3`. Use a separate branch for each world identity:

world-data/<world-id>

A world ID must be derived from validated seed and generation-relevant configuration. Changing the seed or world-generation identity must create a separate namespace and must never overwrite the previous world.

Persist:
- Overworld, Nether and End data.
- Player data, statistics and advancements.
- Whitelist, operators and bans.
- Native-mod databases and configuration.
- Homes, waypoints, claims and trust relationships.
- Ender Chest data and other gameplay state.
- Snapshot manifest and checksums.

Use Horizon's supported backup/snapshot mechanism. Never copy a changing world directory as though it were a consistent snapshot.

Retain at least the current and previous verified snapshots. Do not replace the previous valid snapshot until the new snapshot is verified remotely.

Git is a constrained persistence backend, not a database or large binary object store. Use conservative configurable per-file and repository-size limits. The initial project defaults are 90,000,000 bytes per snapshot file, 750 MB total repository-size warning threshold, and two retained snapshots. These are safety limits, not statements of GitHub's account quotas. If the snapshot exceeds the configured limit, stop the push, preserve the prior snapshot and notify the owner. Do not split files to evade hosting limits. Recommend external object storage or a persistent VPS disk if the world outgrows Git.

## 11. Required gameplay features

Requested player commands and features:

- Homes: /sethome, /home; aliases /sh, /h.
- Personal waypoints: /setwaypoint <name>, /waypointlist, /waypoint <name>; aliases /sw, /wl, /wp.
- Temporary teleport requests: /tpa <player>, /tpaccept, /tpdeny; aliases /tpr, /tpy, /tpn.
- Vein Miner: /veinmine toggle; connected matching ores/logs, survival only.
- Remote personal Ender Chest: /ec.
- PvP duels: sky arena and /pvp <player> command with the requested operator permission.
- Claims: /claim, /unclaim, /trust <player>, /untrust <player>.
- WorldEdit-style schematic upload/import for authorized administrators.

Initial upstream research found homes, TPA, claims/trust and operator-managed warps in the official SMP native mod. It did not establish that personal waypoints, Vein Miner, self-service /ec, PvP duels or schematic import already exist as requested. Recheck exact revisions and the latest upstream source before implementation. /endersee is an operator inspection feature and is not the same as a player's /ec.

All custom functionality must use real server-side hooks and the shared permission, identity, world-mutation, inventory-transaction and persistence services. Test all requested features together, especially claims with Vein Miner and schematic import, and inventories with disconnect/restart behavior.

## 12. Telegram administration

Use TELEGRAM_BOT_TOKEN from GitHub Actions Secrets and a numeric allowlist of Telegram user IDs.

Required commands:
- /status
- /players
- /console <Minecraft console command>
- /say <message>
- /backup
- /logs
- /restart
- /stop
- /help

Telegram input must never be executed by an operating-system shell. Only authorized users may administer the server. The bot must not be a prerequisite for Minecraft persistence and must stop cleanly at workflow termination.

## 13. Security and secrets

- Use Actions secrets for FRP and Telegram credentials.
- Use least-privilege workflow permissions.
- Never print secret values.
- Never commit .env, credentials, tokens, forwarding secrets or private runtime files.
- Restrict backend listener access.
- Use modern proxy forwarding with a nonempty secret when using Velocity.
- Offline mode must not be presented as authenticated identity.
- Do not disable GitHub repository security controls or bypass access restrictions.

## 14. Implementation phases

### Phase 0 — Feasibility and research
Pin Horizon, Horizon Mixins, official SMP and runtime revisions. Verify 26.3 startup, required game resources, server API, backup behavior, FRP version/topology, Velocity/Geyser/Floodgate path, 26.2 translation and offline authentication. Update architecture and status. Block unsupported requirements explicitly.

### Phase 1 — Minimal server
Bootstrap the pinned dedicated server, import prepared resources, create configuration, start and report health.

### Phase 2 — Networking
Run FRPC, establish public Java TCP mapping, then add Bedrock UDP mapping only when proxy components are verified.

### Phase 3 — Persistence
Implement restore, hourly backup, manifest/checksum, branch synchronization, previous snapshot retention, final backup and recovery tests.

### Phase 4 — Session lifecycle
Implement warnings, graceful stop, bounded timeout, manual stop handling and opt-in budget-controlled continuation.

### Phase 5 — Telegram
Implement allowlisted Telegram commands and notifications independently of the server lifecycle.

### Phase 6 — Gameplay
Integrate compatible official SMP functionality; implement and prove missing native modules.

### Phase 7 — Compatibility
Verify Java 26.3, investigate Java 26.2 translation, test Bedrock and offline identity architecture.

### Phase 8 — Final validation
Run combined mod tests, real client tests, session simulation, snapshot recovery and failure-injection tests.

## 15. Completion criteria

The project is complete only when:
- A pinned Horizon dedicated server starts on the runner.
- Prepared game resources are supplied lawfully by the owner and validated.
- The stable public Java endpoint works through FRP.
- Bedrock works if enabled and proven.
- Java 26.3 works; Java 26.2 is only advertised if integration tests prove it.
- Offline mode risks and identity handling are documented and tested.
- Hourly checkpoints and final checkpoint pass integrity tests.
- The 5h00 and 5h15 notices arrive.
- Graceful shutdown begins at 5h25, not later.
- Graceful shutdown finishes before job timeout.
- A failed save or push prevents continuation.
- Restore and rollback are tested.
- Telegram permissions and commands work.
- Every required gameplay feature has real implementation and combined tests.
- No credentials or game assets are committed.
- README, status and troubleshooting documentation reflect reality.

## 16. Status vocabulary

Use NOT_STARTED, RESEARCHING, IN_PROGRESS, TESTING, VERIFIED, BLOCKED and FAILED. Every VERIFIED entry must link to concrete test output, commit or proof. Maintain IMPLEMENTATION_STATUS.md and DECISIONS.md.

The primary objective is a reliable and technically valid community server, not merely a large generated codebase.
