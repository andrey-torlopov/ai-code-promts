# AI Core

> Standalone fallback. Use only for a repository that must work without
> the global system in `$CODEX_HOME/custom/`. With the global Codex system present,
> use `agents-md-template.md` plus `project-facts-template.md` instead.
> This is a minimal profile, not a mirror of the installed CORE.md.

This file is the SSOT for global agent behavior.

Read `RESOLVER.md`, then exactly one selected `skills/<skill>/SKILL.md`.

Core rules:

1. Trust No One: verify requirements against files and user constraints.
2. Minimal Diff: change only what the task requires.
3. Production Ready: no placeholders or skipped code.
4. Delete Carefully: destructive work requires explicit confirmation unless the user
   explicitly requested that exact destructive action.
5. Stop at Deliverable Boundary: analysis, review and planning do not imply implementation.
6. No Silent Deploy: deploy/release work requires an explicit gated flow.
7. No Unrequested Builds: launch a project build only when the request or the project's
   `PROJECT.md` build policy explicitly allows it.
