# 04 — Native Gameplay Mods and Feature Requirements

## 1. Objective

Implement the requested gameplay features as real Horizon server-side native Rust mods. Java plugin JARs do not run on Horizon. Do not use Bukkit/Paper/Spigot plugin APIs.

Inspect:
- https://github.com/horizon-rust/horizon
- https://github.com/horizon-rust/horizon/blob/main/docs/native-mods.md
- https://github.com/horizon-rust/horizon-mods/tree/main/native/smp

The official SMP mod is separate from the standard Horizon server build. Verify its exact compatibility.json and source revision against the pinned engine before reusing it. Record Horizon, Horizon Mixins, SMP and custom mod revisions.

Native mods run with the server process's permissions. Review and trust code before compiling it into the server.

## 2. Initial feature research baseline

| Requested feature | Official SMP source baseline | Required action |
|---|---|---|
| /sethome, /home | Present | Reuse if compatible |
| /sh, /h aliases | Not listed as requested aliases | Add and test aliases |
| /setwaypoint, /waypointlist, /waypoint | Not established | Implement personal waypoints |
| /sw, /wp, /wl | Not listed | Add aliases |
| /tpa, /tpaccept, /tpdeny | Present | Reuse if compatible |
| /tpr, /tpy, /tpn | Not listed | Add aliases |
| /veinmine | Not established | Implement |
| /ec | Not established as self-service command | Implement |
| /endersee | Official SMP has operator inspection | Not equivalent to /ec |
| PvP duels | Not established | Implement |
| /claim, /unclaim, /trust, /untrust | Present | Reuse if compatible |
| Schematic import | Not established | Research and implement |

This is a source-research baseline, not a guarantee that the current latest revision is compatible. Recheck exact revisions and implementation before status becomes VERIFIED.

## 3. Shared architecture

Create common services for:
- Player identity by UUID.
- Permissions and operator levels.
- Player locations and dimensions.
- Teleport state and safe destination validation.
- Authoritative world mutations.
- Inventory transactions.
- Persistent storage.
- Audit logging.
- Command registration and alias collision detection.

All modules must share the same permission and mutation enforcement paths. Do not duplicate command routers or permission systems. Adapt directory layout to the real native-mod template rather than inventing a loader.

## 4. Homes

Required commands:
- /sethome
- /home
- /sh
- /h

Optional named-home operations:
- /sethome <name>
- /home <name>
- /homes
- /delhome <name>

Requirements: per-player UUID ownership, persistent positions and dimension, configurable limit, validated world/dimension, safe destination, duplicate prevention, permission checks and clean restart behavior. Reuse the official SMP implementation if compatible. Personal home and operator warp are different concepts.

## 5. Personal waypoints

Required:
- /setwaypoint <name>
- /waypointlist
- /waypoint <name>
Aliases:
- /sw
- /wl
- /wp

Requirements: player-specific waypoints; store UUID, name, dimension and position; case-insensitive lookup; duplicate-name prevention; configurable limit; list and delete/rename management where supported; safe destination validation; persistent restore. Do not substitute operator-managed /warp for personal waypoints.

## 6. Temporary teleport requests

Required:
- /tpa <player>
- /tpaccept
- /tpdeny
Aliases:
- /tpr
- /tpy
- /tpn

Requirements: temporary request state, expiry, configurable cooldown, spam prevention, no self-target, reject offline/unknown targets, cancel on disconnect/death according to configured policy, notify both players and ensure acceptance is single-use. If warmup exists, movement or damage cancellation must be server-authoritative and tested.

Reuse official SMP TPA where compatible; add aliases through the documented command registration interface.

## 7. Vein Miner

Command: /veinmine toggles the feature per player.

Requirements:
- Survival mode only.
- Connected matching ores or logs, with configurable block groups.
- Respect tool type, enchantments and durability.
- Preserve valid drops and experience behavior.
- Enforce permissions for every target block.
- Respect claims and other protection systems.
- Bound traversal and maximum connected block count.
- Prevent recursion, duplicate visits and unbounded CPU work.
- Handle unloaded chunks safely.
- Cancel cleanly if the player disconnects, dies or changes state.

