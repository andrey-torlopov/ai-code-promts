# Skill Resolver

Global router. Lives in `~/.claude/custom/RESOLVER.md` and applies to every project.

Use the first concrete deliverable match. If several rows match, choose the skill with the safest stop gate.

## Invocation

The seven workflow skills are installed as native user skills in `~/.claude/skills/`.
Selecting a row means invoking that skill through the runtime's skill mechanism when one exists,
otherwise reading `~/.claude/skills/<skill>/SKILL.md` directly. Both paths are equivalent;
the `SKILL CONTEXT` block is mandatory either way.

A project may override a global skill by defining a skill with the same name in its own
`.claude/skills/`. The project version wins.

## Skill Context Template

Substantial work must start with this flat block:

```text
SKILL: <skill> (mode=<mode-or-none>)
REASON: <why this skill owns the deliverable>
KNOWLEDGE: <loaded packs or none>
SKIPPED: <relevant packs intentionally not loaded>
REFERENCES: <local references loaded or none>
RULES: <CORE rules and local gates>
ARTIFACT: <path or none>
STOP: <deliverable boundary; no hidden next phase>
```

Final reports for substantial work must include:

```text
TRACE:
- Skill:
- References read:
- Knowledge read:
- Patterns/policies applied:
- Verification:
- Residual risk:
```

## Routing Table

| Request signal | Skill | Mode | Knowledge packs | Deliverable |
|---|---|---|---|---|
| optimize Xcode/iOS/macOS build time, slow clean build, slow incremental build, Swift compile hotspots, Xcode build settings audit, SPM build overhead | `swift-build-optimization` | `benchmark/analyze/fix/verify` | `swift`, `ios` | Benchmark artifacts, optimization plan, approved fixes plus re-benchmark |
| study, analyze, plan, RND, architecture, dependency, repo scout | `analysis-plan` | `plan/refactor/architecture/deps/scout` | selected by scope | Markdown report or plan |
| review, PR review, diff review, find issues without edits | `analysis-plan` | `review` | language-specific patterns | Findings/report |
| standalone research, comparison, external sources | `analysis-plan` | `research` | optional | Source-backed report |
| design spec, brainstorm, product or technical spec | `analysis-plan` | `spec` | optional/domain-specific | Design/spec artifact |
| implement, do from plan, apply fix, concrete edit | `implementation-from-plan` | none | language/project-specific | Changed files plus verification |
| build fails, CI fails, runtime error, crash, logs, root cause | `debug-diagnose` | `build/ci/runtime/environment` | logs/build/CI/language-specific; `swift/debugging/` for Apple crash artifacts; `zig` for Zig panics and builds | Root cause plus fix plan |
| macOS, shell, files, zsh, brew, mise, local diagnosis | `mac-local-ops` | none | `shell`, macOS/project-specific | Safe local action/report |
| deploy, release, publish, rollout, production/staging operation | `deploy-ops` | none | `devops`, project-specific deploy docs | Gated deploy/release action |
| create/update/audit skills, instruction set, registry, lint | `skill-maintenance` | `authoring/audit/registry/lint/ai-context-init` | AI instruction rules | Changed skills or audit report |

## Tie-Breakers

1. Explicit user skill selection wins if it does not contradict the task.
2. If a request contains analysis and code changes, choose `analysis-plan` first unless there is an approved plan or a concrete edit directive.
3. If a request contains debug and "fix it now", choose `debug-diagnose` first, then hand off to `implementation-from-plan` only after a root cause is stated.
4. Deploy/release/publish/rollout never routes to `mac-local-ops`.
5. Destructive local operations require the destructive-action confirmation gate.
6. `analysis-plan` does not change project files except an explicitly requested Markdown artifact.
7. `implementation-from-plan` does not change architecture beyond the approved plan or concrete directive.
8. Do not create a new top-level skill for a new language or stack; add `~/.claude/custom/KNOWLEDGE/<domain>/` first.
9. Xcode build-time optimization routes to `swift-build-optimization` before generic `analysis-plan`, `debug-diagnose` or `implementation-from-plan`; its approval gate decides whether the turn stops at a plan or proceeds to edits.

## Canonical Read Order

```text
~/.claude/CLAUDE.md  (or project CLAUDE.md / AGENTS.md / GEMINI.md)
  -> ~/.claude/custom/CORE.md
  -> ~/.claude/custom/RESOLVER.md
  -> ~/.claude/skills/<selected-skill>/SKILL.md
  -> references/scripts/assets named by selected skill
  -> ~/.claude/custom/KNOWLEDGE/<domain> packs named by resolver or selected skill
  -> project-local KNOWLEDGE/ or .claude/skills/ only when the project defines them
```

Forbidden active read order:

```text
selected skill -> sibling skill
selected skill -> legacy prompt layers
selected skill -> random role notes
```
