# 01 — Hosting Lifecycle and Session Rotation

## Objective

Run Horizon in one bounded GitHub Actions session. Warn players, checkpoint data, gracefully stop the dedicated server and verify the final world snapshot before the job ends.

## Hard timing policy

Measure elapsed time from the very first workflow step, before checkout, installation or server startup:

| Job elapsed time | Action |
|---|---|
| 0m | Capture start epoch and validate inputs |
| 0–10m (target only) | Checkout, install pinned tools, restore data and start service |
| 60m, 120m, 180m, 240m | Hourly consistent world checkpoint; no new checkpoint starts after 4h30m |
| 300m / 5h00m | First player and Telegram warning |
| 315m / 5h15m | Second player and Telegram warning |
| 325m / 5h25m | Stop new play and begin graceful shutdown immediately |
| 325–340m | Stop Horizon, create final snapshot, verify and push |
| 350m / 5h50m | Job hard timeout; retain at least a 10-minute margin before a six-hour boundary |

**Never wait until 5h40m. Never target the full six-hour window.** The workflow job timeout is set to 350 minutes. Graceful shutdown must begin at elapsed 325 minutes, regardless of when Horizon finished booting.

The controller checks the elapsed time every five seconds. The stop can therefore begin slightly after the 325-minute check boundary, but it must not be scheduled later than 325 minutes intentionally. The job timeout remains a final failsafe, not the normal shutdown path.

## Player messages

At 300 minutes:

Scheduled maintenance begins in 25 minutes. Please finish activities and return to a safe location.

At 315 minutes:

Scheduled maintenance begins in 10 minutes. The server will save and stop at 5h25.

At 325 minutes:

Server saving and stopping now. Your world progress is being checkpointed.

Send administrative notifications to Telegram if its token and alert chat ID are configured. Player chat warnings use the documented horizon-server cmd say interface.

## Startup and world restore

1. Validate that the EULA input was explicitly accepted.
2. Validate the world seed and, when provided, the operator username. If no operator is requested, require the Telegram bot token and numeric user allowlist before startup.
3. Install the pinned Horizon release and FRP binary.
4. Fetch owner-prepared Minecraft 26.3 resources from the private repository release and verify SHA-256.
5. Initialize the dedicated server only when server.toml is absent.
6. Initialize/fetch the world-data/<world-id> branch.
7. Restore the latest verified current snapshot; use previous only if current fails validation.
8. Bind the Horizon Java listener to loopback.
9. Start Horizon and confirm status --json reports phase=running.
10. Start FRPC and ensure its process remains alive.

Never initialize a new world over a damaged or unverified existing snapshot.

## Hourly checkpoint

scripts/checkpoint.sh performs a serialized checkpoint:

1. Acquire a nonblocking flock lock.
2. Ask Horizon for a named backup using the supported horizon-server backup session command.
3. Verify that the expected ZIP exists and passes CRC validation.
4. Compute SHA-256 and write a schema-versioned manifest.
5. Enforce the configured archive and world-branch history size caps.
6. Rotate only a previously verified current snapshot to previous.
7. Commit the current/previous snapshots to the dedicated world-data branch.
8. Push and verify the remote branch head.
9. Notify Telegram of success or failure.

The project intentionally refuses to exceed its conservative Git snapshot storage budget. A failed checkpoint preserves the last good remote snapshot and must not trigger automatic continuation.

## Graceful shutdown at 5h25

The controller's EXIT handler must:

1. Broadcast the stop message.
2. Ask Horizon's supervisor to stop gracefully using horizon-server stop.
3. Confirm horizon-server status --json reports phase=stopped.
4. Only after that confirmation, run horizon-server backup session through the supported CLI and create the final snapshot with clean_shutdown=true.
5. Verify the final archive CRC, SHA-256 manifest and remote world-data branch head.
6. Stop FRPC and Telegram processes.
7. Remove the temporary Git worktree.
8. Return a failing workflow status if the final save/push failed or shutdown could not be verified.

Horizon's backup implementation supports creating a backup from the server directory when no running control API is present. This stop-then-backup sequence is chosen so the final filesystem archive cannot race live world writes. The first Codespaces/Actions smoke test must prove this behavior against the pinned binary before the workflow is used for a real shared world.

Never mark clean_shutdown=true unless the process has confirmed the stopped phase. Do not use SIGKILL as normal shutdown behavior.

## Manual stop

Telegram /stop writes a manual-stop marker. The session controller then follows the same graceful stop and final snapshot path. It must not dispatch or launch another session automatically.

## Failure policy

If Horizon stops unexpectedly, FRPC exits, or the server reports a phase other than running:
- Notify Telegram when possible.
- Preserve logs.
- Attempt only the normal graceful shutdown path.
- Do not claim the final snapshot is clean unless verified.
- Do not discard the last verified remote snapshot.

If backup or push fails:
- Preserve the previous valid remote snapshot.
- Report failure.
- Fail the workflow.
- Do not start a successor session.

If the runner is terminated unexpectedly, the next manual run restores the last verified checkpoint. Changes made since that checkpoint may be lost.

## Automatic continuation

Automatic continuation is **not implemented and disabled**. Do not dispatch a successor run in the current bootstrap. Any future continuation feature must be separately designed, budget-limited, tested for overlap and compliant with current GitHub usage restrictions.

A 30-day month of uninterrupted sessions requires 43,200 runner-minutes before setup overhead. GitHub Actions is not guaranteed permanent hosting.

## Acceptance tests

- Test clock confirms warning at 300m and 315m.
- Test clock confirms shutdown begins at 325m, never intentionally at 340m or six hours.
- Job hard timeout is 350 minutes.
- Failed startup is not treated as a running server.
- Failed backup/push does not overwrite the last verified remote snapshot.
- A clean final snapshot is only marked after Horizon reports stopped.
- Manual stop follows the same final snapshot path.
- Duplicate checkpoint requests do not run simultaneously.
- The next manual run restores the most recent verified world snapshot.