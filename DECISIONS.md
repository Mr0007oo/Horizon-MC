# Horizon MC — Architecture Decisions

## DEC-001 — Use the actual Horizon upstream
Use https://github.com/horizon-rust/horizon and its documented dedicated server. Do not replace Horizon with a different server.

## DEC-002 — Native Rust extensions
Use Horizon native mods and Horizon Mixins. Java plugin JARs are not a compatible extension mechanism.

## DEC-003 — Reuse official SMP features
Inspect and pin the official horizon-rust/horizon-mods native SMP module. Reuse only what is compatible with the pinned engine and test it.

## DEC-004 — Java 26.3 as initial server target
The inspected Horizon server docs describe Java Edition 26.3. Java 26.2 client compatibility is a separate unverified requirement and must not be inferred from save migration.

## DEC-005 — Cross-play proxy path
Investigate Velocity + Geyser + Floodgate, following Horizon's documented modern forwarding. Do not mark Bedrock support complete until end-to-end tests pass.

## DEC-006 — Offline mode is not authentication
Horizon supports offline mode, but that mode does not verify account ownership. Public cracked/offline access requires a verified authentication architecture or must remain blocked.

## DEC-007 — Reuse the existing FRP server
The owner already operates FRPS. Only implement an FRPC client with separate Java TCP and Bedrock UDP mappings, after checking the installed FRP version.

## DEC-008 — Bounded GitHub Actions sessions
Warn at 5h20, send second warning at 5h30 and begin graceful shutdown at 5h40 by default. Verify current runner limits and leave a safe exit margin.

## DEC-009 — Separate world persistence
Keep source on main and runtime world snapshots on world-data/<world-id>. Git storage is size-limited; refuse oversized snapshots without damaging the previous valid copy.

## DEC-010 — Controlled continuation only
Automatic continuation is disabled by default, budget-controlled and allowed only after a verified final snapshot. It does not guarantee 24/7 uptime or bypass platform limits.

## DEC-011 — Telegram allowlist
Use numeric Telegram ID allowlists. Telegram messages are never OS shell commands.

## DEC-012 — Handoff PR workflow
Create a feature branch based on the latest canonical main, push it to Mr0007oo/Horizon-MC and open a PR into main. Do not push directly to main. When gh CLI authentication fails, test the workspace's existing Git credential transport; stop if remote Git is also unauthorized.

## Pending decisions
- Exact pinned Horizon release and commit.
- Exact Horizon Mixins and SMP revisions.
- Prepared resources transfer method.
- Java 26.2 compatibility path.
- Bedrock dependency versions and authentication.
- Final FRP client version/config.
- Maximum world archive size and fallback storage.
- Continuation cycle/billing budget.
- Native hook gaps for requested gameplay features.