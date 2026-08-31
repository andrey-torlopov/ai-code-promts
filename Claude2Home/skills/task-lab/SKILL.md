---
name: task-lab
description: "Locate by TaskID, create, resume, maintain, audit, and migrate durable multi-session task folders with a single README entry point carrying a machine-readable state line, atomic facts and hypotheses, request-bound single-file Step-NN records (request → plan → done → result → knowledge footer), newest-first history, disposable inbox material, and self-contained results. Use when the user names a task such as 123 or APP-001, asks to work inside or resume its folder, or needs any task to survive context loss regardless of domain or work type."
---

# Task Lab

Keep durable task state on disk so a fresh agent can continue without rereading the whole folder
or repeating prior work. Treat the folder—not chat—as the task's system of record. One entry point
(`README.md`), one checkpoint (the latest `Steps/Step-NN.md`), one registry of claims
(`Knowledge/`).

## SKILL CONTEXT

Before substantial work, state:

```text
SKILL: task-lab (mode=<general|bug|perf|plan>)
TASK: <TaskID> → <absolute resolved task-folder path>
STATE: <new|resumed|drifted>
READ: <files actually loaded>
CURRENT: <the sole open Step-NN or "none; waiting for user request">
STOP: <deliverable boundary for this turn>
```

## Inputs

- TaskID such as `123` or `APP-001`, or an explicit task-folder path.
- User goal and concrete success condition.
- Optional internal mode: `general` by default; infer `bug`, `perf`, or `plan` only when useful.
- Subject boundaries, authoritative revision, and forbidden changes.
- Optional input materials, observations, and required result format.

Read missing values from the repository before asking the user. Ask only for choices that would
materially change the result.

## Task identity and location

The task is the folder whose basename is exactly the `TaskID`. Its parent directory has no
semantic meaning. Resolve before reading or writing:

```bash
python3 <skill>/scripts/resolve_task.py APP-001 [--workspace <search-root>]
```

1. An explicit path wins.
2. A bare TaskID is searched as an exact directory name inside the current workspace.
3. One match is the task folder; no match for an explicitly new task is created as
   `<workspace>/<TaskID>`; no match for a task described as existing requires its path.
4. Multiple matches are ambiguous: stop and request the exact path.

TaskID identifies the durable workspace; it does not classify the work. The mode changes the gates
(`references/modes.md`), never the folders.

## One structure, no profiles

```text
<TaskID>/
├── README.md       the only entry point (human + agent); carries the state line
├── env.json        external knowledge pointer; "" when the task has none
├── Knowledge/      F-NN facts and H-NN hypotheses; one claim per file + README registry
├── Steps/          Step-NN.md — one file per step: request, plan, done, result, knowledge
├── Results/        self-contained deliverables; subfolders allowed
├── tools/          task-local scripts: readers, calculators, analysers
├── Notes/          scratch prose and journals; never a source of truth
├── Logs/           raw captured output (.log/.trace/.xcresult/.csv/…); sibling of Notes/
├── Inbox/          optional disposable input; never a link target from durable artifacts
└── Archive/        appears ONLY as a v1→v2 migration artifact; audit ignores it;
                    durable files never link into it
```

Optional root files, created on need: `decisions.md` (`D-NN`, ascending registry),
`change-log.md` (`P-NN` experimental changes, newest first, with `откачено: да/нет`),
`acceptance.md` (the full acceptance bar when a metric alone is not it).

Not part of the structure — never created: `index.md`, root `steps.md`, `Context/` (the v1 layout:
its folders are refused by the scripts with a `migrate_task.py` hint), `Process/`,
`Steps/_next.md`, `timeline.md`, `Steps/README.md`, root `Tools/`, root `Traces/`, a separate
`Hypotheses/`, and `Logs/` nested inside any other folder. A folder built on another shape is not
silently read and not silently migrated: the scripts stop and say so. Migration v1→v2 is its own
explicitly requested run of `migrate_task.py`.

## README contract

`README.md` is the single entry point and the only synchronized projection. Its first body line is
the machine-readable state line — the sole pointer to the current step:

```text
**Состояние:** шаг 05 открыт · 2026-08-31
**Состояние:** открытого шага нет · ждём запрос пользователя · 2026-08-31
```

