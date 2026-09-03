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

Before substantial work, output the SKILL CONTEXT block (the template is already in the
injected RESOLVER.md; fallback: `$CODEX_HOME/custom/_core/skill-context.md`).
Always include deploy gate, rollback assumptions, verification assumptions and `No silent deploy`.

## Inputs

- Target environment or release channel.
- Requested operation: deploy, release, publish, rollout or rollback.
- Project-specific deploy docs and CI/CD files.
- Confirmation boundary.

## Workflow

1. In one batched read, load `references/deploy-gates.md`,
   `$CODEX_HOME/custom/KNOWLEDGE/devops/_rules.md`,
   `$CODEX_HOME/custom/KNOWLEDGE/devops/ci-pipelines.md`,
   `$CODEX_HOME/custom/KNOWLEDGE/devops/verification.md` and project-specific deploy docs.
2. Run preflight checks that do not mutate external state.
3. Show the deploy gate and wait for confirmation before state-changing operations.
4. Execute only approved steps.
5. Verify result and report rollback path.

## Local References

- `references/deploy-gates.md` - release gate block plus rollback contract.

CI and verification facts live in `$CODEX_HOME/custom/KNOWLEDGE/devops/` (canonical; do not
duplicate them here).

## Output

Return actions taken, verification, rollback path, residual risk and final `TRACE`.

## Stop Conditions

- No silent deploy.
- No production/staging mutation without explicit confirmation.
- Do not route deploy/release work to `mac-local-ops`.
- Do not require another skill folder.
