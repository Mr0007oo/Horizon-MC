#!/usr/bin/env python3
"""Branch-isolated Horizon snapshot store. Runtime archives never touch main."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile


MAX_ARCHIVE_BYTES = int(os.environ.get("MAX_SNAPSHOT_FILE_BYTES", "90000000"))
MAX_HISTORY_BYTES = int(os.environ.get("MAX_REPOSITORY_HISTORY_BYTES", "750000000"))
HORIZON_VERSION = os.environ.get("HORIZON_VERSION", "v0.2.97")


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value


def git(*args: str, cwd: pathlib.Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return result


def horizon(*args: str) -> str:
    command = [env("HORIZON_BIN", "horizon-server"), "--dir", env("SERVER_DIR"), *args]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Horizon command failed: {' '.join(args)}\n{result.stdout}")
    return result.stdout


def digest(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def world_store() -> pathlib.Path:
    return pathlib.Path(env("WORLD_STORE_DIR"))


def validate_snapshot(folder: pathlib.Path) -> dict | None:
    manifest_path = folder / "manifest.json"
    archive_path = folder / "world.zip"
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
        if digest(archive_path) != manifest.get("sha256"):
            return None
        return manifest
    except (OSError, ValueError, TypeError):
        return None


def init_store() -> None:
    repo = pathlib.Path(env("GITHUB_WORKSPACE")).resolve()
    store = world_store().resolve()
    branch = env("WORLD_BRANCH")

    if store.exists():
        shutil.rmtree(store)
    store.parent.mkdir(parents=True, exist_ok=True)

    remote = git("ls-remote", "--exit-code", "--heads", "origin", f"refs/heads/{branch}", cwd=repo, check=False)
    if remote.returncode == 0:
        git("fetch", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}", cwd=repo)
        git("worktree", "add", "--detach", str(store), f"refs/remotes/origin/{branch}", cwd=repo)
        git("switch", "-c", branch, cwd=store)
    elif remote.returncode == 2:
        git("worktree", "add", "--detach", str(store), env("GITHUB_SHA"), cwd=repo)
        git("switch", "--orphan", branch, cwd=store)
        git("clean", "-fdx", cwd=store)
        readme = store / "README.md"
        readme.write_text(
            "# World snapshot branch\n\n"
            f"World ID: {env('WORLD_ID')}\n"
            f"Seed: {env('WORLD_SEED')}\n"
            "Runtime snapshots only. Source code stays on main.\n",
            encoding="utf-8",
        )
        git("config", "user.name", "github-actions[bot]", cwd=store)
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=store)
        git("add", "README.md", cwd=store)
        git("commit", "-m", "chore: initialize world snapshot branch", cwd=store)
        git("push", "origin", f"HEAD:refs/heads/{branch}", cwd=store)
    else:
        raise RuntimeError(f"Could not inspect remote branch {branch}: {remote.stderr}")

    git("config", "user.name", "github-actions[bot]", cwd=store)
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=store)
    print(f"World snapshot store ready: {branch}")


def restore_world() -> None:
    store = world_store()
    server = pathlib.Path(env("SERVER_DIR"))
    snapshot_dir = store / "current"
    manifest = validate_snapshot(snapshot_dir)
    selected = snapshot_dir

    if manifest is None:
        previous = store / "previous"
        manifest = validate_snapshot(previous)
        selected = previousous

    if manifest is None:
        print("No verified world snapshot exists yet; a new world will be created.")
        return

    backup_path = server / "backups" / "horizon-restore.zip"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected / "world.zip", backup_path)
    horizon("restore", "horizon-restore", "--yes")
    print(f"Restored verified snapshot sequence {manifest.get('sequence')}.")



def reachable_blob_bytes(cwd: pathlib.Path) -> int:
    """Estimate all unique blob bytes reachable from this world branch's HEAD.

    This includes old snapshot versions retained in Git history, not just the
    two snapshot folders currently visible in the working tree.
    """
    object_lines = git("rev-list", "--objects", "HEAD", cwd=cwd).stdout.splitlines()
    object_ids = [line.split(" ", 1)[0] for line in object_lines if line.strip()]
    if not object_ids:
        return 0
    result = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objecttype) %(objectsize)"],
        cwd=cwd,
        input="\n".join(object_ids) + "\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    