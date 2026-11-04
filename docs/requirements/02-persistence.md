# 02 — Persistence, Repository Storage and Recovery

## Objective

Keep runtime data separate from source code. Use one dedicated branch per world identity: world-data/<world-id>. Never store world archives in main.

## Data to persist

- Overworld, Nether and End world data.
- Player data, statistics and advancements.
- Whitelist, operators and bans.
- Native mod databases and configuration.
- Homes, personal waypoints, claims and trust lists.
- Ender Chest and other gameplay data.
- World/server configuration required to restore the same instance.
- Snapshot manifest, sequence and integrity metadata.

Do not put runtime logs, executables, compiled engines, Rust caches, FRP binaries, temporary files, environment secrets, tokens or prepared Minecraft resources into hourly world snapshots unless a separate explicit and lawful provisioning design requires it.

Horizon requires prepared Minecraft 26.3 game resources from the owner's own copy. Do not download, redistribute or commit Mojang game assets.

## World identity and seed isolation

The owner's current seed is **9064150133272194**. The initial world name is `survival`, Minecraft version is `26.3`, and world ID is `survival-9064150133272194-26.3`. The initial runtime branch is `world-data/survival-9064150133272194-26.3`. Do not silently change this seed or restore another world identity.

Create a stable world ID from validated seed and generation-relevant configuration, including Minecraft generation version and relevant data pack/config identity. Do not rely on the seed alone if other generation inputs alter the world.

A changed seed or generation identity must select a new world-data branch. Never merge worlds or overwrite the previous seed's data automatically. A new world with no matching snapshot must require an explicit first-world initialization path.

## Snapshot consistency

Use Horizon's supported backup mechanism for the pinned release. Do not copy region or player files while the server is mutating them unless the exact snapshot consistency mechanism has been verified.

A snapshot contains:
- A single verified archive.
- A schema-versioned manifest.
- SHA-256 digest.
- Monotonic sequence number.
- World ID.
- Horizon release/commit.
- Native mod revisions.
- Minecraft version.
- Creation timestamp in UTC.
- Clean-shutdown flag.

Example manifest (values generated at runtime):

    {
      "schema_version": 1,
      "world_id": "validated-world-id",
      "minecraft_version": "26.3",
      "horizon_revision": "pinned-commit",
      "native_mod_revision": "pinned-commit",
      "created_at": "UTC timestamp",
      "snapshot_sequence": 1,
      "archive": "world.zip",
      "archive_sha256": "computed-sha256",
      "clean_shutdown": false
    }

Version the manifest schema and implement explicit migration logic when the format changes.

## Branch layout

    world-data/<world-id>/
      current/
        manifest.json
        world.zip
      previous/
        manifest.json
        world.zip

Do not put multiple worlds in one unvalidated namespace. Keep at least current and previous verified snapshots.

## Checkpoint algorithm

1. Generate a consistent Horizon backup.
2. Test the archive.
3. Compute and compare checksum.
4. Generate manifest.
5. Fetch the world-data branch and record its exact HEAD SHA.
6. Validate the current snapshot before replacing it.
7. Prepare next tree in a temporary local directory.
8. Move existing current to previous only after it validates.
9. Write new current archive and manifest.
10. Commit with parent equal to fetched branch head.
11. Update the branch only if the expected head is still current; on a race, fetch and reconcile rather than overwriting.
12. Fetch again and verify remote manifest and archive hash.
13. Retain successful commit metadata for HANDOFF/operations logs.

Use compare-and-swap/expected-head semantics where available. A force update is not acceptable for routine snapshots. Never force-push main. If two writers race, one must fail and reconcile.

## Storage limits

Initial project safety defaults:
- MAX_SNAPSHOT_FILE_BYTES=90,000,000
- MAX_REPOSITORY_SIZE_MB=750 warning threshold
- SNAPSHOTS_RETAINED=2

These are configurable conservative project limits, not statements of GitHub's account quota. A single file above the configured maximum must be refused before upload. Do not split archives to evade file limits, silently truncate files or switch to Git LFS without an explicit reviewed design.

If the archive or repository grows beyond the safe threshold:
- Preserve previous valid snapshot.
- Stop the upload.
- Notify Telegram.
- Mark repository storage BLOCKED.
- Recommend external object storage or persistent VPS storage.
- Do not claim the latest world has been persisted.

Git history does not behave like a rolling database, and deleting old paths does not necessarily reclaim hosted repository storage immediately. Avoid accumulating full archives in normal commit history; design a controlled snapshot history and retention strategy, and document its limits.

## Restore algorithm

Create scripts/restore.sh.

1. Calculate validated world ID.
2. Fetch matching world-data branch.
3. Read current manifest.
4. Validate schema, world ID, version and digest.
5. Test the archive.
6. Extract into a temporary directory.
7. Validate required world layout and metadata.
8. Atomically replace runtime data.
9. Start Horizon only after restore succeeds.

If current is invalid, validate previous independently and restore it only if its world ID and format match. If neither validates, stop, notify the owner and do not initialize a new world over the damaged data.

## Destructive operations

Require a verified pre-operation snapshot before:
- Horizon or native mod upgrades.
- World migration.
- Schematic import.
- Large-scale block modifications.
- Configuration or data schema migration.
- Any operation that can rewrite existing world data.

## Acceptance tests

- Restore existing world.
- Homes, claims, player data and Ender Chest survive restart.
- Invalid checksum is rejected.
- Corrupt current falls back to valid previous.
- Different seed cannot overwrite existing world.
- Concurrent writer cannot replace a newer snapshot.
- Final snapshot has clean_shutdown=true only after clean shutdown.
- Failed push retains previous remote snapshot.
- Oversized archive is refused without damaging existing data.