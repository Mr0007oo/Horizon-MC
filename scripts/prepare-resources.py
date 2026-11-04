#!/usr/bin/env python3
"""Safely extract the owner's prepared Minecraft 26.3 resource folder."""

from __future__ import annotations

import pathlib
import sys
import tarfile


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare-resources.py ARCHIVE DESTINATION", file=sys.stderr)
        return 2

    archive = pathlib.Path(sys.argv[1])
    destination = pathlib.Path(sys.argv[2]).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if not members:
            raise SystemExit("Resource archive is empty.")

        for member in members:
            relative = pathlib.PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise SystemExit(f"Unsafe path in resource archive: {member.name}")
            if not relative.parts or relative.parts[0] != "26.3":
                raise SystemExit(
                    "Archive must contain one top-level directory named 26.3/."
                )
            if member.issym() or member.islnk() or member.isdev():
                raise SystemExit(f"Links/devices are not allowed: {member.name}")
            target = (destination / pathlib.Path(*relative.parts)).resolve()
            if destination not in target.parents and target != destination:
                raise SystemExit(f"Path escapes destination: {member.name}")

        bundle.extractall(destination, members=members)

    resource_dir = destination / "26.3"
    required = ("registries.json", "commands.json")
    missing = [name for name in required if not (resource_dir / name).is_file()]
    if missing:
        raise SystemExit(
            "Prepared resources are missing required files: " + ", ".join(missing)
        )

    print(f"Prepared Minecraft 26.3 resources installed at {resource_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
