# Horizon MC — Current Handoff

## Current phase
Phase 1 — Initial runtime bootstrap implemented; latest push and pull-request validation passed; owner setup and live smoke test remain.

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

## Working features
The workflow and scripts are implemented but not live-verified. Do not call the server production-ready.

## Tests
Offline tests are present in tests/test_runtime_helpers.py. Validation is run on every PR update. The latest validated commit is `1ac38fe833886d3318ad4c4c36e735a5ee87dee2`. Push validation [41775433347](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775433347) and PR validation [41775439286](https://github.com/Mr0007oo/Horizon-MC/actions/runs/41775439286) both passed Python compileall, Bash syntax checks and all ten offline tests.

No actual FRP connection, Java client session, or live server backup/restore has been tested yet.

## Latest checkpoint
- Commit: `1ac38fe833886d3318ad4c4c36e735a5ee87dee2`
- PR #1: https://github.com/Mr0007oo/Horizon-MC/pull/1
- Base branch: `main`
- PR remains open and unmerged.

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
4. Review and merge PR #1 when ready.
5. Perform a controlled first Java 26.3 connection and world persistence test.

## Exact next task
Complete the private resource release and Actions variables/secrets using `docs/SETUP-CODESPACES.md`. Then run a controlled Java 26.3 session with no important player data, verify the public FRP endpoint from a real client, and test the next-run restore.

## Handoff branch
copilot/initial-runtime-bootstrap

## Pull request
https://github.com/Mr0007oo/Horizon-MC/pull/1