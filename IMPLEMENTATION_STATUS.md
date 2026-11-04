# Horizon MC — Implementation Status

**State:** Specification initialized; implementation not yet verified.  
**Canonical repository:** https://github.com/Mr0007oo/Horizon-MC  
**Default branch:** main

## Project phases

| Area | Initial state | Evidence/next action |
|---|---|---|
| Horizon upstream | RESEARCHING | Verify pinned release and executable |
| Prepared 26.3 resources | BLOCKED | Owner must supply prepared resources from their own copy |
| Dedicated server startup | NOT_STARTED | Bootstrap and health test |
| FRP Java TCP | NOT_STARTED | Verify FRP client/server config and mapping |
| FRP Bedrock UDP | NOT_STARTED | Enable only with tested Geyser path |
| Velocity forwarding | RESEARCHING | Verify exact release and modern forwarding |
| Geyser/Floodgate | RESEARCHING | Verify current compatibility end to end |
| Java 26.3 | RESEARCHING | Native target; run client integration test |
| Java 26.2 | BLOCKED_PENDING_RESEARCH | Protocol translation not established |
| Offline/cracked authentication | BLOCKED_PENDING_RESEARCH | Offline mode alone does not authenticate |
| Hourly checkpoint | NOT_STARTED | Implement consistent backup and remote verification |
| world-data storage | NOT_STARTED | Test archive size and branch strategy |
| Graceful session shutdown | NOT_STARTED | Simulated lifecycle test |
| Optional continuation | NOT_STARTED | Disabled by default; budget and restrictions |
| Telegram bot | NOT_STARTED | Use existing TELEGRAM_BOT_TOKEN secret |
| Homes | RESEARCHING | Official SMP baseline; verify pinned compatibility |
| TPA | RESEARCHING | Official SMP baseline; add aliases |
| Claims/trust | RESEARCHING | Official SMP baseline; test all mutation hooks |
| Personal waypoints | NOT_STARTED | Implement custom native mod |
| Vein Miner | NOT_STARTED | Implement custom native mod |
| Self-service /ec | NOT_STARTED | Implement safely; distinct from /endersee |
| PvP duels | NOT_STARTED | Implement custom native mod |
| Schematic import | BLOCKED_PENDING_RESEARCH | Format/parser and hooks need verification |
| Combined gameplay regression | NOT_STARTED | Required before feature VERIFIED |

## Pinned upstream revisions

Fill only after checking out and testing exact commits:

- Horizon repository:
- Horizon commit:
- Horizon release:
- Horizon Mixins commit:
- Official SMP commit:
- Custom native mod revision:
- Runtime artifact and SHA-256:

## Verification log

No runtime build, client test, world backup or restore test has yet been performed by this repository initialization.

## Known blockers

1. Prepared game resources must be supplied by the owner.
2. Java 26.2 client protocol compatibility is not established.
3. Public offline-mode identity/authentication design is not yet verified.
4. FRP server version and exact server config must be inspected.
5. Bedrock proxy and Geyser/Floodgate versions must be pinned and tested.
6. Git snapshot storage limits may be exceeded by a growing world.
7. Missing custom gameplay features require real native hooks and combined tests.

## Next task

Complete Phase 0 feasibility research and write docs/ARCHITECTURE.md before starting gameplay implementation.