---
name: debug-diagnose
description: Diagnoses build, CI, runtime and environment failures, producing root cause, evidence and a fix plan without automatically changing code.
---

# Debug Diagnose

This skill diagnoses failures. It does not silently transition into implementation.

## SKILL CONTEXT

Before substantial work, output the block from `../../_core/skill-context.md`.
Set `mode` to `build`, `ci`, `runtime` or `environment`.

## Inputs

- Error output, logs, failing command, CI job, crash report or environment symptom.
- Repository or project path when available.
- Recent changes or suspected scope when known.
- Permission boundary for commands.

## Workflow

1. Read the selected `modes/<mode>.md`.
2. Read only the references named by that mode.
3. Inspect logs and files before claiming root cause.
4. Reproduce or narrow the failure when safe and useful.
5. Separate symptom, evidence, root cause, fix plan and verification.
6. Stop with a diagnosis unless the user explicitly asks to implement the fix after the root cause is stated.

## Local References

- `references/log-analysis.md`
- `references/build-diagnosis.md`
- `references/ci-diagnosis.md`
- `references/root-cause-format.md`

## Output

Return root cause, evidence, fix plan, verification plan and final `TRACE`.

## Stop Conditions

- Do not edit code before stating a root cause and fix plan.
- Do not deploy or roll out.
- Do not use destructive commands without the destructive-action gate.
- Do not require another skill folder.
