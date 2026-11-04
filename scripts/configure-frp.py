#!/usr/bin/env python3
"""Write a minimal FRP v0.71.1 client config without embedding the token."""

from __future__ import annotations

import json
import os
import pathlib
import re


def required(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    out_dir = pathlib.Path(required("FRP_DIR"))
    out_dir.mkdir(parents=True, exist_ok=True)

    address = required("FRP_SERVER_ADDR")
    if not re.fullmatch(r"[A-Za-z0-9.:[\]-]+", address):
        raise SystemExit("FRP_SERVER_ADDR contains unsupported characters.")

    token = required("FRP_AUTH_TOKEN")
    control_port = int(required("FRP_SERVER_PORT", "7000"))
    local_port = int(required("FRP_JAVA_LOCAL_PORT", "25565"))
    remote_port = int(required("FRP_JAVA_REMOTE_PORT", "25565"))

    if not all(1 <= port <= 65535 for port in (control_port, local_port, remote_port)):
        raise SystemExit("FRP ports must be between 1 and 65535.")

    token_file = out_dir / "frp-auth-token"
    token_file.write_text(token, encoding="utf-8")
    token_file.chmod(0o600)

    def toml_string(value: str) -> str:
        return json.dumps(value)

    config = "\n".join(
        [
            f"serverAddr = {toml_string(address)}",
            f"serverPort = {control_port}",
            'auth.method = "token"',
            'auth.tokenSource.type = "file"',
            f"auth.tokenSource.file.path = {toml_string(str(token_file))}",
            'log.to = "console"',
            'log.level = "info"',
            "",
            "[[proxies]]",
            'name = "horizon-java"',
            'type = "tcp"',
            'localIP = "127.0.0.1"',
            f"localPort = {local_port}",
            f"remotePort = {remote_port}",
            "",
        ]
    )

    config_path = out_dir / "frpc.toml"
    config_path.write_text(config, encoding="utf-8")
    config_path.chmod(0o600)
    print(f"Generated FRP Java TCP tunnel config at {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
