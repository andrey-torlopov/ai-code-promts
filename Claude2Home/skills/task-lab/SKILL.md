---
name: task-lab
description: "Locate by TaskID, create, resume, maintain, and audit durable multi-session task folders with agent context, atomic facts and hypotheses, request-bound Step-XX plans and Step-XX-result outcomes, newest-first history, disposable inbox material, and self-contained results. Use when the user names a task such as 123 or APP-001, asks to work inside or resume its folder, or needs any task to survive context loss regardless of domain or work type."
---

# Task Lab

Keep durable task state on disk so a fresh agent can continue without rereading the whole folder
or repeating prior work. Treat the folder—not chat—as the task's system of record.

## SKILL CONTEXT

Before substantial work, state:

```text
SKILL: task-lab (mode=<general|bug|perf|plan>)
TASK: <TaskID> → <absolute resolved task-folder path>
STATE: <new|resumed|drifted>
READ: <files actually loaded>
CURRENT: <the sole open Step-XX or "none; waiting for user request">
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
semantic meaning and does not need a conventional name.

Resolve before reading or writing:

```bash
python3 <skill>/scripts/resolve_task.py APP-001 [--workspace <search-root>]
```

1. An explicit path wins.
2. A bare TaskID is searched as an exact directory name inside the current workspace.
3. One match is the task folder; do all task-state work inside it.
4. No match is created as `<workspace>/<TaskID>` only when the user is creating a new task.
5. No match for a task described as existing requires its path or search root; do not invent one.
6. Multiple matches are ambiguous: stop and request the exact path.

TaskID identifies the durable workspace; it does not classify the work. Feature development,
defect analysis, RND, research, planning, content localization, operations, and other multi-session
work use the same Context/Knowledge/Steps/Results contract.

## One structure, no profiles

There is exactly one task-folder shape, and every task uses it: feature work, defect analysis, RND,
research, planning, localization, operations, and measurement-heavy work alike. The mode changes the
gates, never the folders.

```text
<TaskID>/
├── README.md       human entry: status and navigation
├── index.md        agent entry: read order, hard rules, compact state
├── steps.md        newest-first completed-step history plus current pointer
├── env.json        external knowledge pointer; "" when the task has none
├── Context/        agent-only context
│   ├── 00-START-HERE.md        goal, boundaries, invariants, current phase
│   ├── 10-repo-and-revisions.md  authoritative subject, revisions, check commands
│   ├── 20-code-map.md          where to go for what
│   ├── 30-method.md            what counts as a fact, a finding, an acceptance
│   ├── 40-queue.md             unnumbered candidates and blocking questions
│   ├── 90-session-restore.md   read order and drift check
│   └── tools/                  task-local scripts: readers, calculators, analysers
├── Knowledge/      F-NN facts and H-NN hypotheses; one claim per file + README registry
├── Steps/          Step-XX.md is a request plan; Step-XX-result.md closes it
├── Results/        self-contained deliverables; subfolders allowed
├── Notes/          scratch prose: pasted briefs and observation journals; never a source of truth
├── Logs/           raw captured output: logs, traces, profiles, measurement dumps
└── Inbox/          optional disposable input; never a link target from durable artifacts
```

`Logs/` sits at the root, beside `Notes/` — it is never nested inside another folder. Machine-made
output (`.log`, `.trace`, `.logarchive`, `.xcresult`, `.csv`, `.har`, `.nettrace`) goes to `Logs/`;
the hand-written journal that interprets it stays in `Notes/runs.md`. Both are disposable and
neither is a source of truth.

`Process/`, `Steps/_next.md`, `timeline.md`, `Steps/README.md`, root `Tools/`, root `Traces/`, and a
separate `Hypotheses/` are not part of this structure and are never created. Put experimental change
tracking in `Context/change-log.md`, acceptance criteria in
`Context/verification-and-acceptance.md`, observation journals in `Notes/`, raw captured output in
`Logs/`, and every calculation script in `Context/tools/`.

A folder built on another shape is not silently read and not silently migrated: the scripts stop and
say so. Converting one is a separate, explicitly requested task, because it rewrites history and
every entry point.

Load [`references/layouts.md`](references/layouts.md) when deciding where an artifact belongs. Load
[`references/modes.md`](references/modes.md) when the mode or acceptance rule is unclear.

## Projection contract

The same state appears in several projections for different readers. Keep them consistent:

- an open step is the only `Step-XX.md` without a matching `Step-XX-result.md`;
- when a step is open, `index.md`, `README.md`, and `steps.md` name the same step;
- when no step is open, those projections say that the next user request will create it;
- `steps.md` lists completed steps by descending number: latest first;
- `Context/90-session-restore.md` carries the current drift assumptions;
- `Knowledge/README.md` matches the entity files and their statuses;
- `Results/` is usable after the task folder is gone: no links to `Knowledge/`, `Steps/`,
  `Context/`, `Notes/`, `Logs/`, or `Inbox/`.

The state claim lives in the state block of each projection (`## Состояние` / `## Текущий шаг`);
prose that merely explains the waiting rule is not a status claim and is not kept in sync.

