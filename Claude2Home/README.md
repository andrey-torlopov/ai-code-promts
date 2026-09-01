# Claude2Home

Image of `~/.claude`. Everything here is copied into a Claude Code home directory by
`init_claude.sh`. This is the only supported way to deploy the instruction system; the older
project-level route (`Templates/Main` + `init_ai.sh`) is archived and must not be used.

## Install

```sh
./init_claude.sh                                  # into ~/.claude
./init_claude.sh --dry-run                        # show changes only
./init_claude.sh --target /path/to/fake-claude    # test target
```

Replaced files are copied to `<target>/backups/home-template-<timestamp>/` first.
After copying, the installer runs the validator and fails loudly if anything is broken.

## Payload Map

| Here | Installed to | Replaced how |
|---|---|---|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` | overwritten |
| `settings.json` | `~/.claude/settings.json` | overwritten |
| `hooks/*.sh` | `~/.claude/hooks/` | per file |
| `skills/<name>/` | `~/.claude/skills/<name>/` | per skill, wholesale |
| `custom/` | `~/.claude/custom/` | wholesale |

Not touched in the target: `projects/`, `sessions/`, `history.jsonl`, `plugins/`,
`file-history/`, `todos/`, and any skill not shipped here.

Not copied at all: this `README.md` and `init_claude.sh`.

## Layout After Install

```text
~/.claude/
├── CLAUDE.md                 auto-loaded anchor: personal rules + pointer to custom/
├── settings.json             model, permissions, hooks
├── hooks/
│   ├── bash-guard.sh         PreToolUse: deny/ask gate for destructive shell commands
│   ├── route-guard.sh        PreToolUse: denies Write/Edit until SKILL CONTEXT was emitted
│   ├── skill-lint.sh         PostToolUse: validates instruction files
│   ├── rules-context.sh      SessionStart: injects CORE.md + RESOLVER.md deterministically
│   ├── project-context.sh    SessionStart: injects PROJECT.md when the repository has one
│   └── skill-context-lint.sh Stop: every active skill still requires SKILL CONTEXT + TRACE
├── skills/                   7 workflow skills + task-lab (state layer),
│                             auto-discovered by Claude Code
└── custom/
    ├── CORE.md               SSOT for global rules
    ├── RESOLVER.md           routing table: request signal -> skill
    ├── COMMON.md             compatibility bridge
    ├── _core/                skill-context, handoff, validation, destructive-action policy
    │   └── active-skills.txt registry read by all three linters
    └── KNOWLEDGE/            lazy-loaded domain packs (swift, ios, devops, shell, python, zig)
                              plus general/ - the fallback pack when no domain matches
```

## How It Gets Loaded

1. Claude Code always loads `~/.claude/CLAUDE.md`.
2. The `SessionStart` hook `rules-context.sh` injects `CORE.md` and `RESOLVER.md` into context
   deterministically (also after resume, clear and compaction); the `# AI Runtime` section in
   `CLAUDE.md` stays as the fallback pointer for installs without the hook.
3. When the repository provides `PROJECT.md` (or `.claude/PROJECT.md`), the `SessionStart`
   hook injects it; without it nothing extra is read.
4. `RESOLVER.md` picks exactly one skill from `~/.claude/skills/`.
5. That skill loads only the `~/.claude/custom/KNOWLEDGE/` packs it names; when none match
   the scope, the `general/` fallback pack.
6. When the request carries a TaskID or points into a task folder and a `task-lab` skill is
   installed, `RESOLVER.md` also activates it as a state layer: the folder is resolved and
   restored before the subject, and the selected skill's deliverable is recorded there.
   Without that skill installed, routing is unchanged.

The fixed per-session cost is `CLAUDE.md` plus the injected `CORE.md` + `RESOLVER.md`
(about 16 KB); skills, references and `KNOWLEDGE/` packs stay lazy. The `route-guard` hook
enforces the contract mechanically: Write/Edit tool calls are denied until the agent has
emitted the `SKILL CONTEXT` block in the session (escape hatch: `CLAUDE_ROUTE_GUARD=off`;
scratch space and `~/.claude/projects/` are never gated).

## Path Rules

- Every cross-file reference is absolute (`~/.claude/custom/...`), because the agent's
  working directory is the project, not the config directory.
- Paths inside a skill (`references/...`, `modes/...`, `scripts/...`) are relative to that
  skill's own root, stated at the top of each `SKILL.md`.

## Machine-Specific Values

`settings.json` needs absolute home paths in its deny rules, but the template must stay portable,
so it stores them as `{{HOME}}`, for example `Read(/{{HOME}}/.ssh/**)` — `{{HOME}}` expands to
`/Users/<name>`, leading slash included, so the template writes one slash and gets two. `init_claude.sh` substitutes
the real `$HOME` after copying, so the installed `~/.claude/settings.json` always matches the machine
it runs on. Never hand-write a literal user path here — it silently stops matching on other hardware.
The `Bash(...)` deny rules and `hooks/bash-guard.sh` are path-independent either way.

## Editing

Edit here, then re-run `./init_claude.sh`. Editing `~/.claude/custom/` directly makes the
source tree stale; the installer overwrites those edits on the next run.

## Validation

```sh
sh skills/skill-maintenance/scripts/validate-system.sh .        # this source tree
sh ~/.claude/skills/skill-maintenance/scripts/validate-system.sh # installed system
```

Checks anchors, the registry, every registered skill, and that every absolute
`~/.claude/...` reference resolves to a file that exists.

## Adding A Skill

1. Create `skills/<name>/SKILL.md` with `## Inputs`, `## Workflow`, `## Output`,
   `## Stop Conditions`, `## SKILL CONTEXT` and a final `TRACE` requirement.
2. Add `<name>` to `custom/_core/active-skills.txt`.
3. Add a routing row to `custom/RESOLVER.md`.
4. Run the validator, then `./init_claude.sh`.

Skipping step 2 means the skill still works, but no linter guards it.

## Adding Knowledge

Put domain rules in `custom/KNOWLEDGE/<domain>/` and add a detection row to
`custom/KNOWLEDGE/_index.md`. Do not create a new top-level skill for a new language.
