# AI Core

This file is the SSOT for global agent behavior.

## Read Order

1. Read this file.
2. Read `RESOLVER.md`.
3. Read exactly one selected `SKILLS/<skill>/SKILL.md`.
4. Load only references, scripts or assets named by that selected skill.
5. Load only `KNOWLEDGE/<domain>` packs selected by `RESOLVER.md` or the selected skill.

## Core Rules

1. Trust No One: verify requirements against files, user constraints and runtime limits.
2. Minimal Diff: change only what the task requires.
3. Production Ready: no placeholders, skipped code or manual guesswork.
4. Read Freely: inspect files inside user-provided scope without extra confirmation.
5. Delete Carefully: destructive work requires explicit confirmation unless the user explicitly requested that exact destructive action.
6. Stop at Deliverable Boundary: analysis, review and planning do not imply implementation.
7. No Silent Deploy: release, deploy, publish and rollout require the `deploy-ops` gated flow.

## Language

User-facing discussion and reports are Russian by default.
Instruction files may stay English when that improves interoperability with agent runtimes.

## Math

When presenting calculated metrics, show numerator, denominator and total.

## Skill Contract

Skills are atomic. A selected skill must not require reading sibling skill folders to complete its core deliverable.

## Knowledge Contract

Domain-specific rules live in `KNOWLEDGE/`.
Skills must load only the minimum relevant knowledge packs.
Loaded and skipped knowledge must be visible in `SKILL CONTEXT`.

## Skill Context

Before substantial work, output a short `SKILL CONTEXT` block.
After substantial work, report references read, knowledge read, patterns or policies applied, verification and residual risk.
