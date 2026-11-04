#!/usr/bin/env python3
"""Offline tests for Horizon MC bootstrap helpers. No network or Mojang assets required."""

from __future__ import annotations

import json
import os
import pathlib
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(args, *, cwd=None, env=None, check=True):
    result = subprocess.run(args, cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and result.returncode:
        raise AssertionError(
            f"Command failed ({result.returncode}): {args}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


class RuntimeHelpersTests(unittest.TestCase):
    def test_resource_archive_validates_and_extracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            archive = base / "resources.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for name, data in (("26.3/horizon-resources.json", b"{}"),
                                   ("26.3/registries.json", b"{}"),
                                   ("26.3/commands.json", b"{}")):
                    source = base / pathlib.Path(name).name
                    source.write_bytes(data)
                    tar.add(source, arcname=name)
            destination = base / "out"
            run([sys.executable, str(ROOT / "scripts/prepare-resources.py"),
                 str(archive), str(destination)])
            self.assertTrue((destination / "26.3/horizon-resources.json").is_file())
            self.assertTrue((destination / "26.3/registries.json").is_file())
            self.assertTrue((destination / "26.3/commands.json").is_file())

    def test_resource_archive_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            archive = base / "unsafe.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                source = base / "x"
                source.write_text("bad")
                tar.add(source, arcname="26.3/../../escape")
            result = run([sys.executable, str(ROOT / "scripts/prepare-resources.py"),
                          str(archive), str(base / "out")], check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((base / "escape").exists())

    def test_resource_archive_requires_horizon_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            archive = base / "missing-manifest.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                for name in ("registries.json", "commands.json"):
                    source = base / name
                    source.write_text("{}")
                    tar.add(source, arcname=f"26.3/{name}")
            result = run([sys.executable, str(ROOT / "scripts/prepare-resources.py"),
                          str(archive), str(base / "out")], check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("horizon-resources.json", result.stderr + result.stdout)

    def test_invalid_saved_snapshot_refuses_to_create_a_new_world(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            store = base / "world-store"
            server = base / "server"
            (store / "current").mkdir(parents=True)
            server.mkdir()
            (store / "current/world.zip").write_bytes(b"not-a-zip")
            (store / "current/manifest.json").write_text(
                json.dumps({
                    "world_id": "survival-9064150133272194-26.3",
                    "archive": "world.zip",
                    "size_bytes": len(b"not-a-zip"),
                    "sha256": "deliberately-wrong",
                })
            )
            env = os.environ.copy()
            env.update({
                "WORLD_STORE_DIR": str(store),
                "SERVER_DIR": str(server),
                "WORLD_ID": "survival-9064150133272194-26.3",
            })
            result = run(
                [sys.executable, str(ROOT / "scripts/world-data.py"), "restore"],
                env=env,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to create a fresh world", result.stderr)

    def test_resource_downloader_uses_expanded_shell_variables(self):
        script = (ROOT / "scripts/fetch-resources.sh").read_text(encoding="utf-8")
        self.assertNotRegex(script, r"\\\\\\$\\{[A-Z_]+")
        self.assertIn('${GITHUB_REPOSITORY}', script)
        self.assertIn('"\${headers[@]}"', script)

    def test_frp_config_does_not_embed_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env.update({
                "FRP_DIR": tmp,
                "FRP_SERVER_ADDR": "frp.example.test",
                "FRP_SERVER_PORT": "7000",
                "FRP_JAVA_LOCAL_PORT": "25565",
                "FRP_JAVA_REMOTE_PORT": "25565",
                "FRP_AUTH_TOKEN": "TEST_TOKEN_MUST_NOT_APPEAR",
            })
            run([sys.executable, str(ROOT / "scripts/configure-frp.py")], env=env)
            folder = pathlib.Path(tmp)
            config = (folder / "frpc.toml").read_text()
            token_file = folder / "frp-auth-token"
            self.assertNotIn("TEST_TOKEN_MUST_NOT_APPEAR", config)
            self.assertEqual(token_file.read_text(), "TEST_TOKEN_MUST_NOT_APPEAR")
            self.assertEqual(stat.S_IMODE(token_file.stat().st_mode), 0o600)
            self.assertIn('type = "tcp"', config)
            self.assertIn("remotePort = 25565", config)
            self.assertNotIn("19132", config)

    def test_world_branch_snapshot_rotation_and_remote_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            remote, workspace = base / "remote.git", base / "workspace"
            server, store = base / "server", base / "world-store"
            workspace.mkdir()
            server.mkdir()
            run(["git", "init", "--bare", str(remote)])
            run(["git", "init", str(workspace)])
            run(["git", "config", "user.name", "Test"], cwd=workspace)
            run(["git", "config", "user.email", "test@example.invalid"], cwd=workspace)
            (workspace / ".gitignore").write_text("*.zip\n.env\n", encoding="utf-8")
            (workspace / "README.md").write_text("source branch\n", encoding="utf-8")
            run(["git", "add", "."], cwd=workspace)
            run(["git", "commit", "-m", "init"], cwd=workspace)
            run(["git", "branch", "-M", "main"], cwd=workspace)
            run(["git", "remote", "add", "origin", str(remote)], cwd=workspace)
            run(["git", "push", "-u", "origin", "main"], cwd=workspace)

            fake = base / "horizon-server"
            fake.write_text("""#!/usr/bin/env python3
import datetime, pathlib, sys, zipfile
args = sys.argv[1:]
server = pathlib.Path(args[args.index("--dir") + 1])
folder = server / "backups"
folder.mkdir(parents=True, exist_ok=True)
if args[2] == "restore":
    with zipfile.ZipFile(folder / "horizon-restore.zip") as archive:
        archive.extract("survival/level.dat", server)
    print("Restored test world")
elif args[2] == "backup":
    name = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S") + "-session.zip"
    with zipfile.ZipFile(folder / name, "w") as archive:
        archive.writestr("survival/level.dat", b"test-world")
        archive.writestr("server.toml", b"[server]\\nport = 25565\\n")
        archive.writestr("ops.json", b"[{\\"name\\":\\"Owner\\"}]")
        archive.writestr("whitelist.json", b"[{\\"name\\":\\"Friend\\"}]")
        archive.writestr("banned-players.json", b"[]")
        archive.writestr("banned-ips.json", b"[]")
    print("Backed up to backups/" + name)
""", encoding="utf-8")
            fake.chmod(0o755)
            sha = run(["git", "rev-parse", "HEAD"], cwd=workspace).stdout.strip()
            env = os.environ.copy()
            env.update({
                "GITHUB_WORKSPACE": str(workspace), "GITHUB_SHA": sha,
                "WORLD_STORE_DIR": str(store), "SERVER_DIR": str(server),
                "WORLD_ID": "survival-9064150133272194-26.3",
                "WORLD_BRANCH": "world-data/survival-9064150133272194-26.3",
                "WORLD_SEED": "9064150133272194", "WORLD_NAME": "survival",
                "HORIZON_BIN": str(fake), "HORIZON_VERSION": "v0.2.97",
            })
            script = str(ROOT / "scripts/world-data.py")
            for command in ("init", "snapshot"):
                run([sys.executable, script, command], env=env)
            run([sys.executable, script, "restore"], env=env)
            self.assertIn('"Owner"', (server / "ops.json").read_text())
            self.assertIn('"Friend"', (server / "whitelist.json").read_text())
            run([sys.executable, script, "final-snapshot"], env=env)

            clone = base / "verify"
            run(["git", "clone", "--branch", env["WORLD_BRANCH"], str(remote), str(clone)])
            self.assertTrue((clone / "current/world.zip").is_file())
            self.assertTrue((clone / "previous/world.zip").is_file())
            current = json.loads((clone / "current/manifest.json").read_text())
            previous = json.loads((clone / "previous/manifest.json").read_text())
            self.assertTrue(current["clean_shutdown"])
            self.assertFalse(previous["clean_shutdown"])
            tracked = run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=clone).stdout
            self.assertIn("current/world.zip", tracked)

    def test_session_deadline_is_325_minutes(self):
        script = (ROOT / "scripts/run-session.sh").read_text(encoding="utf-8")
        self.assertIn('"$elapsed" -ge 300', script)
        self.assertIn('"$elapsed" -ge 315', script)
        self.assertIn('"$elapsed" -ge 325', script)
        self.assertNotIn('"$elapsed" -ge 340', script)
        self.assertIn('"$elapsed" -lt 270', script)
        self.assertIn('timeout --signal=TERM --kill-after=30s 1500s', script)
        self.assertIn("sleep 5", script)


if __name__ == "__main__":
    unittest.main()