## Entity laws

1. One claim per file: `F-NN-*` is verified; `H-NN-*` is unverified.
2. A fact has evidence and scope. Without evidence it is a hypothesis.
3. A hypothesis has a falsifiable expected outcome and a predeclared gate.
4. Numbers show numerator, denominator, result, units, and scope.
5. Heavy details move to `<entity>_context.md`; the main file stays skimmable.
6. Supersede durable claims explicitly; never silently rewrite history into agreement.
7. Refuted work remains discoverable because it prevents repeated dead ends.

Load [`references/entities.md`](references/entities.md) before creating or changing an entity.
Load [`references/gates.md`](references/gates.md) before defining a measurement or acceptance gate.

## Inbox, notes, logs, and results boundary

`Inbox/` is staging, not evidence. Extract each durable claim into `Knowledge/` and cite the real
subject, command, log, or revision there. Do not create Markdown links from `Knowledge/`, `Steps/`,
`Context/`, or `Results/` into `Inbox/`. Before removing inbox material, run the audit and verify
that no durable file depends on it.

`Notes/` is scratch produced during the work — a pasted brief, an observation journal, a working
sketch. It is disposable for the same reason: durable claims are extracted into `Knowledge/`, and a
durable file that depends on a note is a finding, not a design.

`Logs/` is the raw output the work captured — a command log, a profiler trace, an exported table.
It is a sibling of `Notes/`, not a subfolder of it and not of anything else, and it is disposable
under the same rule: a durable file that depends on a log means the number or the line it needs was
never extracted into `Knowledge/`. Cite the log's content as evidence in the fact; do not link the
file.

`Results/` is an export boundary. Repeat enough context inside the result for it to stand alone.
Internal IDs may appear as provenance text only when the user wants them; they must not be required
to understand or execute the deliverable.

## External knowledge base

Every task carries a root `env.json` — `{"external_knowledge": "<path>"}` — pointing at a
shared, long-lived knowledge base; an empty string means none. The base is a flat set of
self-contained topic files (free names, permanent IDs pinned in the registry) plus a
`README.md` registry: `ID | Tags | Problem | Описание | Источник / срез` for facts
(hypotheses drop the Problem column), with the task folders that touched the entry listed
as `Задачи:` in the source cell. The base stores only
current knowledge: stale entries are physically deleted, not archived. Search it before
opening a new hypothesis; cite entries in durable task files as dated plain text
(`база F-12 (Player), снимок 2026-08-28`), never as Markdown links. Export into the base
and deletion from it happen only on an explicit user request, under an open step, with
deletions named (ID and file) before execution.

Load [`references/external-knowledge.md`](references/external-knowledge.md) before
reading the base, exporting into it, or deleting from it.

