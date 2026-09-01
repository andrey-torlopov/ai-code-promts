# Validation

Use these checks after instruction-system changes.

## Automated Check

```sh
sh ~/.claude/skills/skill-maintenance/scripts/validate-system.sh            # installed system
sh <Home>/skills/skill-maintenance/scripts/validate-system.sh <Home>   # source tree
```

It validates anchors, the registry, every registered skill and every `~/.claude/...`
reference target. Exit code 0 means clean.

## Structural Checks

1. Runtime anchors point to `~/.claude/custom/CORE.md` and `~/.claude/custom/RESOLVER.md`.
2. `~/.claude/custom/COMMON.md` is only a compatibility bridge.
3. Top-level `~/.claude/skills/` contains workflow skills, not routing skills.
4. Active instructions do not reference legacy prompt layers.
5. Every `SKILL.md` has YAML frontmatter with only `name` and `description`.
6. Every active `SKILL.md` contains Inputs, Workflow, Output and Stop Conditions.
7. Every active `SKILL.md` requires `SKILL CONTEXT`.
8. No skill requires reading sibling skill folders.
9. Deploy/release/publish/rollout routes only to `deploy-ops`.
10. Xcode build-time optimization routes to `swift-build-optimization`.
11. Every registered skill in `~/.claude/custom/_core/active-skills.txt` exists in `~/.claude/skills/`.
12. Skills not in the registry (plugin skills) are never structurally linted.
13. Every absolute `~/.claude/...` reference resolves to an existing file.
14. `~/.claude/settings.json` hook paths point at existing scripts in `~/.claude/hooks/`.
15. `~/.claude/settings.json` registers the `SessionStart` project-context hook and
    `~/.claude/hooks/project-context.sh` exists.
16. `SKILL CONTEXT` templates require `TASK:` and `PROJECT:` lines.

## Regression Prompts

Check routing for:

1. RND analysis with a Markdown artifact.
2. Coding from an approved plan.
3. Build/CI/runtime log diagnosis.
4. Swift review.
5. Dependency check.
6. Architecture documentation.
7. Repository scout.
8. Local filesystem or shell task.
9. Gated deploy/release task.
10. Skill maintenance or audit task.
11. Xcode clean or incremental build-time optimization.
