# GitHub Copilot Instructions — Horizon MC

## 1. Repository identity and source of truth

Canonical repository: https://github.com/Mr0007oo/Horizon-MC  
Canonical repository full name: Mr0007oo/Horizon-MC  
Canonical target branch: main  
Master specification: PRD.md

Read the master PRD and the relevant requirement documents before changing code:

- docs/requirements/01-hosting-lifecycle.md
- docs/requirements/02-persistence.md
- docs/requirements/03-networking-crossplay.md
- docs/requirements/04-gameplay-mods.md
- docs/requirements/05-telegram-control.md
- docs/requirements/06-testing-handoff.md

Keep IMPLEMENTATION_STATUS.md, DECISIONS.md and HANDOFF.md current.

## 2. Upstream Horizon

Actual upstream source: https://github.com/horizon-rust/horizon  
Dedicated server guide: https://github.com/horizon-rust/horizon/blob/main/docs/hosting.md  
Server API: https://github.com/horizon-rust/horizon/blob/main/docs/api/server.md  
Native mods: https://github.com/horizon-rust/horizon/blob/main/docs/native-mods.md  
Official SMP mod: https://github.com/horizon-rust/horizon-mods/tree/main/native/smp

Horizon is a Rust implementation. Do not assume Bukkit, Spigot, Paper, Fabric, Forge or Java plugin JAR compatibility. Use only real, documented Horizon interfaces and verified native mod hooks.

## 3. No hallucinated capabilities

Never invent:
- Horizon CLI flags or subcommands.
- Horizon server.toml keys.
- Native hooks, mod APIs or ABI details.
- Protocol IDs or compatibility claims.
- FRP configuration syntax.
- GitHub Actions capabilities or quotas.
- Geyser, Floodgate or Velocity compatibility.
- File formats or schematic behavior.

Inspect the exact source revision and official documentation used by this project. Pin tested revisions. If evidence is missing, mark the item BLOCKED or PENDING and explain the evidence needed. Do not quietly substitute another server.

## 4. Native mods and feature reuse

Inspect the official SMP source first. Reuse only when the exact revision is compatible with the pinned Horizon engine. Record Horizon, Horizon Mixins and SMP revisions in a dependency lock file.

Build missing features as real Rust native mods through the documented Horizon Mixins workflow. Do not create fake plugin JARs, fake loaders or commands that merely print success.

Use shared services for player identity, permissions, location validation, world mutations, inventory transactions, persistence and audit logs. Avoid duplicate command registration and duplicate permission systems.

Native mods execute with the server process's permissions. Review and trust all code before building it into the server.

## 5. Git repository and authentication recovery — mandatory

The canonical repository is exactly:
https://github.com/Mr0007oo/Horizon-MC

A GitHub CLI authentication error does not, by itself, prove that Git operations are unavailable. In Codespaces or another authenticated workspace:

1. Inspect the workspace before changing anything: run git status, git remote -v, git branch --show-current and git log -5 --oneline.
2. Verify the canonical repository URL. Do not assume the workspace is the canonical repository just because the folder has the expected name.
3. Test the existing Git credential helper / Codespaces-provided Git authentication by fetching the canonical remote. Do not print credentials, credential-helper output, tokens or environment secrets.
4. If the current origin is a fork or another repository, preserve it and add or use a clearly named canonical remote pointing to https://github.com/Mr0007oo/Horizon-MC.git. Do not overwrite an existing remote without inspecting it.
5. Fetch the canonical main branch and inspect its history. Do not assume it is empty or that the local main is current.
6. If GitHub CLI says it is unauthenticated but Git fetch/push works through the workspace credential helper, continue using authenticated Git transport. Do not paste tokens into remote URLs, shell history or files.
7. If Git fetch/push is also unauthorized, stop and report the exact permission/authentication blocker. Never bypass access controls, impersonate an account, search for credentials, or weaken repository security.

### Where to push

All handoff work must be based on the latest canonical main and pushed to a feature/checkpoint branch in the canonical repository when the authenticated account has permission. Example:

copilot/handoff/<task-slug>

Do not push working changes directly to the main branch. A pull request is then opened from that canonical feature branch into canonical main.

If the workspace belongs to a different repository or fork, do not open a PR against that wrong repository. Add/use the canonical remote, fetch canonical main, create a branch based on it, bring over only the intended project changes, resolve conflicts, test, push that branch to the canonical repository, and create the PR with base Mr0007oo/Horizon-MC:main.

If pushing to the canonical repository is not authorized, do not claim completion. Preserve the local checkpoint and clearly explain that owner action or corrected permissions are required.

A GitHub CLI-only error must not cause Copilot to abandon a working authenticated Git transport. Equally, a successful local checkout is not proof that a remote push succeeded: verify the remote branch and commit after pushing.

## 6. Git safety and conflict resolution

- Never force-push main.
- Never rewrite another contributor's branch.
- Never discard world data, tests, configuration or another agent's work just to clear a conflict.
- Rebase/merge only after inspecting the actual histories.
- Resolve a conflict automatically only when intent is clear and both valid changes can be preserved.
- If intent is ambiguous, preserve a checkpoint and document the conflict; do not fabricate a resolution.
- Never commit .env, secrets, tokens, forwarding secrets, prepared Mojang assets, world files, backups, caches or build outputs to main.
- Do not weaken branch protection or repository controls.

## 7. Hosting and persistence

Follow docs/requirements/01-hosting-lifecycle.md and 02-persistence.md.

GitHub Actions is a bounded session runner, not a permanent VM. A successor session is optional, budget-controlled and only allowed after a verified final snapshot. No quota evasion and no guarantee of uninterrupted 24/7 availability.

Use the world-data/<world-id> branch exclusively for runtime snapshots. Never put runtime backups on main. Use Horizon's consistent backup mechanism. Never archive an actively mutating world directory without a documented consistent snapshot procedure.

## 8. Networking

Follow docs/requirements/03-networking-crossplay.md. Reuse the owner's existing FRP server. Use separate Java TCP and Bedrock UDP mappings. Keep backend services private behind the proxy where configured. Never put real credentials in example TOML or logs.

## 9. Telegram

Follow docs/requirements/05-telegram-control.md. Authorize only configured numeric Telegram user IDs. Never execute Telegram input using an OS shell. Use the documented Horizon CLI/control API. Telegram failure must not corrupt world persistence.

## 10. Tests and completion

A feature is not complete merely because it compiles or a command is registered. Add unit, integration, persistence, permission and combined regression tests. Run all relevant modules together and test their interactions.

Update IMPLEMENTATION_STATUS.md after meaningful work. Mark VERIFIED only with concrete proof, test output or reproducible evidence. Document failed/skipped tests and limitations.

## 11. /hand-off

When the user invokes /hand-off, follow .github/prompts/hand-off.prompt.md. Freeze unrelated feature expansion, preserve work, test it, update HANDOFF.md and status, create a checkpoint branch based on canonical main, push to the canonical repository using authenticated Git transport, and open a PR to canonical main. Verify the remote branch and PR URL. Never claim success without GitHub confirmation.

## 12. Priority

Preserve completed work and data integrity before adding another feature. Keep implementation small, testable, documented and reproducible.