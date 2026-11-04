#!/usr/bin/env python3
"""Branch-isolated, checksum-verified Horizon world snapshots."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import zipfile

MAX_ARCHIVE = int(os.getenv("MAX_SNAPSHOT_FILE_BYTES", "90000000"))
MAX_HISTORY = int(os.getenv("MAX_REPOSITORY_HISTORY_BYTES", "750000000"))
HORIZON_VERSION = os.getenv("HORIZON_VERSION", "v0.2.97")


def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def git(*args: str, cwd: pathlib.Path, check: bool = True, input: str | None = None):
    result = subprocess.run(
        ["git", *args], cwd=cwd, text=True, input=input,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def horizon(*args: str) -> str:
    command = [env("HORIZON_BIN", "horizon-server"), "--dir", env("SERVER_DIR"), *args]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RuntimeError(f"Horizon {' '.join(args)} failed:\n{result.stdout}")
    return result.stdout


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def store_path() -> pathlib.Path:
    return pathlib.Path(env("WORLD_STORE_DIR"))


def validate(folder: pathlib.Path) -> dict | None:
    manifest_path, archive_path = folder / "manifest.json", folder / "world.zip"
    if not manifest_path.is_file() or not archive_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("world_id") != env("WORLD_ID"):
            return None
        if manifest.get("archive") != "world.zip":
            return None
        if archive_path.stat().st_size != manifest.get("size_bytes"):
            return None
        if sha256(archive_path) != manifest.get("sha256"):
            return None
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                return None
        return manifest
    except (OSError, ValueError, zipfile.BadZipFile, TypeError):
        return None


def init_store() -> None:
    repo = pathlib.Path(env("GITHUB_WORKSPACE")).resolve()
    store = store_path().resolve()
    branch = env("WORLD_BRANCH")
    store.parent.mkdir(parents=True, exist_ok=True)
    if store.exists():
        shutil.rmtree(store)

    remote = git("ls-remote", "--exit-code", "--heads", "origin",
                 f"refs/heads/{branch}", cwd=repo, check=False)
    if remote.returncode == 0:
        git("fetch", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}", cwd=repo)
        git("worktree", "add", "--detach", str(store),
            f"refs/remotes/origin/{branch}", cwd=repo)
    elif remote.returncode == 2:
        git("worktree", "add", "--detach", str(store), env("GITHUB_SHA"), cwd=repo)
        git("switch", "--orphan", branch, cwd=store)
        git("rm", "-rf", "--ignore-unmatch", ".", cwd=store, check=False)
        readme = store / "README.md"
        readme.write_text(
            f"# World snapshot branch\n\nWorld ID: {env('WORLD_ID')}\n"
            f"Seed: {env('WORLD_SEED')}\nRuntime snapshots only; source code stays on main.\n",
            encoding="utf-8"
        )
        git("config", "user.name", "github-actions[bot]", cwd=store)
        git("config", "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com", cwd=store)
        git("add", "README.md", cwd=store)
        git("commit", "-m", "chore: initialize world snapshot branch", cwd=store)
        git("push", "origin", f"HEAD:refs/heads/{branch}", cwd=store)
    else:
        raise RuntimeError(f"Cannot inspect remote world branch: {remote.stderr.strip()}")

    git("config", "user.name", "github-actions[bot]", cwd=store)
    git("config", "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com", cwd=store)
    print(f"World snapshot store ready: {branch}")



RESTORE_FILES = (
    "server.toml",
    "server.properties",
    "ops.json",
    "whitelist.json",
    "banned-players.json",
    "banned-ips.json",
)
MAX_RESTORE_FILE_BYTES = 5 * 1024 * 1024


def restore_server_files(archive_path: pathlib.Path, server: pathlib.Path) -> None:
    """Restore Horizon's small server lists/config that its world restore intentionally leaves in place."""
    restored_total = 0
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        for name in RESTORE_FILES:
            if name not in names:
                continue
            info = archive.getinfo(name)
            file_mode = info.external_attr >> 16
            if info.is_dir() or stat.S_ISLNK(file_mode):
                raise RuntimeError(f"Unsafe entry in Horizon backup: {name}")
            if info.file_size > MAX_RESTORE_FILE_BYTES:
                raise RuntimeError(f"Backup support file {name} exceeds the restore size limit.")
            restored_total += info.file_size
            if restored_total > 20 * 1024 * 1024:
                raise RuntimeError("Backup server settings/lists exceed the total restore size limit.")
            contents = archive.read(info)
            temporary = server / f".{name}.restore"
            target = server / name
            temporary.write_bytes(contents)
            os.replace(temporary, target)


