# Horizon MC — Architecture Decisions

## DEC-001 — Use the actual Horizon upstream
Use https://github.com/horizon-rust/horizon and its documented dedicated server. Do not replace Horizon with a different server.

## DEC-002 — Native Rust extensions
Use Horizon native mods and Horizon Mixins. Java plugin JARs are not a compatible extension mechanism.

## DEC-003 — Reuse official SMP features only with a matching engine
The inspected SMP source at `horizon-rust/horizon-mods` commit `ee1620f438c853b03ff2c568f4c4b1b443211294` declares Horizon `48c63bc09d9acc82f2074e75ae59720514796a9d` and Horizon Mixins `d9c83d7096b7ea5b83678da2efdfd6161f74997e`. This does not match the project's pinned Horizon `a3acb5f0d2f59d2d5ff21a5aa000809ba1e35e2f`; do not reuse/build this SMP revision until a compatible, tested revision set is selected.

## DEC-004 — Java 26.3 as initial server target
The inspected Horizon server docs describe Java Edition 26.3. Java 26.2 client compatibility is a separate unverified requirement and must not be inferred from save migration.

## DEC-005 — Cross-play proxy path
Investigate Velocity + Geyser + Floodgate, following Horizon's documented modern forwarding. Do not mark Bedrock support complete until end-to-end tests pass.

## DEC-006 — Offline mode is not authentication
Horizon supports offline mode, but that mode does not verify account ownership. Public cracked/offline access requires a verified authentication architecture or must remain blocked.

## DEC-007 — Reuse the existing FRP server
The owner already operates FRPS. The initial FRPC client is pinned to v0.71.1 and maps Java TCP 25565 through FRPS control port 7000. Bedrock UDP remains a later, separately tested extension. Confirm the owner's frps version before first live run.

## DEC-008 — Bounded GitHub Actions sessions
Warn at 5h00, send second warning at 5h15 and begin graceful shutdown at 5h25. The Actions job timeout is 5h50; never target the full six-hour window. Timer checks poll every five seconds; hourly backups stop starting after 4h30 to protect the final shutdown window.

## DEC-009 — Separate world persistence
Keep source on main and runtime world snapshots on world-data/<world-id>. Git storage is size-limited; refuse oversized snapshots without damaging the previous valid copy.

## DEC-010 — Controlled continuation only
Automatic continuation is disabled by default, budget-controlled and allowed only after a verified final snapshot. It does not guarantee 24/7 uptime or bypass platform limits.

## DEC-011 — Telegram allowlist
Use numeric Telegram ID allowlists. Telegram messages are never OS shell commands.

## DEC-012 — Handoff PR workflow
Create a feature branch based on the latest canonical main, push it to Mr0007oo/Horizon-MC and open a PR into main. Do not push directly to main. When gh CLI authentication fails, test the workspace's existing Git credential transport; stop if remote Git is also unauthorized.

## Pending decisions
- Exact Horizon Mixins and SMP revisions for future native mods.
- Java 26.2 compatibility path.
- Bedrock dependency versions and authentication.
- Owner's installed frps version and whether it accepts frpc v0.71.1.
- Maximum world archive size and fallback storage beyond the current conservative limit.
- Continuation cycle/billing budget (continuation remains disabled).
- Native hook gaps for requested gameplay features.