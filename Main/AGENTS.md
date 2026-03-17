# Agents Entry

This file is the entry point for agent runtimes, which automatically look for `AGENTS.md`.

## Read Order

1. `CORE.md` - global rules and contracts.
2. `RESOLVER.md` - choose one workflow skill.
3. Selected `SKILLS/<skill-name>/SKILL.md`.
4. Only references, scripts, assets and `KNOWLEDGE/` packs declared by that selected skill.

## Available Skills

- `SKILLS/analysis-plan/SKILL.md` - analysis, planning, review, research, repo scout, dependency checks and specs.
- `SKILLS/swift-build-optimization/SKILL.md` - Xcode, Swift, iOS and macOS build-time benchmarking, optimization planning and approved fixes.
- `SKILLS/implementation-from-plan/SKILL.md` - code/config changes from an approved plan or concrete directive.
- `SKILLS/debug-diagnose/SKILL.md` - build, CI, runtime and environment diagnosis.
- `SKILLS/mac-local-ops/SKILL.md` - macOS, shell and filesystem tasks.
- `SKILLS/deploy-ops/SKILL.md` - gated deploy, release, publish and rollout work.
- `SKILLS/skill-maintenance/SKILL.md` - AI instruction, skill, registry and lint maintenance.

Do not duplicate the rules from `CORE.md` in this file.
