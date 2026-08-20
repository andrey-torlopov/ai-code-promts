# AI Core

> Standalone fallback. Use only for a repository that must work without
> the global system in `~/.claude/custom/`. With the global system present, use
> `claude-md-template.md` plus `project-facts-template.md` instead.

This file is the SSOT for global agent behavior.

Read `RESOLVER.md`, then exactly one selected `SKILLS/<skill>/SKILL.md`.

Core rules:

1. Verify requirements against files and user constraints.
2. Change only what the task requires.
3. Do not use placeholders or skipped code.
4. Destructive work requires explicit confirmation.
5. Deploy/release work requires an explicit gated flow.
