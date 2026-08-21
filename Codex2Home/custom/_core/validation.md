# Validation

Use these checks after instruction-system changes.

## Automated Check

```sh
CODEX_HOME="$CODEX_HOME" sh "$CODEX_HOME/skills/skill-maintenance/scripts/skill-lint.sh"
CODEX_HOME="<Home>" sh <Home>/skills/skill-maintenance/scripts/skill-lint.sh <Home>
```

It validates anchors, the registry, every registered skill and every `$CODEX_HOME/...`
reference target. Exit code 0 means clean.

## Structural Checks

1. Runtime anchors point to `$CODEX_HOME/custom/CORE.md` and `$CODEX_HOME/custom/RESOLVER.md`.
2. `$CODEX_HOME/custom/COMMON.md` is only a compatibility bridge.
3. Top-level `$CODEX_HOME/skills/` contains workflow skills, not routing skills.
4. Active instructions do not reference legacy prompt layers.
5. Every `SKILL.md` has YAML frontmatter with only `name` and `description`.
6. Every active `SKILL.md` contains Inputs, Workflow, Output and Stop Conditions.
7. Every active `SKILL.md` requires `SKILL CONTEXT`.
8. No skill requires reading sibling skill folders.
9. Deploy/release/publish/rollout routes only to `deploy-ops`.
10. Xcode build-time optimization routes to `swift-build-optimization`.
11. Every registered skill in `$CODEX_HOME/custom/_core/active-skills.txt` exists in `$CODEX_HOME/skills/`.
12. Skills not in the registry (graphify, plugin skills) are never structurally linted.
13. Every absolute `$CODEX_HOME/...` reference resolves to an existing file.
14. `$CODEX_HOME/AGENTS.md` is the only required global runtime anchor.
15. Native discovery links are managed separately in `$HOME/.agents/skills/`; the
    validator checks canonical skill contents under `$CODEX_HOME/skills/`.
16. `$CODEX_HOME/hooks.json` registers the `SessionStart` project-context hook and
    `$CODEX_HOME/hooks/project-context.sh` exists.
17. `SKILL CONTEXT` templates require a `PROJECT:` line.

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
