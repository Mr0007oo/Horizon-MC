# Horizon MC — Current Handoff

## Current phase
Phase 1 — Runtime bootstrap and documentation follow-up merged into canonical `main` by PRs #1 and #2. A lifecycle timing fix is locally tested; owner setup and live smoke test remain.

## Completed in this branch
- Updated lifecycle requirement to first warning at 5h00m, second warning at 5h15m, graceful shutdown at 5h25m and job hard timeout at 5h50m.
- Recorded the owner-supplied seed 9064150133272194 and initial world identity.
- Added manual Actions workflow, pinned Horizon and FRP installers, resource archive fetcher and checksum validation.
- Added Java TCP FRP config generator for 25565 through FRPS control port 7000.
- Added current/previous world snapshot store on a dedicated world-data branch.
- Added final shutdown snapshot verification, serialization with the checkpoint lock and a manual-stop marker.
- Added Telegram notifier and allowlisted command bot with stale-update filtering and a manual-backup cutoff near shutdown.
- Added static validation workflow and offline helper tests.
- Added Codespaces setup, architecture and upstream dependency pins.
- Corrected lifecycle comparisons to use seconds (the unit produced by `date +%s`): 5h00 warning, 5h15 warning, 5h25 shutdown, and no new hourly checkpoint after 4h30.

## Working features
The workflow and scripts are implemented but not live-verified. Do not call the server production-ready.

## Tests
Offline tests are present in tests/test_runtime_helpers.py. Validation runs on every PR update. The latest previously CI-validated implementation commit is `34fa293088e93b048a1e3dd024d1f9e8710978dd`; push validation [41775625706](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775625706) and PR validation [41775630663](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775630663) passed Python compileall, Bash syntax checks and all ten offline tests.

On the current local lifecycle fix, all ten offline tests and `bash -n scripts/run-session.sh` pass. CI has not run on this change. The fix addresses a real seconds/minutes mismatch that would otherwise have triggered maintenance after about five minutes and prevented hourly checkpoints.

The official SMP source was inspected at `ee1620f438c853b03ff2c568f4c4b1b443211294`; its compatibility metadata requires Horizon `48c63bc09d9acc82f2074e75ae59720514796a9d` and Mixins `d9c83d7096b7ea5b83678da2efdfd6161f74997e`. The pinned runtime Horizon revision differs, so SMP reuse and those gameplay features remain blocked until a matching revision set is selected and tested.

The Codespace reports nonempty FRP and Telegram inputs. Local FRP config generation passed with file-based token auth and mode-0600 token storage. GitHub API checks could not verify Actions secrets (403) or access the private `resources-26.3` release (401); its presence is unverified, and no live workflow was dispatched.

No actual FRP connection, Java client session, or live server backup/restore has been tested yet.

## Latest checkpoint
- Current canonical base: `a1c84bb418d55f26e52cf72b7f28b466adb2ad30`
- Original implementation PR #1: https://github.com/Mr0007oo/Horizon-MC/pull/1 (merged)
- Documentation follow-up PR #2: https://github.com/Mr0007oo/Horizon-MC/pull/2 (merged)
- Latest validated implementation commit: `34fa293088e93b048a1e3dd024d1f9e8710978dd`.

## Pinned revisions
- Horizon v0.2.97 — a3acb5f0d2f59d2d5ff21a5aa000809ba1e35e2f
- FRP v0.71.1 — Linux AMD64 SHA-256 recorded in docs/UPSTREAM-PINS.md

## World details
- World: survival
- Seed: 9064150133272194
- Version: 26.3
- Branch: world-data/survival-9064150133272194-26.3

## Timing
- Warning: 5h00m
- Warning: 5h15m
- Graceful shutdown: 5h25m
- Hard workflow timeout: 5h50m
- Hourly checkpoints at 1h, 2h, 3h and 4h elapsed; do not start a new one after 4h30m.
- No automatic continuation

## Owner setup blockers
1. Prepare and upload the private Minecraft 26.3 resource release and SHA-256 sidecar.
2. Configure `FRP_SERVER_ADDR` and `FRP_AUTH_TOKEN`.
3. Configure Telegram numeric allowlists and alert chat ID if bot control is wanted.
4. PRs #1 and #2 are merged.
5. Perform a controlled first Java 26.3 connection and world persistence test.

## Current working branch
`copilot/fix-lifecycle-seconds` (based on canonical `main`; PR pending)

## Exact next task
Push this tested feature branch and open a PR against canonical `main`; address its CI results. The next runtime gate requires the owner to upload the private `resources-26.3` release and configure FRP Actions variables/secrets; then perform the controlled Java 26.3 connection and persistence test. Gameplay work must wait until a Horizon/Mixins/SMP revision set is mutually compatible and the documented native-mod APIs are verified.