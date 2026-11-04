# Horizon MC — Implementation Status

**State:** Initial runtime bootstrap merged into `main` by PR #1; CI validation passed; owner setup and live smoke test remain.
**Latest validated implementation commit:** `34fa293088e93b048a1e3dd024d1f9e8710978dd`  
**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC  
**Default branch:** main  
**Current implementation branch:** main (bootstrap merged by PR #1)

## Implemented in the current PR

| Area | State | Evidence / next action |
|---|---|---|
| Horizon installer | CI_VALIDATED | Pinned v0.2.97 installer script; live install still needs runner test |
| FRP client | CI_VALIDATED | Pinned v0.71.1 Linux AMD64 archive and SHA-256 |
| Java TCP tunnel config | CI_VALIDATED | Generated FRPC TOML; test against owner's FRPS |
| Prepared 26.3 resources | BLOCKED_ON_OWNER | Upload private resources-26.3 release with archive and checksum |
| Dedicated server startup | IMPLEMENTED_NOT_LIVE_TESTED | Manual Actions workflow and Horizon CLI init/start |
| Seed isolation | IMPLEMENTED | Initial seed 9064150133272194; branch world-data/survival-9064150133272194-26.3 |
| Hourly snapshot | CI_VALIDATED | ZIP CRC, SHA-256 manifest and dedicated branch; live server test pending |
| Current/previous rotation | CI_VALIDATED | Only verified current rotates to previous |
| Snapshot restore | CI_VALIDATED | Current then previous fallback; invalid snapshots fail closed; server lists/settings restored |
| Final shutdown save | IMPLEMENTED_PENDING_LIVE_TEST | Graceful stop at 325m, then CLI final backup and remote verification |
| Workflow timeout | IMPLEMENTED | 350 minutes (5h50m) |
| Lifecycle warnings | CI_VALIDATED | 300m and 315m; shutdown starts at 325m; 5-second polling |
| Telegram notifier | IMPLEMENTED_NOT_LIVE_TESTED | Uses existing token secret and alert chat ID |
| Telegram control bot | CI_VALIDATED | Numeric allowlists, no shell execution, stale-update filtering, manual-backup cutoff |
| Static/portable tests | PASS | Python compileall, Bash syntax and all ten offline tests pass on latest validated commit |
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
- Hourly checkpoints at 1h, 2h, 3h and 4h elapsed; no new one starts after 4h30m.
- Automatic continuation: disabled.

Do not drift back to 5h40m shutdown or use the full six-hour window.

## Verification log

Latest validated implementation commit: `34fa293088e93b048a1e3dd024d1f9e8710978dd`.

- Push validation [run 41775625706](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775625706): success.
- Pull request validation [run 41775630663](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775630663): success.
- Python compileall: passed.
- Bash syntax checks: passed.
- Offline helper suite: all ten tests passed.

Coverage includes prepared resource archive extraction and traversal rejection, required Horizon resource manifest, downloader variable expansion, FRP token separation, stale Telegram update filtering, snapshot identity/seed/level.dat validation, fail-closed restore, server settings/operator/whitelist restoration, snapshot rotation/remote verification and lifecycle timing.

The Minecraft runtime workflow is manual-dispatch only. Push events do not start a server.

No end-to-end test has yet proved:
- the prepared private resource archive is accepted by the pinned binary;
- the owner's frps accepts the pinned frpc config;
- a real Java client can join via the public FRP endpoint;
- a real world can be restored and final-saved on Actions.

## Required owner action

1. Add the private release tag resources-26.3 with the prepared resources archive and its .sha256 asset.
2. Set FRP_SERVER_ADDR variable and FRP_AUTH_TOKEN secret.
3. Keep TELEGRAM_BOT_TOKEN secret and add numeric Telegram allowlists/alert chat ID if using bot control.
4. Review and merge PR #1 when ready, then execute one controlled first session.

See [Codespaces setup](docs/SETUP-CODESPACES.md).

## Next implementation tasks

1. Complete the private resource release and Actions variables/secrets.
2. Run a controlled first session and verify the endpoint from a real Java 26.3 client.
3. Test shutdown save, second-run restore and operator/whitelist persistence.
4. Then implement compatible official SMP native modules and the requested missing features.