---
name: deploy-ops
description: Runs or prepares gated deploy, release, publish, rollout and production or staging operations with explicit preflight, confirmation, rollback and verification.
---

# Deploy Ops

Skill root: `$CODEX_HOME/skills/deploy-ops/`. Reference paths such as `references/...`, `modes/...`,
`scripts/...` or `../references/...` resolve against the file that names them, inside this
skill root - never against the current project directory.

This skill owns high-blast-radius release and rollout operations.

## SKILL CONTEXT

Before substantial work, output the block from `$CODEX_HOME/custom/_core/skill-context.md`.
Always include deploy gate, rollback assumptions, verification assumptions and `No silent deploy`.

## Inputs

- Target environment or release channel.
- Requested operation: deploy, release, publish, rollout or rollback.
- Project-specific deploy docs and CI/CD files.
- Confirmation boundary.

## Workflow

1. Read `references/release-gates.md`.
2. Read `references/rollback.md`.
3. Read `references/ci-cd.md`.
4. Read `references/verification.md`.
5. Load `$CODEX_HOME/custom/KNOWLEDGE/devops/_rules.md` and project-specific deploy docs.
6. Run preflight checks that do not mutate external state.
7. Show the deploy gate and wait for confirmation before state-changing operations.
8. Execute only approved steps.
9. Verify result and report rollback path.

## Local References

- `references/release-gates.md`
- `references/rollback.md`
- `references/ci-cd.md`
- `references/verification.md`

## Output

Return actions taken, verification, rollback path, residual risk and final `TRACE`.

## Stop Conditions

- No silent deploy.
- No production/staging mutation without explicit confirmation.
- Do not route deploy/release work to `mac-local-ops`.
- Do not require another skill folder.
