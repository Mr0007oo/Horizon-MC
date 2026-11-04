# 01 — Hosting Lifecycle and Session Rotation

## Objective

Run Horizon in bounded GitHub Actions sessions. Notify players, checkpoint the world, gracefully stop the dedicated server and optionally dispatch a successor run only after persistence is verified.

## Timing

Measure elapsed time from the start of the Actions job, not from when the Minecraft server becomes ready. This includes bootstrap and restoration time.

Default project timeline:

| Job elapsed time | Action |
|---|---|
| 0m | Validate workflow inputs, secrets, concurrency and runner |
| 0–10m | Restore data, prepare runtime, start Horizon and network |
| Every 60m | Create a consistent backup and sync a checkpoint |
| 320m / 5h20m | First in-game and Telegram warning |
| 330m / 5h30m | Second warning |
| 340m / 5h40m | Begin graceful shutdown |
| 340–352m | Stop Horizon, create final backup, verify and push |
| Before 355m | Finish workflow with timeout margin |

The proposed workflow job timeout is 355 minutes, subject to verification against the current applicable GitHub runner/job limits. Do not assume this value is universally available. If a platform limit, queue delay or bootstrap duration makes the schedule unsafe, adjust the plan and document the decision. Never intentionally approach a hard timeout without a shutdown margin.

## Player messages

At 320 minutes:

Server notice: Scheduled maintenance is approaching. The server will restart in approximately 20 minutes. Your world progress is checkpointed automatically.

At 330 minutes:

Server notice: 10 minutes until scheduled maintenance. Please finish your activities and return to a safe location.

At shutdown:

Server notice: The server is saving its world and restarting. The latest verified progress will be restored on the next session.

Send the same operational notices to Telegram administrators. Use Horizon's documented command interface, for example the verified horizon-server cmd say command for the pinned release. Do not invent console APIs or use an OS shell to inject game chat.

## Hourly checkpoint

Create scripts/checkpoint.sh. It must:

1. Confirm Horizon and the supervisor are healthy.
2. Request a consistent backup using the documented Horizon backup command/API for the pinned release.
3. Wait for the operation to finish.
4. Verify archive integrity.
5. Calculate SHA-256.
6. Generate a schema-versioned manifest with world ID, sequence, timestamps, engine/mod revisions, checksum and clean_shutdown=false.
7. Fetch and validate the existing world-data branch.
8. Update current/previous snapshots atomically using a concurrency-safe expected branch head.
9. Push to the world-data branch only.
10. Fetch again and verify the remote manifest and checksum.
11. Notify Telegram of success or failure.

Horizon documents horizon-server backup and horizon-server backups; verify exact output and options against the pinned binary. Never invent a save-all command.

## Graceful shutdown

Create scripts/shutdown.sh.

At 340 minutes:
1. Notify players and Telegram.
2. Stop accepting new administrative operations.
3. Ask the documented Horizon supervisor to stop gracefully.
4. Wait for the game process to exit and confirm with the documented status command.
5. Create the final backup using the correct sequence established by integration tests.
6. Generate and validate the final manifest with clean_shutdown=true only after clean termination is proven.
7. Sync the final snapshot to the world-data branch.
8. Fetch the branch and verify the exact commit and checksum.
9. Release locks and finish the job.

Do not assume that backup after stop works without testing; determine the correct supported sequence from the pinned Horizon release. Do not use immediate SIGKILL as normal shutdown behavior.

## Failure policy

If Horizon does not stop, preserve logs, continue waiting only within the grace period, and use documented supervisor stop behavior. Do not report a clean shutdown unless verified.

If the backup or push fails:
- Preserve the last known-good remote snapshot.
- Retry transient failures with bounded backoff.
- Never replace a good snapshot with an invalid one.
- Notify Telegram.
- Mark persistence failed.
- Do not auto-dispatch a successor.

If the runner terminates unexpectedly, restore the latest verified remote checkpoint on the next run. Work since the last successful hourly checkpoint may be lost; do not promise zero data loss.

## Controlled continuation

Default ENABLE_AUTO_CONTINUATION=false.

Suggested controls:
- ENABLE_AUTO_CONTINUATION
- MAX_CYCLES_PER_DAY
- MONTHLY_RUNNER_MINUTES_BUDGET
- CONTINUATION_COUNT
- MANUAL_STOP_REQUESTED

A successor is allowed only if the previous Horizon process is confirmed stopped, final snapshot validates and is remotely committed, no manual stop/cancellation/critical error exists, the configured budget remains, and current GitHub platform/usage limits permit the run.

Dispatch exactly one successor using the official workflow dispatch mechanism and a least-privilege token with only the required Actions permission. Pass non-secret identifiers only. Use durable run IDs and a single concurrency group to prevent overlap. The successor independently restores and verifies the latest snapshot before launching. If the Actions token cannot dispatch another workflow, report the blocker; do not try to evade restrictions.

This does not guarantee 24/7 uptime. A 30-day month of uninterrupted execution requires 43,200 runner-minutes before overhead. Quotas, billing, queueing, maintenance and platform restrictions remain applicable.

## Concurrency and health

Use one server concurrency group, such as horizon-minecraft-runtime, with cancellation disabled for an active server session. Reject or safely queue duplicate launches. Never run two Horizon processes against the same world.

Monitor status, TPS, MSPT, player count, RAM, CPU, disk, FRP tunnel, backup outcome and process state. Parse actual output from the pinned Horizon version; do not assume undocumented JSON fields.

## Acceptance tests

- Simulated clock verifies 320m and 330m notifications.
- Simulated clock verifies graceful stop at 340m.
- Successful final snapshot verifies remotely.
- Failed backup and failed push prevent continuation.
- Manual stop prevents continuation.
- Cancellation and duplicate dispatch do not create two servers.
- The workflow exits before its hard timeout.
- Recovery restores the last verified snapshot.