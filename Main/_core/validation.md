# Validation

Use these checks after instruction-system changes.

## Structural Checks

1. Runtime anchors point to `CORE.md` and `RESOLVER.md`.
2. `COMMON.md` is only a compatibility bridge.
3. Top-level `SKILLS/` contains workflow skills, not routing skills.
4. Active instructions do not reference legacy prompt layers.
5. Every `SKILL.md` has YAML frontmatter with only `name` and `description`.
6. Every active `SKILL.md` contains Inputs, Workflow, Output and Stop Conditions.
7. Every active `SKILL.md` requires `SKILL CONTEXT`.
8. No skill requires reading sibling skill folders.
9. Deploy/release/publish/rollout routes only to `deploy-ops`.
10. Xcode build-time optimization routes to `swift-build-optimization`.

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
