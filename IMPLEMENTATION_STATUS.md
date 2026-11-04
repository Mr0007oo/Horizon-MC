# Horizon MC — Implementation Status

**State:** Initial runtime bootstrap implemented; CI validation is being rerun after resource-manifest and fail-closed restore changes; first live smoke test remains.  
**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC  
**Default branch:** main  
**Current implementation branch:** copilot/initial-runtime-bootstrap

## Implemented in the current PR

| Area | State | Evidence / next action |
|---|---|---|
| Horizon installer | IMPLEMENTED | Pinned v0.2.97 installer script; verify in Actions |
| FRP client | IMPLEMENTED | Pinned v0.71.1 Linux AMD64, SHA-256 verified |
| Java TCP tunnel config | IMPLEMENTED | Generated FRPC TOML; test against owner's FRPS |
| Prepared 26.3 resources | BLOCKED_ON_OWNER | Upload private resources-26.3 release with archive and checksum |
| Dedicated server startup | IMPLEMENTED_NOT_LIVE_TESTED | Manual Actions workflow and Horizon CLI init/start |
| Seed isolation | IMPLEMENTED | Initial seed 9064150133272194; branch world-data/survival-9064150133272194-26.3 |
| Hourly snapshot | IMPLEMENTED_PENDING_CI | ZIP CRC, SHA-256 manifest and dedicated branch |
| Current/previous rotation | IMPLEMENTED_PENDING_CI | Only verified current rotates to previous |
| Snapshot restore | IMPLEMENTED_PENDING_CI | Current then previous checksum fallback |
| Final shutdown save | IMPLEMENTED_PENDING_LIVE_TEST | Graceful stop at 325m, then CLI final backup and remote verification |
| Workflow timeout | IMPLEMENTED | 350 minutes (5h50m) |
| Lifecycle warnings | IMPLEMENTED_PENDING_TEST | 300m and 315m; shutdown starts at 325m |
| Telegram notifier | IMPLEMENTED_NOT_LIVE_TESTED | Uses existing token secret and alert chat ID |
| Telegram control bot | IMPLEMENTED_PENDING_TEST | Numeric user/chat allowlists and no shell execution |
| Static/portable tests | PASSING_ON_PRIOR_CHECKPOINT | Previous PR run passed compileall, Bash syntax and all offline tests; latest resource/restore regression run must be checked |
| FRP public endpoint | PENDING_LIVE_TEST | Requires FRP_SERVER_ADDR and FRP_AUTH_TOKEN |
| Bedrock UDP | NOT_IMPLEMENTED | Later Velocity/Geyser/Floodgate task |
| Java 26.2 client | BLOCKED_PENDING_RESEARCH | Protocol translation not established |
| Offline/cracked authentication | BLOCKED | Offline mode alone does not authenticate identities |
| Homes / TPA / claims | RESEARCHING | Verify official SMP compatibility and build integration |
| Personal waypoints | NOT_STARTED | Custom native mod needed |
| Vein Miner | NOT_STARTED | Custom native mod needed |
| Self-service /ec | NOT_STARTED | Custom native mod needed; distinct from /endersee |
| PvP duels | NOT_STARTED | Custom native mod needed |
| Schematic import | BLOCKED_PENDING_RESEARCH | Parser format and server mutation hooks need verification |
| Combined gameplay regression | NOT_STARTED | Required before gameplay features are VERIFIED |

## Pinned upstream revisions

- Horizon release: v0.2.97
- Horizon commit: a3acb5f0d2f59d2d5ff21a5aa000809ba1e35e2f
- Minecraft target: Java Edition 26.3
- FRP release: v0.71.1
- FRP Linux AMD64 SHA-256: 1d9875210972a5d1a62b2dc4c48df45ab0af05d3ca1b5e494a014428259df803
- See [UPSTREAM-PINS.md](docs/UPSTREAM-PINS.md).

## World identity

- World: survival
- Seed: 9064150133272194
- Version: 26.3
- Snapshot branch: world-data/survival-9064150133272194-26.3

## Lifecycle policy

- 5h00m: first warning.
- 5h15m: second warning.
- 5h25m: graceful shutdown begins.
- 5h50m: hard workflow timeout.
- Automatic continuation: disabled.

Do not drift back to 5h40m shutdown or use the full six-hour window.

## Verification log

The bootstrap contains offline tests for complete Horizon resource extraction, archive path safety, FRP secret separation, invalid-snapshot fail-closed behavior, server-list restore, world snapshot branch rotation and timer thresholds. PR validation run 41773567179 passed compileall, Bash syntax and all five offline tests before the final 5h25 late-checkpoint guard. A fresh run is pending for the latest commit.

No end-to-end test has yet proved:
- the prepared private resource archive is accepted by the pinned binary;
- the owner's frps accepts the pinned frpc config;
- a real Java client can join via the public FRP endpoint;
- a real world can be restored and final-saved on Actions.

## Required owner action

1. Add the private release tag resources-26.3 with the prepared resources archive and its .sha256 asset.
2. Set FRP_SERVER_ADDR variable and FRP_AUTH_TOKEN secret.
3. Keep TELEGRAM_BOT_TOKEN secret and add numeric Telegram allowlists/alert chat ID if using bot control.
4. Merge PR after the latest validation run succeeds, then execute one controlled first session.

See [Codespaces setup](docs/SETUP-CODESPACES.md).

## Next implementation tasks

1. Review CI and fix any failures before merge.
2. Validate prepared resource upload and first server boot.
3. Test FRP tunnel from a real Minecraft Java 26.3 client.
4. Test world backup, second-run restore and final save.
5. Then implement compatible official SMP native modules and requested missing features.