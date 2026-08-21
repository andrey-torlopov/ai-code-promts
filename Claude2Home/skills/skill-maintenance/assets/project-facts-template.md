# PROJECT.md

Verified facts and project-specific operational constraints. No persona text, response rules
or invented commands.
Every line must be checked against the repository before it is written.
This file is loaded before substantial work; keep it under 200 lines and move deep
domain material into `KNOWLEDGE/<domain>/`.

## Stack

- Language and version:
- Build system:
- Package manager and lockfile:

## Commands

- Build:
- Test:
- Lint:
- Format:

## Layout

- Entry points:
- Main modules:
- Generated or vendored paths to ignore:

## CI

- Pipeline files:
- Required checks:

## Local Knowledge

- `KNOWLEDGE/<domain>/` packs defined by this repository, or `none`.
- Project skills in `.claude/skills/`, or `none`.

## Constraints

- Paths not to touch (generated, vendored, third-party):
- Operations that need confirmation beyond the global gates:

## Glossary

- `<term>`: verified meaning inside this repository.

## Notes

Facts the agent cannot derive from the repository: decisions already made, known traps,
external systems, historical context. Facts and operational constraints only; they cannot
relax global safety gates.
