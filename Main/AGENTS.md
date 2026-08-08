# Project

This file is the entry point for Codex-compatible runtimes.

## Read Order

1. Read `CORE.md` - this is the SSOT for global rules.
2. Read `RESOLVER.md` - choose one workflow skill.
3. Read only the selected `SKILLS/<skill-name>/SKILL.md`.
4. Load only references, scripts, assets and `KNOWLEDGE/` packs named by that selected skill.

## Runtime Notes

- Do not copy core rules to this file: they live in `CORE.md`.
- Unknown or unclear tasks route through `RESOLVER.md`.
- Skills are Markdown-only and atomic; do not require sibling skill folders.