## Workflow

### New task

1. Load [`references/bootstrap.md`](references/bootstrap.md).
2. Read the subject before scaffolding; convert verified premises into facts and unknowns into
   hypotheses or questions.
3. Scaffold the canonical structure:

   ```bash
   python3 <skill>/scripts/init_task.py --id APP-001 \
     [--workspace <root>] [--title "..."] [--mode general] [--with-inbox] [--kb <path>]
   ```

4. Replace every generated `{{FILL_*}}` marker. A scaffold with markers is intentionally invalid.
5. The initializer does not invent a step. If the current user request includes substantive work
   beyond creating the folder, open `Step-01.md` after the base context is ready and before doing
   that work; otherwise wait for a later concrete request.
6. Run audit and restore before declaring the folder ready; both must accept the no-open-step state.

For new entities and step plan/result files, copy the matching skeleton from
`templates/items/standard/`.

### Existing task

1. Load [`references/resume.md`](references/resume.md).
2. Run the bounded brief before opening files:

   ```bash
   python3 <skill>/scripts/restore_task.py APP-001 [--workspace <search-root>]
   ```

3. Perform the drift check in `Context/90-session-restore.md`.
4. Continue the current step. Do not restart the task or propose a direction already eliminated.
5. Persist durable findings before replying.

### Step or no step

**A request that changes a durable artifact opens a step. Always — a one-line edit included. A
request whose whole output is the reply does not.**

| The user asks for | Step? |
|---|---|
| any edit to `Results/`, `Knowledge/`, `Context/`, `Steps/`, `README.md`, `index.md`, `steps.md` | **yes** |
| any edit to code or documents outside the task folder | **yes** |
| a fix so small it feels like a typo | **yes** — a small request is a small pair, not no pair |
| an explanation of what was already done, or why | no |
| where something lives, what a file says, what a number means | no |
| reading the subject, running audit/restore, searching | no |

Exactly three edits are exempt, and no others: scratch dropped into `Notes/`, raw output captured
into `Logs/`, and the drift record written into `Context/90-session-restore.md` when a session
resumes.

The rule starts once the folder exists. Scaffolding it and filling the base context is the
folder-creation request itself, not a step; `Step-01.md` opens when that same request also carries
substantive work.

Consequences worth stating, because they are the cases that get fudged:

- A question that turns into an edit inside the same turn — the user reads the answer and says
  "fix it" — is a request: create `Step-XX.md` first, then edit. The explaining part stays outside
  the step.
- If an answer produces something worth keeping in the folder, keeping it *is* the edit, so it
  needs its own step. An unrecorded finding and a finding recorded without a step are both defects.
- Two user requests are two steps, even when the second arrives while the first is still open:
  close the current pair, then open the next.

### Execute one user request

1. On the user's request, choose `max(existing step numbers) + 1`, zero-pad it (`01`, `02`, …),
   and create `Steps/Step-XX.md` before
   touching any durable file. Record the user's request, scope, actions, and completion criterion.
2. Execute that step. Do not pre-create a later step.
3. When execution ends, create `Steps/Step-XX-result.md`; start with the verdict and record
   evidence, changed artifacts, limits, and debts. A cancelled or blocked execution still gets a
   result file with that honest status.
4. Add or update facts, hypotheses, decisions, questions, and exported results.
5. Insert the completed step as the first row of the completed table in root `steps.md`; never
   append it below older steps.
6. Leave no planned future step. Synchronize `README.md`, `index.md`, `steps.md`, and
   `Context/90-session-restore.md` in the same turn.
7. Run audit and restore.

Load [`references/steps.md`](references/steps.md) for step anatomy and
[`references/maintenance.md`](references/maintenance.md) for close/resume consistency.

## Scripts

