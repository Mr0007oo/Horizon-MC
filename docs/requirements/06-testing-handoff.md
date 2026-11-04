# 06 — Testing, Quality Gates and Agent Handoff

## Research gate

Before runtime implementation, inspect and pin:
- Horizon source and release.
- horizon-server executable and help.
- server.toml template and control API.
- Horizon backup and restore behavior.
- Native hook catalog and native mod API.
- Horizon Mixins revision.
- Official SMP compatibility metadata and source.
- FRP client/server versions and config syntax.
- Velocity, Geyser and Floodgate exact versions.
- 26.2 protocol translation feasibility.
- Offline-mode identity/authentication design.

Write docs/ARCHITECTURE.md and update DECISIONS.md and IMPLEMENTATION_STATUS.md.

## Build gate

Verify every build command against the pinned source revision. Use upstream formatting, compilation, clippy, native-mod checks and test tooling where applicable. Build the dedicated engine with custom native mods using the documented process. Do not invent scripts or use undocumented command-line options.

## Unit tests

Cover:
- Command registration and aliases.
- Permission evaluation.
- Player identity.
- Home and waypoint storage.
- Teleport request expiry/cooldown.
- Claims and trusted players.
- Block permission checks.
- Vein Miner bounded traversal.
- Inventory transactions.
- Duel lifecycle.
- Schematic parsing/limits.
- Snapshot manifest/checksum validation.
- Telegram authorization and input validation.

## Integration tests

Cover:
- Horizon initialization and startup.
- Correct prepared game-resource discovery.
- FRPC connection and separate TCP/UDP routes.
- Proxy startup and backend forwarding.
- Java connection.
- Bedrock connection when enabled.
- Telegram polling and admin commands.
- Hourly backup.
- Graceful shutdown and final backup.
- Git snapshot push and remote verification.
- Restore and next-session startup.

## Combined feature tests

Test claims + Vein Miner; claims + schematic; homes + waypoints; TPA + duels; Ender Chest + disconnect; all gameplay data + restart/restore. A module is not VERIFIED if it works alone but breaks another module.

## Lifecycle simulation

Do not use a full 6-hour real workflow as the first lifecycle test. Add a test-only clock/interval configuration so the 300m warning, 315m warning, 325m shutdown, retry/backoff, failed push, invalid archive, manual stop, cancellation, duplicate dispatch and budget-exceeded paths can be simulated quickly. Test mode must be impossible to enable accidentally in production.

## IMPLEMENTATION_STATUS.md

Use statuses:
- NOT_STARTED
- RESEARCHING
- IN_PROGRESS
- TESTING
- VERIFIED
- BLOCKED
- FAILED

For each VERIFIED feature, link to exact proof/test output or commit. Record upstream revisions, runtime artifact, last successful build/tests, known limitations and remaining blockers.

## Handoff command

When the user invokes /hand-off, stop expanding unrelated features and follow .github/prompts/hand-off.prompt.md.

The handoff must:
1. Inspect git status, all diffs, untracked files, current branch and remotes.
2. Preserve user and agent changes.
3. Exclude credentials, environment files, generated assets, world archives and runtime data.
4. Run appropriate formatters/tests and document failures or skipped tests.
5. Update IMPLEMENTATION_STATUS.md and HANDOFF.md.
6. Fetch canonical https://github.com/Mr0007oo/Horizon-MC and its main branch.
7. Make the checkpoint branch from current canonical main, then bring over intended safe project changes.
8. Resolve only clear conflicts while preserving both valid sides.
9. Push the feature branch to the canonical repository using the workspace's authorized Git credentials.
10. Verify remote branch SHA.
11. Open a pull request with base Mr0007oo/Horizon-MC:main.
12. Verify the PR URL and update HANDOFF.md.

## Authentication and repository mismatch

A GitHub CLI auth error is not proof Git transport cannot authenticate. Inspect git remote -v and the Codespaces/workspace credential helper, then test fetch using that existing authentication. Do not reveal credentials or put tokens in remote URLs.

If the checkout is a fork or another repository, keep that remote intact and add/use the canonical target remote. Fetch canonical main, base the handoff branch on it, bring across intended changes, test, push branch to canonical and open PR to canonical main.

Do not push straight to main. Here "push to the main repo" means push the feature branch to the canonical repository, then PR into its main branch.

If the CLI and Git transport are both unauthorized, stop and report the permission blocker. Never bypass access controls, search for tokens or claim a push succeeded. Local checkout does not prove a remote push; fetch/inspect the remote branch after pushing.

## Conflict rules

Resolve obvious additive conflicts when intent is clear. Never discard project data, world data, tests, config or other agent work merely to make a clean merge. Never force-push main or rewrite another agent's branch. If a conflict is ambiguous, save a local checkpoint, document it and do not claim the PR is complete.

## PR requirements

Create an open PR, do not merge automatically. Include summary, changes, test results, skipped tests, known limitations, blockers and next recommended task.

## Handoff state

HANDOFF.md must record current phase, completed tasks, working features, passing/failing tests, changed files, pinned revisions, remaining tasks, blockers, exact next task, last checkpoint SHA, branch and PR URL.

Preserving completed work is more important than starting another feature.