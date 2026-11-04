# Upstream Dependency Pins

These versions were inspected for the initial bootstrap. Runtime updates require a deliberate version bump and integration test.

| Component | Version | Source / evidence |
|---|---|---|
| Horizon dedicated server | v0.2.97 | https://github.com/horizon-rust/horizon/releases/tag/v0.2.97 |
| Horizon source commit | a3acb5f0d2f59d2d5ff21a5aa000809ba1e35e2f | https://github.com/horizon-rust/horizon/commit/a3acb5f0d2f59d2d5ff21a5aa000809ba1e35e2f |
| Minecraft Java Edition | 26.3 | Horizon hosting guide for this release |
| FRP | v0.71.1 | https://github.com/fatedier/frp/releases/tag/v0.71.1 |
| FRP Linux AMD64 archive SHA-256 | 1d9875210972a5d1a62b2dc4c48df45ab0af05d3ca1b5e494a014428259df803 | GitHub release asset digest, verified by workflow |

## Horizon

The official server installer at the pinned tag supports:
- horizon-server init
- horizon-server start
- horizon-server stop
- horizon-server status --json
- horizon-server cmd ...
- horizon-server backup ...
- horizon-server restore ... --yes
- horizon-server config set KEY=VALUE

The exact installer script is fetched from the pinned version tag, not from moving main.

Horizon requires prepared Minecraft 26.3 resources supplied by the owner. The private asset release is separate from source control.

## FRP

The workflow pins the FRP v0.71.1 Linux AMD64 client archive and verifies the archive against the published SHA-256 before extracting it. The generated TOML uses the file-based token source syntax documented by that exact release:

    auth.method = "token"
    auth.tokenSource.type = "file"
    auth.tokenSource.file.path = "/temporary/path/frp-auth-token"

The FRPS deployment owner must still confirm that their installed frps accepts v0.71.1 clients and permits TCP remote port 25565.

## Updates

Never update Horizon or FRP by silently switching to latest. Update the version, checksum, generated config, setup documentation and integration tests together.