Required sections, in order: mini-table (Режим/Фаза/Блокер/Результаты) · «Задача» (one paragraph;
the full statement lives in `Knowledge/F-01`, the subject slice in `Knowledge/F-02`) · «Правила
задачи» (INV-NN with reasons) · «Проверить при возобновлении» (drift table; the observed drift
record goes to `Notes/`) · «Шаги» (completed history, newest first; the open step is named only in
the state line) · «Рекомендуемая очередность» (numbered self-contained items + «Вопросы к вам»;
no internal ids — a question whose answer is durable becomes a fact) · «Не предлагать повторно» ·
«Устройство папки и порядок чтения».

## Step contract — one file per step

**A request that changes a durable artifact opens a step. Always — a one-line edit included. A
request whose whole output is the reply does not.**

| The user asks for | Step? |
|---|---|
| any edit to `Results/`, `Knowledge/`, `Steps/`, `README.md`, root files | **yes** |
| any edit to code or documents outside the task folder | **yes** |
| a fix so small it feels like a typo | **yes** — a small request is a small step, not no step |
| an explanation, a location, a quote, reading the subject, audit/restore runs | no |

Exactly two edits are exempt, and no others: scratch dropped into `Notes/` and raw output captured
into `Logs/` (the on-resume drift record is scratch in `Notes/`).

Lifecycle of `Steps/Step-NN.md` (`NN` = `max(existing) + 1`, zero-padded):

1. **Open** — on the user's request, before touching any durable file, create the file from
   `templates/items/standard/Step-NN.md` with status `выполняется` and sections «Запрос» and
   «План» (границы, действия, **критерий завершения — фиксируется до выполнения**, otherwise the
   criterion gets fitted to the numbers). Update the README state line. «Запрос» and «План» are
   frozen once execution starts: a materially changed request closes the step as `отменён` and
   opens the next one.
2. **Close** — set status `завершён`, `отменён`, or `заблокирован` (all three are honest) and
   append three sections: «Что сделано» (actual actions, including deviations from the plan),
   «Результат» (first line `**Вердикт:** …`; evidence and scope, changed artifacts, what was NOT
   done, limits and debts), «Задействованные знания» (table `| ID | Роль в шаге |` naming every
   F-NN/H-NN the step used, checked, refuted, or created; `нет` is a valid single row).
3. **Synchronize README in the same turn**: state line, first row of «Шаги», re-ranked
   «Рекомендуемая очередность». Update `Knowledge/` (new/changed claims, «Шаги» column).
4. Run audit and restore.

The open step is mechanically defined: status `выполняется` and no `## Результат` heading. At most
one step is open, and its number is the highest. Never pre-create a future step.

Load [`references/steps.md`](references/steps.md) before opening or closing a step.

## Entity laws

1. One claim per file: `F-NN-*` is verified; `H-NN-*` is unverified.
2. A fact has evidence and scope. Without evidence it is a hypothesis.
3. A hypothesis has a falsifiable expected outcome and a predeclared gate.
4. Numbers show numerator, denominator, result, units, and scope.
5. Heavy details move to `<entity>_context.md`; the main file stays skimmable.
6. Supersede durable claims explicitly; never silently rewrite history into agreement.
7. Refuted work remains discoverable (`Knowledge/README.md`, «Опровергнуто») because it prevents
   repeated dead ends; README keeps the one-line «Не предлагать повторно» projection.

Load [`references/entities.md`](references/entities.md) before creating or changing an entity.
Load [`references/gates.md`](references/gates.md) before defining a measurement or acceptance gate.

## Inbox, notes, logs, and results boundary

`Inbox/` is staging, `Notes/` is scratch prose, `Logs/` is raw machine output — none is a source
of truth, and durable files never link into `Inbox/` or `Archive/` (a link into `Notes/`/`Logs/`
warns: extract the claim into `Knowledge/`, quote the line, do not link the file). `Results/` is
an export boundary: it must stand alone without Knowledge IDs, task-local paths, or chat context.
Delete `Inbox/` only with user authorization, after the audit confirms no dependency.

## External knowledge base

Every task carries a root `env.json` — `{"external_knowledge": "<path>"}`; an empty string means
none. The base is a flat set of self-contained topic files plus a `README.md` registry with
permanent IDs. Search it before opening a new hypothesis; cite entries in durable task files as
dated plain text (`база F-12 (Player), снимок 2026-08-28`), never as Markdown links. Export into
the base and deletion from it happen only on an explicit user request, under an open step. Load
[`references/external-knowledge.md`](references/external-knowledge.md) before reading, exporting,
or deleting.

## Workflow

