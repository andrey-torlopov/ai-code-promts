# Home

Image of `~/.claude`. Everything here is copied into a Claude Code home directory
by `init_claude.sh`, the way `Templates/init_ai.sh` copies `Templates/Main` into a project.

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
`file-history/`, `todos/`, and any skill not shipped here, such as `skills/graphify/`
and `skills/task-lab/`.

Not copied at all: this `README.md` and `init_claude.sh`.

## Layout After Install

```text
~/.claude/
├── CLAUDE.md                 auto-loaded anchor: personal rules + pointer to custom/
├── settings.json             model, permissions, hooks
├── hooks/
│   ├── bash-guard.sh         PreToolUse: deny/ask gate for destructive shell commands
│   ├── skill-lint.sh         PostToolUse: validates instruction files
│   ├── project-context.sh    SessionStart: injects PROJECT.md when the repository has one
│   └── skill-context-lint.sh Stop: every active skill still requires SKILL CONTEXT + TRACE
├── skills/                   7 workflow skills, auto-discovered by Claude Code
└── custom/
    ├── CORE.md               SSOT for global rules
    ├── RESOLVER.md           routing table: request signal -> skill
    ├── COMMON.md             compatibility bridge
    ├── _core/                skill-context, handoff, validation, destructive-action policy
    │   └── active-skills.txt registry read by all three linters
    └── KNOWLEDGE/            lazy-loaded domain packs (swift, ios, devops, shell, python, zig)
```

## How It Gets Loaded

1. Claude Code always loads `~/.claude/CLAUDE.md`.
2. Its `# AI Runtime` section sends the agent to `~/.claude/custom/CORE.md`, then `RESOLVER.md`.
3. `RESOLVER.md` picks exactly one skill from `~/.claude/skills/`.
4. That skill loads only the `~/.claude/custom/KNOWLEDGE/` packs it names.
5. When the repository provides `PROJECT.md` (or `.claude/PROJECT.md`), the `SessionStart`
   hook injects it; without it nothing extra is read.
6. When the request carries a TaskID or points into a task folder and a `task-lab` skill is
   installed, `RESOLVER.md` also activates it as a state layer: the folder is resolved and
   restored before the subject, and the selected skill's deliverable is recorded there.
   Without that skill installed, routing is unchanged.

Nothing outside step 1 is read eagerly, so the token cost of the whole system
is one file until a task actually needs routing.

## Path Rules

- Every cross-file reference is absolute (`~/.claude/custom/...`), because the agent's
  working directory is the project, not the config directory.
- Paths inside a skill (`references/...`, `modes/...`, `scripts/...`) are relative to that
  skill's own root, stated at the top of each `SKILL.md`.

## Machine-Specific Values

`settings.json` carries deny rules with an absolute home path copied from the working
config, for example `Read(//Users/at/.ssh/**)`. On a different machine or user name those
rules match nothing. Update them after restoring on new hardware; the `Bash(...)` deny
rules and `hooks/bash-guard.sh` are path-independent and keep working either way.

## Editing

Edit here, then re-run `./init_claude.sh`. Editing `~/.claude/custom/` directly makes the
source tree stale; the installer overwrites those edits on the next run.

## Validation

```sh
sh skills/skill-maintenance/scripts/skill-lint.sh .        # this source tree
sh ~/.claude/skills/skill-maintenance/scripts/skill-lint.sh # installed system
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