```bash
python3 <skill>/scripts/init_task.py --help
python3 <skill>/scripts/resolve_task.py <TaskID-or-path> [--workspace <root>]
python3 <skill>/scripts/restore_task.py <TaskID-or-path> [--workspace <root>] [--section step]
python3 <skill>/scripts/audit_task.py <TaskID-or-path> [--workspace <root>] [--pedantic]
python3 <skill>/scripts/self_test.py
```

- `resolve_task.py` resolves an explicit path or one exact TaskID match and rejects ambiguity.
- `init_task.py` needs only TaskID, defaults to the current workspace and `general`, and creates the
  same structure for every mode: root `Steps/` and `steps.md`, `Notes/`, root `Logs/`,
  `Context/tools/`, and no `Process/`, `Tools/`, or `Traces/`. Root `env.json` is always
  created with an empty pointer; `--kb <path>` fills `external_knowledge` with the base path.
- `restore_task.py` resolves TaskID, emits a bounded brief, and refuses a folder built on another
  shape instead of half-reading it.
- `audit_task.py` resolves TaskID and checks structure, entry-point agreement, entity evidence,
  broken links, inbox/notes/logs isolation, result self-containment, unresolved template markers,
  registry order, artifact placement, and durable files edited while no step was open
  (`edit-outside-step`, a warning: it reads modification times, so a checkout or a copy can move
  them — treat it as a question, not a verdict).
- `self_test.py` verifies numeric and prefixed TaskIDs, ambiguous-ID rejection, the exact scaffold
  file set, mode-independence of the structure, request-bound plan/result pairs, `Context/tools/`
  and root-`Logs/` placement, the edit-outside-step warning and its three exemptions, refusal of
  non-canonical folders, descending history, and Inbox/Results boundary guards.

## Local References

| File | Load when |
|---|---|
| `references/layouts.md` | folder topology, artifact placement, Inbox/Notes/Logs/Results rules |
| `references/bootstrap.md` | creating a task |
| `references/resume.md` | resuming a task |
| `references/context-recovery.md` | recovery budget and projection consistency |
| `references/entities.md` | facts, hypotheses, decisions, questions |
| `references/gates.md` | falsifiable checks and noise |
| `references/steps.md` | opening or closing a step |
| `references/writing-rules.md` | journals, registries, numbers, links, audience split |
| `references/modes.md` | optional general/bug/perf/plan gate specializations |
| `references/maintenance.md` | drift, debts, audit, task close |
| `references/external-knowledge.md` | env.md, external base, export, deletion |

## Output

Return changed task artifacts plus a concise report containing the current state, the executed
request, files changed, audit/restore results, and remaining uncertainty. The folder must contain
every durable fact from the reply.

## Stop Conditions

- Do not scaffold a task that fits in one short session unless the user explicitly requests a
  folder; say why instead.
- Do not assume a parent folder from TaskID, and do not choose silently between duplicate TaskIDs.
- Do not act before drift-checking an existing folder.
- Do not invent structure: no folder outside the canonical set, and no silent migration of a folder
  built on another shape.
- Do not create a step before a concrete user request, create a second open step, or pre-number future work.
- Do not change a durable artifact while no step is open — and do not open a step for a question
  that the reply itself answers.
- Do not finish execution without a matching `Step-XX-result.md`; blocked and cancelled are valid results.
- Do not cite or depend on `Inbox/` from durable artifacts.
- Do not delete inbox material merely because the audit is clean; deletion still requires the
  user's authorization.
- Do not change the subject outside the current step or hiddenly broaden the requested scope.
- Do not claim a clean state while audit fails or restore prints the wrong next action.
- Do not export task knowledge into an external base, and do not delete base entries,
  without an explicit user request; name every deletion (ID and file) before executing it.

## TRACE

```text
TRACE:
- Skill: task-lab (mode) plus the routed deliverable owner when one was used
- Task folder: <absolute path>
- Patterns/policies applied: <projection contract, entity laws, gates, boundary rules>
- Verification: <audit_task.py and restore_task.py results>
- Residual risk: <open H-NN, drift, unverified claims>
```
