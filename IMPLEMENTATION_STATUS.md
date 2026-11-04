# Horizon MC — Implementation Status

**State:** Runtime bootstrap and documentation follow-up merged into canonical `main` by PRs #1 and #2. Lifecycle timing correction is committed locally as `bd455ada2dbf6035da2f3812a0b718fd6a369025`; Telegram-only no-operator startup is committed locally as `91f6931` on `copilot/telegram-only-startup`. Push to both canonical and fork remotes failed because Git could not obtain a write credential; the canonical PR attempt failed because the head branch is not remote. No PR exists; these changes are not merged, CI-validated or live-tested.
**Latest merged canonical commit:** `a1c84bb418d55f26e52cf72b7f28b466adb2ad30`
**Latest previously CI-validated implementation commit:** `34fa293088e93b048a1e3dd024d1f9e8710978dd`
**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC  
**Default branch:** main  
**Current implementation branch:** `copilot/telegram-only-startup` (local checkpoint; canonical push could not authenticate; no PR)

## Implemented in the current PR

| Area | State | Evidence / next action |
|---|---|---|
| Horizon installer | CI_VALIDATED | Pinned v0.2.97 installer script; live install still needs runner test |
| FRP client | CI_VALIDATED | Pinned v0.71.1 Linux AMD64 archive and SHA-256 |
| Java TCP tunnel config | CI_VALIDATED | Generated FRPC TOML; test against owner's FRPS |
| Prepared 26.3 resources | PENDING_OWNER_CONFIRMATION | Owner reports setup complete; private release access has not been verified |
| Dedicated server startup | IMPLEMENTED_NOT_LIVE_TESTED | Manual Actions workflow; optional no-operator path requires Telegram configuration and has not run on Actions |
| Seed isolation | IMPLEMENTED | Initial seed 9064150133272194; branch world-data/survival-9064150133272194-26.3 |
| Hourly snapshot | CI_VALIDATED | ZIP CRC, SHA-256 manifest and dedicated branch; live server test pending |
| Current/previous rotation | CI_VALIDATED | Only verified current rotates to previous |
| Snapshot restore | CI_VALIDATED | Current then previous fallback; invalid snapshots fail closed; server lists/settings restored |
| Final shutdown save | IMPLEMENTED_PENDING_LIVE_TEST | Graceful stop at 325m, then CLI final backup and remote verification |
| Workflow timeout | IMPLEMENTED | 350 minutes (5h50m) |
| Lifecycle timing | TESTING | Elapsed time is measured in seconds; warnings at 300m/315m, shutdown at 325m, checkpoint cutoff at 270m; local tests pass, CI and live workflow validation pending |
| Telegram notifier | IMPLEMENTED_NOT_LIVE_TESTED | Uses existing token secret and alert chat ID |
| Telegram control bot | CI_VALIDATED | Numeric allowlists, no shell execution, stale-update filtering, manual-backup cutoff; current Actions configuration is not API-verified |
| Static/portable tests | TESTING | All eleven offline tests pass locally; Bash syntax and diff checks pass; CI on this branch is pending |
| FRP public endpoint | PENDING_LIVE_TEST | Owner reports FRP settings configured; endpoint and Actions settings are not verified |
| Bedrock UDP | NOT_IMPLEMENTED | Later Velocity/Geyser/Floodgate task |
| Java 26.2 client | BLOCKED_PENDING_RESEARCH | Protocol translation not established |
| Offline/cracked authentication | BLOCKED | Offline mode alone does not authenticate identities |
| Official SMP homes / TPA / claims | BLOCKED | Inspected SMP commit `ee1620f`; its compatibility metadata requires Horizon `48c63bc` and Mixins `d9c83d7`, which do not match the pinned Horizon `a3ac5bf` |
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

Previously validated implementation commit: `34fa293088e93b048a1e3dd024d1f9e8710978dd`.

- Push validation [run 41775625706](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775625706): success.
- Pull request validation [run 41775630663](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775630663): success.
- Python compileall: passed.
- Bash syntax checks: passed.
- Offline helper suite: all ten tests passed.

Current local lifecycle correction:
- `python3 -m unittest discover -s tests -p test_runtime_helpers.py -v`: all eleven tests passed, including no-operator and operator initialization argument checks.
- `bash -n scripts/run-session.sh scripts/initialize-server.sh`: passed.
- CI has not run on the local lifecycle or no-operator changes; no live Actions session has verified them.
- Official SMP compatibility metadata was read at source commit `ee1620f438c853b03ff2c568f4c4b1b443211294`; its declared Horizon/Mixins pins do not match this runtime, so reuse is blocked.
- Local FRP config generation passed; the token is stored in a mode-0600 file and the TOML uses file-based token auth. Values were not printed.
- The current GitHub integration cannot verify Actions secret names (403), and the Codespace token cannot access the private resource release (401). Resource release presence is therefore unverified; no live workflow was dispatched.
- The earlier canonical push of checkpoint `bd455ada2dbf6035da2f3812a0b718fd6a369025` was rejected with HTTP 403 for `Mr0007-AI`. Push of `copilot/telegram-only-startup` to both `upstream` and `origin` failed because Git could not obtain a password. The canonical PR attempt failed because the head ref is not present remotely; no PR exists.
- `gh auth status` reports no authenticated GitHub CLI account. Canonical Git fetch succeeds, but Git transport access alone cannot dispatch a GitHub Actions workflow.

Coverage includes prepared resource archive extraction and traversal rejection, required Horizon resource manifest, downloader variable expansion, FRP token separation, stale Telegram update filtering, snapshot identity/seed/level.dat validation, fail-closed restore, server settings/operator/whitelist restoration, snapshot rotation/remote verification and lifecycle timing.

The Minecraft runtime workflow is manual-dispatch only. Push events do not start a server.

No end-to-end test has yet proved:
- the prepared private resource archive is accepted by the pinned binary;
- the owner's frps accepts the pinned frpc config;
- a real Java client can join via the public FRP endpoint;
- a real world can be restored and final-saved on Actions.

## Required owner action

1. Verify the private resources-26.3 release, FRP settings, and Telegram bot token/numeric user allowlist in canonical repository Actions settings; owner reports the resource and FRP setup is complete, but access is unverified.
2. Obtain authorized Git write access to the fork, publish `copilot/telegram-only-startup`, and open its PR into canonical `main` before selecting the blank operator input.
3. Authenticate GitHub CLI to dispatch from this Codespace, or run the workflow manually from the GitHub Actions UI after the change is merged.
4. Test the public Java 26.3 endpoint and final snapshot before inviting players.

See [Codespaces setup](docs/SETUP-CODESPACES.md).

## Next implementation tasks

1. Obtain authorized Git write access to the fork, push `copilot/telegram-only-startup`, open a PR into canonical `main`, and run CI.
2. Verify the private resource release and required FRP/Telegram Actions settings.
3. Dispatch a controlled first session and verify the endpoint from a real Java 26.3 client.
4. Test shutdown save, second-run restore and operator/whitelist persistence.
5. Resolve a Horizon/Mixins/SMP revision set whose compatibility metadata matches, then build and test official SMP before implementing remaining gameplay features.