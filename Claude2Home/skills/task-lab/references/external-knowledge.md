# External knowledge base

A task may plug into a shared, long-lived knowledge base so that overlapping tasks (the
player, authorization, other large project areas) reuse one set of verified facts instead
of rebuilding it each time. The base is named by an optional root `env.md` in the task
folder. Without `env.md` nothing below applies and the skill behaves exactly as before.

The task folder and the base are two different contracts:

| | Task `Knowledge/` | External base |
|---|---|---|
| Lifetime | one task | the project |
| Stale claims | keep; status lives in the file; never delete or move | physically delete: the file and the registry row |
| Refutations | preserved — they prevent repeated dead ends | not stored; the base holds only current knowledge |
| Cross-references | Markdown links allowed inside the task | plain-text IDs only; no Markdown links |
| Category column | none | mandatory |

## env.md

Root file beside `index.md`. Optional; `init_task.py --kb <path>` creates it.

```markdown
# env — внешнее окружение задачи

## Источники знаний

| Тип | Путь | Категории задачи |
|---|---|---|
| knowledge | /Volumes/DATA-R1/Dev/MyApp/Knowledge | player, auth |
```

- `Путь` — absolute, or relative to the task-folder root.
- `Категории задачи` — which base categories are relevant to this task; they are also the
  default categories on export. `—` means no filter: the whole base is relevant.
- Several source rows are allowed; the common case is one.

## Base layout

Flat. No `Archive/`, no subfolders, no `_context.md` companions.

```text
<Knowledge>/
├── README.md        registry: ID counter, category dictionary, fact and hypothesis tables
├── F-NN-*.md        current verified facts
└── H-NN-*.md        current hypotheses
```

`README.md` shape (see [`../templates/kb/README.md`](../templates/kb/README.md)):

```markdown
# Knowledge — реестр фактов и гипотез

Последние выданные ID: F-12 · H-07

## Категории
| Категория | Что покрывает |

## Факты
| ID | Категория | Утверждение | Тяжесть | Файл |

## Гипотезы
| ID | Категория | Вопрос или механизм | Статус | Чем закрывается | Файл |
```

## Base rules

1. **IDs are base-wide and never reused.** The next number comes from the counter line
   `Последние выданные ID`, not from the table maximum: after a deletion the table maximum
   rolls back, the counter does not. Reusing a deleted ID would silently repoint dated
   citations in old tasks at a different claim.
2. **The category is mandatory** and comes from the `## Категории` dictionary. A new
   category is an explicit new dictionary row, never an ad-hoc spelling (`Player`,
   `player` and `плеер` must not coexist).
3. **Atomic and self-contained.** One file — one claim, and everything needed to
   understand and verify it is inside the file: evidence (command, observation,
   `file:line` at a revision), numbers with their derivation, scope. Another entry may be
   mentioned, but only as a plain-text ID with its substance restated in place
   («опирается на F-07: плеер держит единственный экземпляр AVPlayer»). The test is
   **single-copy**: a file copied out of the base alone loses nothing and sends nobody
   hunting for the F-XX it depended on.
4. **Compact.** A file is an extract, not a dossier; aim for at most ~40 lines. Heavy
   tables, stacks, diffs and full logs stay in the source task named by the
   `Происхождение` block. `_context.md` companions are forbidden in the base — a
   companion breaks single-copy.
5. **No Markdown links between base files.** Mentions are plain-text IDs; the registry is
   the only place that resolves an ID to a file path. IDs stay greppable, which the
   deletion procedure relies on.
6. **Only current knowledge.** No archive folders and no archive tables; stale entries
   are deleted by the procedure below.

## Using the base from a task

- On bootstrap and resume, when `env.md` exists: read the base registry filtered by the
  task categories. Search the base before opening a new `H-NN` — the direction may
  already be settled there.
- Cite base entries in durable task files as dated plain text, never as a Markdown link:
  `база F-12 (player), снимок 2026-08-28`. The audit cannot validate external links, the
  task folder must stay portable, and the entry may be deleted later — a dated citation
  stays honest either way.
- Restate the load-bearing substance of a cited entry inline (one line), so the task's
  conclusions remain verifiable if the base entry is later deleted.
- `Results/` never references the base — restate what the deliverable needs, as always.

## Export from a task

Only on an explicit user request, under an open `Step-XX` (durable artifacts change on
both sides). For each claim:

1. Pick the set: the IDs the user named, or all confirmed `F-NN` / live `H-NN` of the task.
2. Deduplicate against the base (registry + category): a match by substance is not
   copied — the local file gets the mark «уже в базе как F-07» instead.
3. Assign the next ID from the counter and a category from the dictionary (default: the
   task categories in `env.md`).
4. Carry over an **extract, not the file**: claim, evidence in one to three lines
   (command → result → revision), numbers with the derivation, scope, consequence.
   Restate mentioned entries in place; leave heavy material in the task — the
   `Происхождение` block names it. Final check: the single-copy test and the size
   guideline (rules 3–4). Use [`../templates/kb/F-NN-slug.md`](../templates/kb/F-NN-slug.md)
   and [`../templates/kb/H-NN-slug.md`](../templates/kb/H-NN-slug.md) as skeletons.
5. Append the registry row (ascending ID) and bump the counter.
6. Mark the local side: `**Экспортировано:** F-12 → <base path>, 2026-08-28` in the file
   and the same mark in the task's `Knowledge/README.md` row.
7. Close the step result; run the task audit and the base consistency checklist below.

**After export the base copy is canonical.** The local file freezes as a historical
snapshot; refinements happen in the base — a new entry with a new ID plus deletion of the
superseded one by the procedure below.

## Deletion from the base

Deletion is destructive and irreversible on disk; the base's git history, when the base
lives in a repository, is the only trace. The gate is CORE rule 5 (Delete Carefully):

1. **Name what will be deleted before doing it** — IDs, files, reason. If the deletion
   was not itself the explicit user request (for example a supersede during export), wait
   for confirmation first.
2. Grep the base for the IDs being deleted. Fix or drop every mention found (restate, or
   repoint at the successor entry) before deleting.
3. Delete the file; delete the registry row.
4. Do not touch the counter — it never rolls back.
5. Inside a task the operation is covered by the open step, and the step result lists
   what was deleted; outside a task the explicit request is enough.

Export marks in old tasks («Экспортировано: F-12 …») stay as they are: dated historical
snapshots, mechanically linked to nothing. Because base files are self-contained
(rule 3), deleting an entry loses no substance elsewhere — the grep exists to clean up
mentions, not to rescue content.

## Plugging in an existing base

Before first use, compare the real folder against this canon: the counter line, the
dictionary, the table columns, flatness. On mismatch, say so and offer the adaptation as
its own explicitly requested task — never silently migrate or half-read it (the same
philosophy as `unsupported-layout`).

## Base consistency checklist

After an export or a deletion, verify by hand — the audit script checks the task side
only:

- every registry row points at an existing file; every `F-*`/`H-*` file has a row;
- every ID is ≤ the counter; the counter only grows;
- no file mentions an ID that no longer exists in the registry;
- every category used in the tables exists in the dictionary;
- spot-check: a changed file passes the single-copy test and the ~40-line guideline.
