# 03 — FRP, Networking, Cross-Play and Authentication

## Existing owner infrastructure

The owner reports that the FRP server is already installed and configured. Do not rebuild it unless investigation proves it is necessary.

Supplied intended values:
- FRP control/server port: 7000
- Java public port: 25565
- Java local port: 25565
- Bedrock public port: 19132
- Bedrock local port: 19132

The previous variables ambiguously used FRP_REMOTE_PORT for both a control port and comma-separated game ports. Normalize them:

- FRP_SERVER_ADDR
- FRP_SERVER_PORT=7000
- FRP_AUTH_TOKEN
- FRP_JAVA_REMOTE_PORT=25565
- FRP_JAVA_LOCAL_PORT=25565
- FRP_BEDROCK_REMOTE_PORT=19132
- FRP_BEDROCK_LOCAL_PORT=19132
- FRP_LOCAL_HOST=127.0.0.1

Use separate typed mappings, not a comma-separated value. Confirm the actual FRP server configuration and version before writing client TOML. The control/listen port is not a Minecraft client port.

## Transport

- Java Edition: TCP.
- Bedrock Edition: UDP, only if the Geyser listener is enabled and tested.
- FRP control connection: use the configured FRP control port/protocol from the installed FRP version.

Do not silently map Bedrock as TCP. Do not forward an unused Bedrock port.

## Intended topology

    Players
       |
       v
    Existing public FRPS host
       |
       +-- TCP 25565 (Java)
       +-- UDP 19132 (Bedrock, optional)
       |
       v
    FRPC on Actions runner
       |
       v
    Velocity proxy (if required)
       |-----------------------|
       v                       v
    Java backend           Geyser UDP listener
       \                       /
        \                     /
         Horizon dedicated backend
         bound to private/local interface

The exact topology and listener ports must come from tested configuration, not assumptions. If using a proxy, the public FRP mappings should reach the proxy/Geyser entry points, not bypass them to expose the Horizon backend.

## Velocity forwarding

Follow Horizon's hosting documentation for Velocity modern forwarding. Verify the pinned release supports the required forwarding behavior. Keep a non-empty forwarding secret in an Actions Secret or protected runtime file, not in Git.

When using Velocity modern forwarding:
- Configure Horizon backend offline mode as documented for proxy forwarding.
- Configure Velocity modern forwarding.
- Restrict backend access to the proxy's private/local network.
- Verify Horizon rejects direct clients without valid forwarding.
- Test UUID, name and profile propagation.

Never expose the forwarding secret in logs, diagnostics, process arguments visible to untrusted users or repository files.

## Geyser and Floodgate

Investigate compatible Velocity distributions of Geyser and Floodgate. Verify exact versions and compatibility with the selected Bedrock protocol and Horizon's documented proxy forwarding behavior.

Test:
- Bedrock login.
- Floodgate UUID identity.
- Whitelist behavior.
- Bans and player restrictions.
- Chat.
- Movement.
- Inventory.
- Block placement/breaking.
- Disconnect/reconnect.
- Simultaneous Java and Bedrock players.

Horizon documentation describes a Floodgate UUID-prefix whitelist bypass option. Use it only if the pinned release supports it and only for the exact trusted Floodgate prefix. Do not bypass bans or other restrictions.

## Java client versions

Native target: Java Edition 26.3.

Requested additional client: Java Edition 26.2.

Do not infer protocol compatibility from world save migration. A world from an older game version being upgradeable does not mean an older client can join a newer server.

Investigate an actively maintained, exact-version translation path. Verify it works with Velocity and Horizon's backend protocol. Test login, movement, inventory, block interactions, dimensions, chat, reconnect and mixed-version sessions. Do not invent protocol IDs or claim support based on a proxy's version list alone.

If the complete path cannot be verified, mark Java 26.2 BLOCKED and clearly advertise only Java 26.3.

## Offline/cracked clients

Horizon documents online_mode=false. This accepts unverified offline identities and allows username impersonation unless a separate verified authentication system protects the public entry point.

For any public offline-mode design:
- Keep backend private behind Velocity.
- Use only a tested proxy-side authentication solution compatible with the selected Velocity release.
- Verify identity forwarding.
- Ensure operator and permission identity cannot be trivially impersonated.
- Test duplicate names, reconnects and UUID conflicts.
- Document remaining account-security limitations.

Do not call offline-mode alone secure authentication. If no suitable authentication solution is verified, record the risk and block public cracked access rather than claiming it is protected.

## FRPC health

Monitor process liveness, control connection, Java mapping, optional Bedrock mapping and proxy/backend health. Use bounded retry/backoff for FRPC reconnect. A temporary tunnel loss should not trigger destructive world operations or an unnecessary world restart. Notify Telegram when the outage exceeds a configured threshold.

## Acceptance criteria

- Java 26.3 reaches Horizon through the stable FRP address.
- Java TCP mapping is correct.
- Bedrock UDP mapping works when enabled.
- Velocity modern forwarding is accepted.
- Direct backend connections are rejected when proxy-only mode is configured.
- FRPC reconnect does not corrupt data.
- Java 26.2 is advertised only after end-to-end tests.
- Offline-mode risk is documented and tested.