New task: load [`references/lifecycle.md`](references/lifecycle.md), read the subject first, then

```bash
python3 <skill>/scripts/init_task.py --id APP-001 \
  [--workspace <root>] [--title "..."] [--mode general] [--with-inbox] [--kb <path>]
```

Replace every `{{FILL_*}}` marker (a scaffold with markers is intentionally invalid), convert
verified premises into facts, run audit and restore. The initializer does not invent a step: if
the same request carries substantive work, open `Step-01.md` after the base context is ready.

Existing task: run `restore_task.py`, perform the README drift check, continue the open step —
never restart or propose an eliminated direction. Persist durable findings before replying.

## Scripts

```bash
python3 <skill>/scripts/init_task.py --help
python3 <skill>/scripts/resolve_task.py <TaskID-or-path> [--workspace <root>]
python3 <skill>/scripts/restore_task.py <TaskID-or-path> [--workspace <root>] [--section step]
python3 <skill>/scripts/audit_task.py <TaskID-or-path> [--workspace <root>] [--pedantic]
python3 <skill>/scripts/migrate_task.py <TaskID-or-path> [--workspace <root>] [--dry-run]
python3 <skill>/scripts/self_test.py
```

- `resolve_task.py` resolves an explicit path or one exact TaskID match and rejects ambiguity.
- `init_task.py` scaffolds the v2 structure; refuses to overlay v1 (`index.md`, `steps.md`,
  `Context/`) and foreign shapes.
- `restore_task.py` emits a bounded brief (state, invariants, open step or checkpoint verdict,
  history, entities, external base, queue); refuses v1 and foreign shapes instead of half-reading.
- `audit_task.py` checks structure, the state line against the actual open step, step sections and
  statuses, the knowledge footer against `Knowledge/`, README history coverage and order, entity
  evidence, links and boundaries, placement, registries and journals, and durable files edited
  while no step was open (`edit-outside-step`, a warning based on mtimes — a question, not a
  verdict).
- `migrate_task.py` converts a v1 folder (explicit request only): merges step pairs into single
  files, composes the v2 README, relocates `Context/` content, moves originals to `Archive/v1/`,
  and reports links that need manual review.
- `self_test.py` verifies the scaffold set, state-line checks, step lifecycle, footer checks,
  boundary guards, kb wiring, refusals, and migration end to end.

## Local References

| File | Load when |
|---|---|
| `references/lifecycle.md` | creating, resuming, or closing a task; recovery budget; step-close checklist |
| `references/steps.md` | opening or closing a step |
| `references/entities.md` | facts, hypotheses, decisions, invariants |
| `references/gates.md` | falsifiable checks and noise |
| `references/writing-rules.md` | journals, registries, numbers, links |
| `references/modes.md` | optional general/bug/perf/plan gate specializations |
| `references/external-knowledge.md` | env.json, external base, export, deletion |

## Output

Return changed task artifacts plus a concise report containing the current state, the executed
request, files changed, audit/restore results, and remaining uncertainty. The folder must contain
every durable fact from the reply.

## Stop Conditions

- Do not scaffold a task that fits in one short session unless the user explicitly requests a
  folder; say why instead.
- Do not assume a parent folder from TaskID, and do not choose silently between duplicate TaskIDs.
- Do not act before the README drift check on an existing folder.
- Do not invent structure, and do not silently migrate a v1 or foreign folder — migration is its
  own explicitly requested `migrate_task.py` run.
- Do not create a step before a concrete user request, create a second open step, or pre-number
  future work; do not edit «Запрос»/«План» after execution starts.
- Do not change a durable artifact while no step is open — and do not open a step for a question
  that the reply itself answers.
- Do not leave a step without its «Результат» block; blocked and cancelled are valid verdicts.
- Do not cite or depend on `Inbox/` or `Archive/` from durable artifacts.
- Do not delete inbox material without the user's authorization, even when the audit is clean.
- Do not claim a clean state while audit fails or restore prints the wrong next action.
- Do not export task knowledge into an external base, and do not delete base entries, without an
  explicit user request; name every deletion (ID and file) before executing it.

## TRACE

```text
TRACE:
- Skill: task-lab (mode) plus the routed deliverable owner when one was used
- Task folder: <absolute path>
- Patterns/policies applied: <state line, step contract, entity laws, gates, boundary rules>
- Verification: <audit_task.py and restore_task.py results>
- Residual risk: <open H-NN, drift, unverified claims>
```