def restore_world() -> None:
    store, server = store_path(), pathlib.Path(env("SERVER_DIR"))
    selected = store / "current"
    manifest = validate(selected)
    if manifest is None:
        selected = store / "previous"
        manifest = validate(selected)
    if manifest is None:
        print("No verified world snapshot exists yet; first world will be created.")
        return
    backup = server / "backups" / "horizon-restore.zip"
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected / "world.zip", backup)
    # Horizon's native restore command replaces the world directory. The same ZIP also
    # carries the six server settings/list files; restore those explicitly so OP,
    # whitelist and ban state survive ephemeral Actions runners as well.
    restore_server_files(backup, server)
    horizon("restore", "horizon-restore", "--yes")
    print(f"Restored verified snapshot sequence {manifest.get('sequence')}.")


def history_bytes(store: pathlib.Path) -> int:
    objects = git("rev-list", "--objects", "HEAD", cwd=store).stdout.splitlines()
    object_ids = [line.split(" ", 1)[0] for line in objects if line.strip()]
    if not object_ids:
        return 0
    result = git("cat-file", "--batch-check=%(objecttype) %(objectsize)",
                 cwd=store, check=False, input="\n".join(object_ids) + "\n")
    if result.returncode:
        raise RuntimeError(f"Could not estimate world branch history: {result.stderr.strip()}")
    total = 0
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == "blob":
            total += int(fields[1])
    return total


def snapshot(clean_shutdown: bool) -> None:
    store, server = store_path(), pathlib.Path(env("SERVER_DIR"))
    output = horizon("backup", "session")
    print(output.strip())
    archives = sorted((server / "backups").glob("*-session.zip"))
    if not archives:
        raise RuntimeError("Horizon reported backup completion but no session ZIP was found.")
    source = archives[-1]
    size = source.stat().st_size
    if size <= 0 or size > MAX_ARCHIVE:
        raise RuntimeError(f"Backup size {size:,} exceeds configured maximum {MAX_ARCHIVE:,} bytes.")
    with zipfile.ZipFile(source) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"Backup archive CRC validation failed at {bad}.")

    current, previous = store / "current", store / "previous"
    old = validate(current) or validate(previous)
    sequence = int(old.get("sequence", 0)) + 1 if old else 1
    projected = history_bytes(store) + size
    if projected > MAX_HISTORY:
        raise RuntimeError(
            f"World branch history estimate {projected:,} exceeds {MAX_HISTORY:,} bytes. "
            "Previous remote snapshot is unchanged; migrate to object storage or a persistent volume."
        )

    if validate(current) is not None:
        if previous.exists():
            shutil.rmtree(previous)
        os.replace(current, previous)
    elif current.exists():
        shutil.rmtree(current)

    current.mkdir(parents=True, exist_ok=True)
    archive_path = current / "world.zip"
    shutil.copy2(source, archive_path)
    manifest = {
        "schema_version": 1,
        "world_id": env("WORLD_ID"),
        "world_name": env("WORLD_NAME", "survival"),
        "seed": env("WORLD_SEED"),
        "minecraft_version": "26.3",
        "horizon_version": HORIZON_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sequence": sequence,
        "archive": "world.zip",
        "size_bytes": archive_path.stat().st_size,
        "sha256": sha256(archive_path),
        "clean_shutdown": clean_shutdown,
        "horizon_backup_name": source.name,
    }
    (current / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                           encoding="utf-8")

    # *.zip is ignored on the source branch; force-add only approved snapshot paths.
    git("add", "-A", cwd=store)
    for name in ("current", "previous"):
        folder = store / name
        if folder.exists():
            git("add", "-f", f"{name}/manifest.json", f"{name}/world.zip",
                cwd=store, check=False)
    if git("status", "--porcelain", cwd=store).stdout.strip():
        git("commit", "-m",
            f"snapshot: {manifest['world_id']} sequence {sequence}", cwd=store)
        git("push", "origin", f"HEAD:refs/heads/{env('WORLD_BRANCH')}", cwd=store)

    local = git("rev-parse", "HEAD", cwd=store).stdout.strip()
    remote = git("ls-remote", "--exit-code", "origin",
                 f"refs/heads/{env('WORLD_BRANCH')}", cwd=store).stdout.split()
    if not remote or remote[0] != local:
        raise RuntimeError("Remote world branch does not point at the verified snapshot commit.")
    if validate(current) is None:
        raise RuntimeError("Snapshot failed post-write checksum verification.")
    print(f"Snapshot {sequence} committed and verified ({size:,} bytes, sha256 {manifest['sha256']}).")


def cleanup() -> None:
    repo = pathlib.Path(env("GITHUB_WORKSPACE")).resolve()
    store = store_path().resolve()
    if store.exists():
        git("worktree", "remove", "--force", str(store), cwd=repo, check=False)
    git("worktree", "prune", cwd=repo, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("init", "restore", "snapshot", "final-snapshot", "cleanup"))
    command = parser.parse_args().command
    try:
        if command == "init":
            init_store()
        elif command == "restore":
            restore_world()
        elif command == "snapshot":
            snapshot(False)
        elif command == "final-snapshot":
            snapshot(True)
        else:
            cleanup()
        return 0
    except Exception as exc:
        print(f"world-data error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
