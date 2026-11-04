# Horizon MC — Current Handoff

## Current phase
Phase 1 — Initial runtime bootstrap implemented; CI is passing on the last completed validation run; owner setup and live smoke test remain.

## Completed in this branch
- Updated lifecycle requirement to first warning at 5h00m, second warning at 5h15m, graceful shutdown at 5h25m and job hard timeout at 5h50m.
- Recorded the owner-supplied seed 9064150133272194 and initial world identity.
- Added manual Actions workflow, pinned Horizon and FRP installers, resource archive fetcher and checksum validation.
- Added Java TCP FRP config generator for 25565 through FRPS control port 7000.
- Added current/previous world snapshot store on a dedicated world-data branch.
- Added final shutdown snapshot verification and manual-stop marker.
- Added Telegram notifier and allowlisted command bot.
- Added static validation workflow and offline helper tests.
- Added Codespaces setup, architecture and upstream dependency pins.

## Working features
The workflow and scripts are implemented but not live-verified. Do not call the server production-ready.

## Tests
Offline tests are present in tests/test_runtime_helpers.py. Validation is run on every PR update. The current branch includes new resource-manifest, fail-closed restore and serialized final-save checks; confirm the latest CI result before merge.

No actual FRP connection, Java client session, or live server backup/restore has been tested yet.

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
- No automatic continuation

## Owner setup blockers
1. Upload the private prepared Minecraft 26.3 resource release and checksum.
2. Configure FRP_SERVER_ADDR and FRP_AUTH_TOKEN.
3. Configure Telegram numeric allowlists and alert chat ID if bot control is wanted.
4. Merge PR and inspect validation workflow.
5. Perform a controlled first Java 26.3 connection and world persistence test.

## Exact next task
Review the latest CI result, complete docs/SETUP-CODESPACES.md, upload the private prepared-resource release and run a controlled smoke test with no important player data.

## Handoff branch
copilot/initial-runtime-bootstrap

## Pull request
https://github.com/Mr0007oo/Horizon-MC/pull/1