# Layout

## One structure for every task

Feature work, defect analysis, RND, research, planning, localization, operations and
measurement-heavy work use the same folders. The mode changes the gates and the acceptance bar, not
the topology. There are no profiles and no per-domain variants: a second shape means a second set of
rules that nobody remembers.

```text
<TASK_ID>/
├── README.md
├── index.md
├── steps.md
├── env.json             external knowledge pointer; "" when none (external-knowledge.md)
├── Context/
│   ├── 00-START-HERE.md
│   ├── 10-repo-and-revisions.md
│   ├── 20-code-map.md
│   ├── 30-method.md
│   ├── 40-queue.md
│   ├── 90-session-restore.md
│   └── tools/               task-local scripts: readers, calculators, analysers
├── Knowledge/
│   ├── README.md
│   ├── F-NN-*.md
│   └── H-NN-*.md
├── Steps/
│   ├── Step-XX.md
│   └── Step-XX-result.md
├── Results/
│   └── README.md            subfolders allowed for sets of like deliverables
├── Notes/                   scratch prose and journals; not a source of truth
├── Logs/                    raw captured output; sibling of Notes/, never nested in it
└── Inbox/                   optional disposable input
```

The initial `Steps/` directory is empty. A user request creates the next `Step-XX.md`; finishing,
cancelling, or blocking its execution creates the matching result. No unmatched plan means the
task is waiting for a user request, not that its structure is broken.

## Not part of the structure

| Never create | Where it goes instead |
|---|---|
| `Process/`, `Process/steps/` | `Steps/` with `Step-XX.md` + `Step-XX-result.md` |
| `Steps/_next.md`, `Steps/README.md` | root `steps.md` holds the pointer and the history |
| `timeline.md` | root `steps.md` |
| root `Tools/` | `Context/tools/` |
| root `Traces/` | root `Logs/` for the raw output, `Notes/` for the journal that reads it |
| `Notes/Logs/`, `Logs/` under any other folder | root `Logs/`, a sibling of `Notes/` |
| `Hypotheses/`, `Knowledge/Closed/`, `Archive/` | `Knowledge/` with an explicit status in the file |

The no-archive rule governs the task folder. An external knowledge base named by root
`env.json` is a different contract ([`external-knowledge.md`](external-knowledge.md)): a
flat curated set of current entries where stale records are physically deleted on an
explicit user request — no `Archive/` there either, and never a silent deletion.

A folder that already has one of these shapes is not read as if it were canonical and not migrated
in passing: `audit_task.py` reports `unsupported-layout`, `restore_task.py` refuses, and
`init_task.py` will not overlay it. Converting such a folder is a separate, explicitly requested
task, because it rewrites the history and every entry point.

## Additional context files

Add a narrowly required file when the work needs it, without changing the step contract:

- `Context/change-log.md` — experimental changes to the subject, with `откачено: да/нет`;
- `Context/verification-and-acceptance.md` — the full acceptance bar when a metric alone is not it;
- `Context/decisions.md` — `D-NN` decisions when the queue registry stops being enough;
- `Notes/runs.md` — the observation journal, newest first.

## Audience boundary

- Human route: `README.md` → `steps.md` → one plan/result pair or `Results/`.
- Agent route: `index.md` → `Context/00-START-HERE.md` → `steps.md` → the unmatched plan, if any.
- `steps.md` is a compact newest-first history, the current pointer, and a short
  recommended-order block for the user — not the detailed plan or log.
- The recommended-order block is a numbered list (never a table), each item a
  self-contained one-liner the user can turn into the next request. No `Q-NN`, no links
  into `Context/`: the full queue with its ranking stays in `Context/40-queue.md`.

## Inbox, Notes and Logs boundary

`Inbox/` may contain stale, duplicated, or contradictory input and is allowed to disappear.
`Notes/` holds scratch produced while working — a pasted brief, a working sketch, an observation
journal — and is disposable for the same reason. `Logs/` holds the raw output that work captured:
`.log`, `.trace`, `.logarchive`, `.xcresult`, `.csv`, `.har`, `.nettrace`, command dumps.

`Logs/` and `Notes/` are two root folders at the same level. Neither contains the other: a raw
`.log` in `Notes/` is reported as `observation-misplaced`, and a hand-written journal belongs in
`Notes/runs.md` even when it summarises files in `Logs/`. The split is by producer — machine output
against human prose — not by topic.

Read any of the three only to discover candidate claims, recheck them against the real subject,
write durable claims and evidence into `Knowledge/`, and never link into `Inbox/` from a durable
artifact. A durable file linking into `Notes/` or `Logs/` is a warning: the material has outlived
its scratch status and its claim belongs in `Knowledge/`, quoted rather than linked. Delete
`Inbox/` only with user authorization, after the audit confirms no dependency.

## Results boundary

Treat `Results/` as an export that may be copied alone. It must not require Knowledge IDs,
task-local relative paths outside `Results/`, Inbox drafts, notes, logs, or chat context. Duplicate the
minimum necessary explanation inside the result.

## Projection consistency

These four projections must agree:

1. the unmatched `Steps/Step-XX.md`, if any — authority for current execution;
2. `steps.md` — current pointer, descending completed history, recommended-order block;
3. `index.md` — agent projection;
4. `README.md` — human projection.

The claim is the state block of each file (`## Состояние`, `## Текущий шаг`); prose explaining the
waiting rule elsewhere in the file is not a status claim. When a result is created, prepend its row
to `steps.md`, then set all state blocks to “no open step; waiting for user request”. `Results/`
status in README must agree with actual result payloads. Run audit and restore after synchronization.
