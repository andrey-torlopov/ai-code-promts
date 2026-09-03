---
name: debug-diagnose
description: Diagnoses build, CI, runtime and environment failures, producing root cause, evidence and a fix plan without automatically changing code.
---

# Debug Diagnose

Skill root: `$CODEX_HOME/skills/debug-diagnose/`. Reference paths such as `references/...` or
`scripts/...` resolve against the file that names them, inside this skill root - never against
the current project directory.

This skill diagnoses failures. It does not silently transition into implementation.

## SKILL CONTEXT

Before substantial work, output the SKILL CONTEXT block (the template is already in the
injected RESOLVER.md; fallback: `$CODEX_HOME/custom/_core/skill-context.md`).
Set `mode` to `build`, `ci`, `runtime` or `environment`.

## Inputs

- Error output, logs, failing command, CI job, crash report or environment symptom.
- Repository or project path when available.
- Recent changes or suspected scope when known.
- Permission boundary for commands.

## Workflow

1. Pick the mode section below. In one batched read, load `references/diagnosis-core.md`,
   the mode's extra references and its knowledge packs.
2. Inspect logs and files before claiming root cause.
3. Reproduce or narrow the failure when safe and useful. A reproduction that launches a
   project build needs the CORE rule 9 grant (explicit request or `PROJECT.md` build policy);
   without it, diagnose from existing logs and name the command that would verify.
4. Separate symptom, evidence, root cause, fix plan and verification.
5. Stop with a diagnosis unless the user explicitly asks to implement the fix after the root
   cause is stated.

## Modes

### build

Compiler, linker, package and local build failures.

- Knowledge by project: Swift/SPM/Xcode — `$CODEX_HOME/custom/KNOWLEDGE/swift/verification.md`;
  Zig (`build.zig`, `build.zig.zon`) — `$CODEX_HOME/custom/KNOWLEDGE/zig/verification.md` and
  `$CODEX_HOME/custom/KNOWLEDGE/zig/_rules.md`, record `zig version` before quoting stdlib API
  names; shell/toolchain symptoms — `$CODEX_HOME/custom/KNOWLEDGE/shell/_rules.md`.
- Extra reference: `references/build-diagnosis.md`.
- Stop: return root cause and fix plan. Do not implement until the user confirms or the same
  request explicitly asks for implementation after diagnosis.

### ci

GitHub Actions, GitLab CI, runners, templates and pipeline logs.

- Knowledge: `$CODEX_HOME/custom/KNOWLEDGE/devops/_rules.md`,
  `$CODEX_HOME/custom/KNOWLEDGE/devops/ci-pipelines.md`, project-specific CI docs when present.
- Extra reference: `references/ci-diagnosis.md`.
- Stop: return CI root cause, evidence and pipeline fix plan. Do not deploy or mutate external
  CI state without a separate gate.

### runtime

Crashes, runtime errors, logs and incorrect behavior after startup. Load language and platform
packs only after identifying the affected stack.

Apple platforms (iOS, macOS, watchOS, tvOS), in this order:

1. `$CODEX_HOME/custom/KNOWLEDGE/swift/debugging/crash-triage.md` before reading any backtrace
   or decoding any constant; `Exception Type` decides the branch.
2. `$CODEX_HOME/custom/KNOWLEDGE/swift/debugging/hex-codes.md` for a `Termination Reason` code,
   a fault address pattern, a register value or a file magic.
3. `$CODEX_HOME/custom/KNOWLEDGE/swift/debugging/memory-diagnostics.md` when the class is a
   memory bug, or when backtraces differ across otherwise identical crashes.
4. `$CODEX_HOME/custom/KNOWLEDGE/swift/_rules.md` only when the fix scope reaches Swift code style.

Zig: `$CODEX_HOME/custom/KNOWLEDGE/zig/debugging.md` for a `thread <id> panic:` message, a `0xaa`
fill, an allocator double-free or leak report. Confirm `zig version` first; API names are
version-bound. Build and command choices come from `$CODEX_HOME/custom/KNOWLEDGE/zig/verification.md`.

Gates:

- State symbolication status before quoting a backtrace.
- Reproduce in the configuration that produced the report, or say it was not reproduced.
- For Zig, never diagnose from `ReleaseFast` or `ReleaseSmall`; re-run in `ReleaseSafe`.

Stop: return reproduction notes, root cause and fix plan. Do not edit code unless the user
explicitly requests the implementation handoff.

### environment

Shell, local tools, Xcode, package manager and path/configuration problems.

- Knowledge: `$CODEX_HOME/custom/KNOWLEDGE/shell/_rules.md`; plus
  `$CODEX_HOME/custom/KNOWLEDGE/shell/zsh.md` for zsh/profile issues,
  `$CODEX_HOME/custom/KNOWLEDGE/shell/mise.md` for mise issues,
  `$CODEX_HOME/custom/KNOWLEDGE/shell/brew.md` for Homebrew issues.
- Extra reference: `$CODEX_HOME/custom/_core/destructive-actions-policy.md`.
- Stop: report diagnosis and safe remediation. Destructive local changes need explicit
  confirmation.

## Local References

- `references/diagnosis-core.md` - log analysis plus root-cause format; every mode.
- `references/build-diagnosis.md` - mode `build` only.
- `references/ci-diagnosis.md` - mode `ci` only.

## Output

Return root cause, evidence, fix plan, verification plan and final `TRACE`.

## Stop Conditions

- Do not edit code before stating a root cause and fix plan.
- Do not deploy or roll out.
- Do not use destructive commands without the destructive-action gate.
- Do not require another skill folder.
