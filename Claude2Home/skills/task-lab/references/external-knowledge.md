# External knowledge base

A task may plug into a shared, long-lived knowledge base so that overlapping tasks (the
player, authorization, other large project areas) reuse one set of verified knowledge
instead of rebuilding it each time. The pointer lives in the mandatory root `env.json` of
the task folder. An empty pointer means the task has no external source and everything
below is inactive.

The task folder and the base are two different contracts:

| | Task `Knowledge/` | External base |
|---|---|---|
| Lifetime | one task | the project |
| Unit | one atomic claim per `F-NN`/`H-NN` file | one self-contained **topic** per file, free file name, ID pinned in the registry |
| Stale claims | keep; status lives in the file; never delete or move | physically delete: the file and the registry row |
| Refutations | preserved — they prevent repeated dead ends | not stored; the base holds only current knowledge |
| Cross-references | Markdown links allowed inside the task | plain-text IDs only; no Markdown links |

## env.json

Root file beside `index.md`; **every task has it**. `init_task.py` creates it with an
empty pointer; `--kb <path>` fills it.

```json
{
  "external_knowledge": ""
}
```

- `external_knowledge` — absolute path, or relative to the task-folder root; the empty
  string means no external source. One source per task. (The misspelling
  `external_knoledge` is accepted on read; always write `external_knowledge`.)

## Base layout

Flat: topic files plus a registry. File names are free; IDs are pinned by the registry.

```text
<Knowledge>/
├── README.md               registry: ID counter, fact and hypothesis tables
├── player-architecture.md  topic entries, self-contained
└── main-thread-hazards.md
```

`README.md` (skeleton: [`../templates/kb/README.md`](../templates/kb/README.md)):

```markdown
Последние выданные ID: F-12 · H-07

## Факты
| ID | Tags | Описание | Источник / срез |

## Гипотезы
| ID | Tags | Вопрос или механизм | Статус | Источник / срез |
```

Row format:

- `ID` — the permanent number, written as the link to the file:
  `[F-01](player-architecture.md)`.
- `Tags` — coarse filterable categories, comma-separated (App, SDK, Player,
  marketplace, …). Reuse existing tags before inventing one; `Player` and `player` must
  not coexist.
- `Описание` — one line of what is inside.
- `Источник / срез` — branch/revision and date; on the next line in the same cell —
  `<br>Задачи: WIBE-001, WIBE-1020` — the task-lab folders the entry was extracted from
  or that took it into work.

## Base rules

1. **IDs are base-wide, permanent, and never reused.** The next number comes from the
   counter line `Последние выданные ID`, not from the table maximum: after a deletion the
   table maximum rolls back, the counter does not. Reusing a deleted ID would silently
   repoint dated citations in old tasks at a different entry.
2. **One file — one topic, self-contained.** The header quote carries ID, Tags, the code
   slice and the sources; the body reads without access to any task folder. Another entry
   may be mentioned, but only as a plain-text ID with its substance restated in place.
   The test is **single-copy**: a file copied out of the base alone loses nothing and
   sends nobody hunting for the entry it depended on.
3. **Distilled, not dumped.** Every claim carries file/line and revision; numbers show
   numerator and denominator. Heavy tables, stacks, raw logs stay in the source tasks
   named in `Задачи:`. `_context.md` companions are forbidden — a companion breaks
   single-copy.
4. **No links into any task folder, and no Markdown links between base files.** Mentions
   are plain-text IDs; the registry is the only place resolving an ID to a file. IDs stay
   greppable, which the deletion procedure relies on.
5. **Only current knowledge.** No archive folders and no archive tables; stale entries
   are deleted by the procedure below.

## Using the base from a task

- On bootstrap and resume, when the pointer is set: read the base registry, filter by
  `Tags` relevant to the task. Search the base before opening a new `H-NN` — the
  direction may already be settled there.
- Cite base entries in durable task files as dated plain text, never as a Markdown link:
  `база F-12 (Player), снимок 2026-08-28`. The audit cannot validate external links, the
  task folder must stay portable, and the entry may be deleted later — a dated citation
  stays honest either way.
- Restate the load-bearing substance of a cited entry inline (one line), so the task's
  conclusions remain verifiable without the base.
- When a task materially uses an entry, append the TaskID to that entry's `Задачи:` list
  in the registry — inside the task this edit is covered by the open step.
- `Results/` never references the base — restate what the deliverable needs, as always.

## Export from a task

Only on an explicit user request, under an open `Step-XX` (durable artifacts change on
both sides). For each claim:

1. Pick the set: the IDs the user named, or all confirmed `F-NN` / live `H-NN` of the task.
2. Choose the target: **extend an existing topic** when the claim belongs to it — the ID
   stays, the registry row updates (срез/дата, `Задачи:` += TaskID); otherwise **create a
   new topic** with the next ID from the counter and a fresh registry row. Never duplicate
   an existing entry — extend it.
3. Carry over an **extract, not the file**: claim, evidence in one to three lines
   (command → result → revision), numbers with the derivation, scope. Restate mentioned
   entries in place; leave heavy material in the task. Skeletons:
   [`../templates/kb/F-NN-slug.md`](../templates/kb/F-NN-slug.md),
   [`../templates/kb/H-NN-slug.md`](../templates/kb/H-NN-slug.md). Final check: the
   single-copy test.
4. Update the registry (ascending IDs) and bump the counter for new IDs.
5. Mark the local side: `**Экспортировано:** F-12 → <base path>, 2026-08-28` in the file
   and the same mark in the task's `Knowledge/README.md` row.
6. Close the step result; run the task audit and the base consistency checklist below.

**After export the base copy is canonical.** The local file freezes as a historical
snapshot; refinements happen in the base — extend the topic, or supersede it with a new
entry plus deletion of the old one by the procedure below.

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

Export marks and dated citations in old tasks stay as they are: historical snapshots,
mechanically linked to nothing. Because base files are self-contained (rule 2), deleting
an entry loses no substance elsewhere — the grep exists to clean up mentions, not to
rescue content.

## Plugging in an existing base

Before first use, compare the real folder against this canon: the counter line, the
ID-linked rows, flatness. A registry still in the legacy shape
(`| Файл | Что внутри | Источник / срез |`, no IDs) is readable but not writable:
converting it — assigning permanent IDs, adding `Tags`, adding the counter — is its own
explicitly requested task; never convert silently (the same philosophy as
`unsupported-layout`).

## Base consistency checklist

After an export or a deletion, verify by hand — the audit script checks the task side
only:

- every registry row's ID link resolves to an existing file; every topic file has a row;
- every ID is ≤ the counter; the counter only grows;
- tags reuse the existing vocabulary, no case/spelling twins;
- `Задачи:` lists name real task folders;
- spot-check: a changed file passes the single-copy test.
