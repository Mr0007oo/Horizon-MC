---
name: hand-off
description: Preserve Horizon MC work, verify tests, push a checkpoint feature branch to the canonical repository and open a PR against main.
agent: agent
---

# Horizon MC — Hand-off

The user invoked /hand-off. Follow .github/copilot-instructions.md and docs/requirements/06-testing-handoff.md.

Canonical destination:
https://github.com/Mr0007oo/Horizon-MC

Canonical base:
main

## 1. Freeze unrelated work

Do not start new features. Finish only changes needed to create a consistent checkpoint.

## 2. Inspect before modifying Git

Inspect:
- git status
- git remote -v
- git branch --show-current
- git log -5 --oneline
- git diff and git diff --cached
- untracked files

Identify the actual checkout repository and ensure the canonical destination is correct. Never assume the workspace is already the correct clone.

## 3. Preserve and protect

Do not delete unknown files. Do not stage .env, tokens, credentials, forwarding secrets, world directories, backups, Mojang assets, .local, build outputs or runtime caches.

Include safe source, tests, documentation and example configuration only.

## 4. Validate

Run relevant formatters, builds and tests. Update IMPLEMENTATION_STATUS.md, DECISIONS.md and HANDOFF.md. List any failing or skipped tests honestly. Do not mark untested features VERIFIED.

## 5. Authentication error recovery

If gh auth status or another GitHub CLI command reports an authentication error, do not immediately abandon the handoff.

Inspect the existing Git remote and workspace/Codespaces Git credential helper. Test fetch from the canonical repository using the existing authenticated Git transport. Never display credentials, extract tokens, paste tokens into URLs, or write credentials to files.

If Git transport works, continue using it even if gh CLI does not. If Git transport is also unauthorized, preserve the local checkpoint and report that authenticated remote push/PR creation is blocked. Never bypass access restrictions.

## 6. Canonical repository selection

If current origin is a fork or not https://github.com/Mr0007oo/Horizon-MC.git:
- Keep existing origin intact.
- Add or use a clearly named canonical remote.
- Fetch canonical main.
- Inspect remote history and files.
- Create a handoff branch based on the latest canonical main.
- Bring across only intended safe project changes.
- Resolve conflicts only when intent is clear.
- Never replace the canonical repository with an unrelated workspace copy.

"Push to the main repo" means push the handoff feature branch to the canonical repository. Do not push code directly to the main branch.

## 7. Branch and PR

Use a branch such as copilot/handoff/<task-slug> based on canonical main.

Commit a meaningful checkpoint. Push the branch to the canonical repository with existing authorized credentials. Fetch it again and verify that the remote SHA matches the intended checkpoint.

Create an open pull request:
- Repository: Mr0007oo/Horizon-MC
- Base: main
- Head: the canonical handoff branch

Do not merge automatically. Do not force-push main. Do not rewrite other contributors' branches.

## 8. Conflicts

Preserve both valid changes where possible. Do not discard tests, configuration, user data or work by another agent to get a clean diff. If intent is ambiguous, keep the checkpoint, document the conflict and do not claim the PR is ready.

## 9. Final report

After GitHub confirms the PR, update HANDOFF.md with:
- Branch
- Commit SHA
- PR URL
- Completed tasks
- Tests passing/failing/skipped
- Remaining tasks
- Known blockers

Never claim a push or PR succeeded without verifying the remote result.