Use a bounded graph traversal and supported authoritative block-break hooks. Do not mutate region files directly or bypass the game's normal drop/durability logic. Verify what Horizon hooks actually provide before deciding how to preserve vanilla drops and tool damage.

## 8. Remote personal Ender Chest

Command: /ec.

This is a player's own Ender Chest, not operator /endersee.

Requirements:
- Open a vanilla-compatible menu through supported server hooks.
- Access only the invoking player's own Ender Chest.
- Preserve item components, slot correctness and stack limits.
- Validate every click server-side.
- Make transfers atomic.
- Prevent duplication/loss during disconnect, menu close and save.
- Persist changes.
- Test reconnect and concurrent transaction edge cases.

Do not implement a fake menu that merely displays items without safe transaction handling.

## 9. PvP duels

Requested operator command: /pvp <player>. Initial permission should be operator level 3 or a documented equivalent.

Requirements:
- Configured sky arena and spawn points.
- Duel invitation and acceptance.
- Expiring invitations.
- Validate online players and eligibility.
- Prevent a player entering multiple active duels.
- Safe teleport to arena and return location.
- Match state, timer, damage rules and win detection.
- Death and disconnect handling.
- Cleanup and release arena reservation.
- Persist arena configuration, not transient active match state unless recovery is explicitly implemented.
- Integrate with claims and teleport protections.

A command that only teleports a player is not a duel implementation. Test match completion, death, disconnect and server shutdown.

## 10. Land claims

Reuse official SMP claims/trust where compatible.

Required:
- /claim
- /unclaim
- /trust <player>
- /untrust <player>

Requirements: chunk-level ownership, UUID-based owner/trust records, persistence, no overlap, server-side block break/place checks, container and interact protection, entity interaction and environmental mutation protection wherever supported, admin override and audit logging.

Test:
- Vein Miner cannot break protected blocks.
- Schematic import cannot overwrite claims without explicit authorized policy.
- Pistons, fire, fluids and explosions cannot bypass protection where hooks exist.
- Doors, buttons, levers and containers are protected.
- Trusted and owner permissions work after restart.

If a necessary Horizon hook is absent, report it and develop a minimal documented upstream hook patch rather than bypassing protection.

## 11. Schematic import

Allow authorized administrators to upload and import a local structure file.

Investigate actual support for Sponge schematic, Minecraft structure NBT or other formats. Do not claim a format is supported until parser and integration tests pass.

Requirements:
1. Authenticated upload endpoint, loopback-only by default.
2. File size and type validation.
3. Archive/path traversal protection.
4. Parse and validate dimensions, block identifiers, block states and block-entity data.
5. Bound memory, CPU and total block count.
6. Validate placement coordinates and world/dimension.
7. Check claims/protection and explicit admin override policy.
8. Require a verified pre-import backup.
9. Preview or generate a validation report before mutation where feasible.
10. Apply through authoritative world operations, not raw region file edits.
11. Report progress/failure and provide rollback or restore from backup.

Never expose arbitrary filesystem access or allow schematic uploads to overwrite server configuration, executables or secrets.

## 12. Combined module integrity

All modules must be built and tested together. At startup detect duplicate commands/aliases, invalid config schemas, incompatible hook versions and invalid data migrations.

Required combined regression:
- Homes + waypoint persistence.
- TPA + duel state.
- Claims + Vein Miner.
- Claims + schematic import.
- Ender Chest + disconnect/restart.
- All modules + world backup/restore.
- Alias collisions and permission denial.
- Player UUID changes/name changes where applicable.

## 13. Completion criteria

Each module requires unit tests, a real dedicated-server integration test, command invocation, player interaction, permissions, persistence and combined-module regression tests. Compilation alone is insufficient. Update IMPLEMENTATION_STATUS.md with evidence.