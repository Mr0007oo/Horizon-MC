# Horizon MC — Current Handoff

## Current phase
Phase 1 — Runtime bootstrap and documentation follow-up merged into canonical `main` by PRs #1 and #2. Lifecycle fix is locally tested and committed as `bd455ada2dbf6035da2f3812a0b718fd6a369025`; Telegram-only no-operator startup changes are implemented locally but uncommitted. Canonical push was previously denied (HTTP 403), so no PR exists.

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
- Added an optional no-operator startup path: keeps the whitelist enabled and empty, grants no player operator privileges, and requires Telegram token plus numeric user allowlist.

## Working features
The workflow and scripts are implemented but not live-verified. Do not call the server production-ready.

## Tests
Offline tests are present in tests/test_runtime_helpers.py. Validation runs on every PR update. The latest previously CI-validated implementation commit is `34fa293088e93b048a1e3dd024d1f9e8710978dd`; push validation [41775625706](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775625706) and PR validation [41775630663](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775630663) passed Python compileall, Bash syntax checks and all ten offline tests.

On the current local lifecycle and no-operator changes, all eleven offline tests pass; `bash -n scripts/run-session.sh scripts/initialize-server.sh` and `git diff --check` pass. CI has not run on these changes.

The official SMP source was inspected at `ee1620f438c853b03ff2c568f4c4b1b443211294`; its compatibility metadata requires Horizon `48c63bc09d9acc82f2074e75ae59720514796a9d` and Mixins `d9c83d7096b7ea5b83678da2efdfd6161f74997e`. The pinned runtime Horizon revision differs, so SMP reuse and those gameplay features remain blocked until a matching revision set is selected and tested.

The owner reports the resource release and FRP settings are configured; their availability has not been verified through GitHub. `gh auth status` reports no authenticated account. Canonical Git fetch works, but Git access alone cannot dispatch the Actions workflow, and no live workflow was dispatched.

No actual FRP connection, Java client session, or live server backup/restore has been tested yet.

## Latest checkpoint
- Current canonical base: `a1c84bb418d55f26e52cf72b7f28b466adb2ad30`
- Local checkpoint: `bd455ada2dbf6035da2f3812a0b718fd6a369025` on `copilot/fix-lifecycle-seconds`; push to canonical `upstream` was rejected with HTTP 403. The remote branch was verified absent; no PR was opened.
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
1. Verify the private resource release, FRP settings, and Telegram token/numeric user allowlist in canonical Actions settings; the owner reports resource and FRP setup is complete, but access is unverified.
2. Publish and merge the no-operator workflow changes before selecting a blank operator input.
3. Authenticate GitHub CLI in the Codespace or launch from the Actions UI after merge.
4. Perform a controlled first Java 26.3 connection and world persistence test.

## Current working branch
`copilot/fix-lifecycle-seconds` (local checkpoint based on canonical `main`, with uncommitted no-operator changes; canonical push previously denied; no PR)

## Exact next task
Obtain authorized write/API access to canonical `Mr0007oo/Horizon-MC`, publish the lifecycle and no-operator changes on a feature branch, open a PR against `main`, and address CI results. Then verify the private resource release and FRP/Telegram Actions settings, dispatch the workflow, and test a Java 26.3 connection and persistence. Gameplay work must wait until a Horizon/Mixins/SMP revision set is mutually compatible and the documented native-mod APIs are verified.